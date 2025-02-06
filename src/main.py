from backend.ollama import handle_chat_message

def main():
    test_message = "Hello, how are you?"
    response = handle_chat_message(test_message)
    print(f"Response from Ollama API: {response}")

if __name__ == "__main__":
    main()