# My Python Chat App

This project is a multi-platform chat application that integrates with WeChat, Discord, and Telegram using Ollama as the backend. It stores and retrieves chat messages, allowing for a seamless user experience across different messaging platforms.

## Features

- Integration with WeChat, Discord, and Telegram
- Utilizes Ollama for backend processing of chat messages
- Stores chat history for future retrieval
- User session management for each platform

## Project Structure

```
my-python-chat-app
├── src
│   ├── backend
│   │   └── ollama.py        # Ollama backend implementation
│   ├── frontend
│   │   ├── wechat.py        # WeChat integration
│   │   ├── discord.py       # Discord integration
│   │   └── telegram.py      # Telegram bot functionality
│   ├── memory
│   │   └── storage.py       # Message storage and retrieval
│   └── main.py              # Entry point of the application
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/my-python-chat-app.git
   cd my-python-chat-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the necessary API keys and settings for WeChat, Discord, and Telegram in the respective integration files.

4. Run the application:
   ```
   python src/main.py
   ```

## Usage Guidelines

- Follow the instructions in each frontend integration file to set up the respective messaging platform.
- Ensure that the Ollama backend is properly configured to handle chat messages.
- Use the memory storage functions to manage chat history as needed.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.