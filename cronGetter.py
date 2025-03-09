import toml
import requests
import traceback, json, datetime, time
from time import strftime, localtime
from message import MessageSender
import logging
from typing import Dict, List, Tuple
from craw import stock

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config() -> List[Dict]:
    """
    从conf.toml加载配置
    返回: [{"name": "stock_name", "location": "market_location"}, ...]
    """
    try:
        with open('conf/conf.toml', 'r', encoding='utf-8') as f:
            config = toml.load(f)
            
        stock_configs = []
        
        # 遍历所有任务配置
        for task in config.get('task', []):
            stock_configs.append({
                "name": task['name'],
                "location": task['location']
            })
            
        logger.info(f"Loaded {len(stock_configs)} stock configs: {stock_configs}")
        return stock_configs
        
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def main():
    logger.info("Starting stock monitoring service...")
    message_sender = MessageSender()
    
    try:
        # 加载配置
        stock_configs = load_config()
        
        if not stock_configs:
            logger.error("Failed to load configuration")
            return
        
        # 创建任务列表
        tasks = []
        for config in stock_configs:
            try:
                task = stock([config])
                if task.urlList:  # 只添加成功初始化的任务
                    tasks.append(task)
                else:
                    logger.warning(f"Failed to initialize task for {config['name']} ({config['location']})")
            except Exception as e:
                logger.error(f"Error creating task for {config}: {str(e)}")
        
        logger.info(f"Initialized {len(tasks)} tasks")
        
        # 主循环
        while True:
            for task in tasks:
                try:
                    task.getNowData()
                except Exception as e:
                    logger.error(f"Error getting data for task: {str(e)}")
                    logger.error(traceback.format_exc())
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
        logger.error(traceback.format_exc())
        message_sender.send_feishu_message(f"Stock monitoring service error: {str(e)}")
        return

if __name__ == "__main__":
    main()