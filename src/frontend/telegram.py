# telegram_bot.py
import os
import logging
from typing import Dict
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from ollama_client import OllamaClient

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, ollama_client: OllamaClient, token: str):
        self.ollama = ollama_client
        self.token = token
        self.application = Application.builder().token(self.token).build()
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("list_models", self.list_models))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message when user starts the bot"""
        user = update.effective_user
        welcome_msg = (
            f"Hi {user.mention_html()}! I'm an AI assistant powered by Ollama.\n\n"
            "You can:\n"
            "- Ask me anything\n"
            "- Use /list_models to see available models\n"
            "- Use /help for assistance"
        )
        await update.message.reply_html(welcome_msg)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show help message"""
        help_text = (
            "🦙 Ollama Bot Help 🦙\n\n"
            "Available commands:\n"
            "/start - Start conversation\n"
            "/help - Show this help message\n"
            "/list_models - Show available AI models\n\n"
            "Just type your message to chat with the AI!"
        )
        await update.message.reply_text(help_text)

    async def list_models(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List available Ollama models"""
        try:
            models = self.ollama.list_models()
            model_list = "\n".join(f"• {model}" for model in models)
            await update.message.reply_text(f"Available models:\n{model_list}")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to fetch models: {str(e)}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming text messages"""
        user_input = update.message.text
        chat_id = update.effective_chat.id
        
        try:
            # Send typing action to show bot is working
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            
            # Collect response chunks
            full_response = []
            for chunk in self.ollama.generate_streaming_response(
                model="deepseek-llm:latest",  # Default model
                prompt=user_input,
                temperature=0.7,
                max_tokens=500
            ):
                full_response.append(chunk)
                
            # Send complete response
            if full_response:
                await update.message.reply_text("".join(full_response))
            else:
                await update.message.reply_text("🤖 I didn't get a response. Please try again.")
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await update.message.reply_text("🚨 Sorry, I encountered an error processing your request.")

    def run(self):
        """Start the bot"""
        self.application.run_polling()

if __name__ == "__main__":
    # Configuration
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("Please set TELEGRAM_BOT_TOKEN environment variable")

    # Initialize components
    ollama_client = OllamaClient()
    bot = TelegramBot(ollama_client, TELEGRAM_TOKEN)

    # Start the bot
    print("Starting Telegram bot...")
    bot.run()