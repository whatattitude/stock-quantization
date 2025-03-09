import uuid
import requests
import json
import time
from config import Config # type: ignore

class MessageSender:
    def __init__(self):
        self.feishu_url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=user_id'
        self.app_id = Config.FEISHU_APP_ID
        self.app_secret = Config.FEISHU_APP_SECRET
        self.access_token = None
        self.token_expires_time = 0

    def get_access_token(self):
        """
        获取飞书访问令牌
        """
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    self.access_token = result.get("tenant_access_token")
                    self.token_expires_time = time.time() + result.get("expire") - 60  # 提前60秒更新
                    return True
            print(f"Failed to get access token: {response.text}")
            return False
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            return False

    def ensure_token_valid(self):
        """
        确保访问令牌有效
        """
        if not self.access_token or time.time() > self.token_expires_time:
            return self.get_access_token()
        return True

    def send_feishu_message(self, message, max_retries=3):
        """
        发送飞书消息，带重试机制
        :param message: 要发送的消息内容
        :param max_retries: 最大重试次数
        :return: bool 是否发送成功
        """
        if not self.ensure_token_valid():
            print("Failed to get valid access token")
            return False

        payload = {
            'content': json.dumps({"text": message}),
            'msg_type': 'text',
            'receive_id': Config.FEISHU_RECEIVE_ID,
            'uuid': str(uuid.uuid4())
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.feishu_url, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == 0:
                        print(f"Message sent successfully: {message}")
                        return True
                    elif result.get("code") == 99991663:  # token 失效
                        if self.get_access_token():  # 重新获取 token
                            headers['Authorization'] = f'Bearer {self.access_token}'
                            continue
                print(f"Attempt {attempt + 1}/{max_retries} failed. Status: {response.status_code}")
                print(f"Error response: {response.text}")
                if attempt + 1 < max_retries:
                    time.sleep(2 ** attempt)
                continue
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries} error: {str(e)}")
                if attempt + 1 < max_retries:
                    time.sleep(2 ** attempt)
                continue
        
        print("Failed to send message after all retries")
        return False
