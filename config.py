import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    FEISHU_TOKEN = os.getenv('FEISHU_TOKEN')
    FEISHU_RECEIVE_ID = os.getenv('FEISHU_RECEIVE_ID')
    FEISHU_RECEIVE_ID_TYPE = os.getenv('FEISHU_RECEIVE_ID_TYPE')
    # 飞书配置
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID')
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET')