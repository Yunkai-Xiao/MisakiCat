from wechatpy import WeChatClient, WeChatMessage

class WeChatChatApp:
    def __init__(self, app_id, app_secret):
        self.client = WeChatClient(app_id, app_secret)
        self.user_sessions = {}

    def send_message(self, user_id, message):
        self.client.message.send_text(user_id, message)

    def receive_message(self, message):
        user_id = message['FromUserName']
        content = message['Content']
        self.store_message(user_id, content)
        response = self.process_message(content)
        self.send_message(user_id, response)

    def store_message(self, user_id, message):
        # Logic to store message in memory or database
        pass

    def process_message(self, message):
        # Logic to process the message and interact with the Ollama backend
        return "Processed response from Ollama"

    def get_user_session(self, user_id):
        return self.user_sessions.get(user_id, None)

    def set_user_session(self, user_id, session_data):
        self.user_sessions[user_id] = session_data