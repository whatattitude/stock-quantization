from flask import Flask, request, jsonify
from message import MessageSender
import logging

app = Flask(__name__)
message_sender = MessageSender()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/webhook/api/v2/alerts', methods=['POST'])
def handle_alert():
    try:
        alerts = request.json  # 直接获取告警数组
        logger.info(f"Received alert data: {alerts}")
        
        if not alerts:  # 检查是否为空
            return jsonify({"status": "success", "message": "No alerts received"}), 200
            
        # 遍历所有告警
        for alert in alerts:
            status = "firing" if alert.get('endsAt') == "0001-01-01T00:00:00Z" else "resolved"
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
            
            # 构建消息内容
            message = f"""🚨 警报状态: {status.upper()}
报警名称: {labels.get('alertname', 'N/A')}
严重程度: {labels.get('severity', 'N/A')}
位置: {labels.get('location', 'N/A')}
股票: {labels.get('stock_name', 'N/A')}
描述: {annotations.get('description', 'N/A')}
详情: {annotations.get('summary', 'N/A')}
开始时间: {alert.get('startsAt', 'N/A')}
结束时间: {alert.get('endsAt', 'N/A')}"""

            logger.info(f"Sending message: {message}")
            
            # 发送到飞书
            success = message_sender.send_feishu_message(message)
            if not success:
                logger.error("Failed to send message to Feishu")
                return jsonify({"status": "error", "message": "Failed to send to Feishu"}), 500

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting webhook server...")
    app.run(host='0.0.0.0', port=5000)