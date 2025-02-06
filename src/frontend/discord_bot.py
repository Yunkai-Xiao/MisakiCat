# frontend/discord_bot.py
import os
import re
import random
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands
from backend.ollama import OllamaClient

# Load environment variables from parent directory
load_dotenv()


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AutoResponderBot(commands.Bot):
    def __init__(self, ollama_client: OllamaClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ollama = ollama_client
        self.active_model = "deepseek-r1:14b"
        self.conversation_history = {}
        self.response_cooldown = 10  # 5 minutes in seconds
        self.last_response_time = {}
        
        # Configuration
        self.response_probability = 0.5  # 30% chance to respond
        self.trigger_keywords = ["?", "what", "why", "how", "opinion"]
        self.ignore_prefixes = ("!", "?", "/")

    async def setup_hook(self):
        await self.tree.sync()
        # self.add_listener(self.on_message, "on_message")
        logger.info("Bot setup complete")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for interesting conversations"
            )
        )

    def should_respond(self, message: discord.Message) -> bool:
        """Determine if the bot should respond to a message"""
        # Basic checks
        if message.author == self.user:
            return False
        if message.content.startswith(self.ignore_prefixes):
            return False
            
        # Cooldown check
        last_time = self.last_response_time.get(message.channel.id, 0)
        if (message.created_at.timestamp() - last_time) < self.response_cooldown:
            return False
            
        # Contextual triggers
        content = message.content.lower()
        has_question = "?" in content
        mentions_bot = self.user.mentioned_in(message)
        contains_keyword = any(kw in content for kw in self.trigger_keywords)
        
        return mentions_bot or (has_question and contains_keyword) or random.random() < self.response_probability

    def build_prompt(self, context: list, message: str) -> str:
        """Create a prompt with structured response formatting"""
        nl = '\n'
        return (
            "Format your response with these EXACT sections:\n" +
            "[THINKING]\n"+
            "Internal analysis and reasoning\n"+
            "[/THINKING]\n"+
            "[RESPONSE]\n"+
            "Final answer for the user\n\n"+
            f"Conversation history:\n{nl.join(context[-3:])}\n"+
            f"New message: {message}\n"+
            "First analyze the message in [THINKING], then write [RESPONSE]."
        )

    def clean_response(self, raw_response: str) -> str:
        """Extract only the response portion from the model output"""
        # Try to extract the [RESPONSE] section
        response_match = re.search(
            r'\[RESPONSE\](.*?)(\n\[THINKING\]|$)', 
            raw_response, 
            flags=re.DOTALL | re.IGNORECASE
        )
        
        if response_match:
            cleaned = response_match.group(1).strip()
        else:
            # Fallback: Remove all thinking-related tags
            cleaned = re.sub(
                r'\[/?THINKING\].*?\[/THINKING\]', 
                '', 
                raw_response, 
                flags=re.DOTALL|re.IGNORECASE
            ).strip()
        
        # Clean up any remaining markdown or special characters
        return cleaned.replace('**', '').replace('__', '').strip()

    async def on_message(self, message: discord.Message):
        """Handle automatic responses to relevant messages"""
        print(message.content, self.should_respond(message))
        if not self.should_respond(message):
            return

        try:
            # Build conversation context
            user_id = message.author.id
            context = self.conversation_history.get(user_id, [])
            context.append(f"User: {message.content}")
            
            # Create structured prompt
            prompt = self.build_prompt(context, message.content)
            
            async with message.channel.typing():
                raw_response = self.ollama.generate_response(
                    model=self.active_model,
                    prompt=prompt,
                    temperature=0.5,
                    max_tokens=10000
                )
                print(raw_response)
                
            # Process and clean response
            cleaned_response = self.clean_response(raw_response)
            
            if cleaned_response:
                # Send response
                await message.reply(cleaned_response[:2000], mention_author=False)
                self.last_response_time[message.channel.id] = message.created_at.timestamp()
                
                # Update conversation history
                context.extend([
                    f"System Prompt: {prompt}",
                    f"Raw Response: {raw_response}",
                    f"Cleaned Response: {cleaned_response}"
                ])
                self.conversation_history[user_id] = context[-9:]  # Keep last 3 exchanges

        except Exception as e:
            print(f"Error in auto-response: {str(e)}")
            await message.channel.send("⚠️ An error occurred while processing that request.")

        # await self.process_commands(message)


class DiscordBotHandler:
    def __init__(self, ollama_client: OllamaClient):
        self.token = os.getenv("DISCORD_BOT_TOKEN")
        if not self.token:
            raise ValueError("DISCORD_BOT_TOKEN not found in .env file")
        
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        self.bot = AutoResponderBot(
            ollama_client,
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    def run(self):
        """Start the Discord bot"""
        self.bot.run(self.token)

if __name__ == "__main__":
    try:
        # Initialize components
        ollama_client = OllamaClient()
        bot_handler = DiscordBotHandler(ollama_client)
        
        # Start the bot
        logger.info("Starting Discord bot...")
        bot_handler.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise