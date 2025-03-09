import uuid
import requests
import json
import time
from config import Config # type: ignore

class MessageSender:
    def __init__(self):
        self.feishu_url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=user_id'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {Config.FEISHU_TOKEN}'
        }

    def send_feishu_message(self, message, max_retries=3):
        """
        发送飞书消息，带重试机制
        :param message: 要发送的消息内容
        :param max_retries: 最大重试次数
        :return: bool 是否发送成功
        """
        payload = {
            'content': json.dumps({"text": message}),
            'msg_type': 'text',
            'receive_id': Config.FEISHU_RECEIVE_ID,
            'uuid': str(uuid.uuid4())
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.feishu_url, headers=self.headers, json=payload)
                if response.status_code == 200:
                    print(f"Message sent successfully: {message}")
                    return True
                else:
                    print(f"Attempt {attempt + 1}/{max_retries} failed. Status: {response.status_code}")
                    print(f"Error response: {response.text}")
                    if attempt + 1 < max_retries:
                        time.sleep(2 ** attempt)  # 指数退避
                    continue
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries} error: {str(e)}")
                if attempt + 1 < max_retries:
                    time.sleep(2 ** attempt)
                continue
        
        print("Failed to send message after all retries")
        return False
