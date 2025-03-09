import requests
import traceback, json, datetime, time
from time import strftime, localtime
from message import MessageSender


class stock(object):

    def __init__(self, urlList, historyfiveDayUrlList, vmUrlImport):
        self.urlList = urlList
        self.historyfiveDayUrlList = historyfiveDayUrlList
        self.vmUrlImport = vmUrlImport
        return

    def getNowData(self):
        for i in self.urlList:
            timeStamp = int(time.time() * 1000)  # 转换为毫秒时间戳
            data = self.getData(i["url"])
            if data == "":
                break

            # 构建 JSON 行格式数据
            metric = {
                "metric": {
                    "__name__": "stock_price",  # 改为与 getHistoryDataFiveDay 一致
                    "stock_name": i["name"],  # 改为下划线格式
                    "location": i["location"],
                    "type": "realtime",
                },
                "values": [float(data["Result"][0]["TplData"]["result"]["price"])],
                "timestamps": [timeStamp],
            }

            # 添加其他可能的指标（如果数据中有的话）
            result_data = data["Result"][0]["TplData"]["result"]
            if "volume" in result_data:
                volume_metric = {
                    "metric": {
                        "__name__": "stock_volume",  # 改为与 getHistoryDataFiveDay 一致
                        "stock_name": i["name"],  # 改为下划线格式
                        "location": i["location"],
                        "type": "realtime",
                    },
                    "values": [float(result_data["volume"])],
                    "timestamps": [timeStamp],
                }
                vmStr = json.dumps(volume_metric)
                # print(f"Sending volume data for {i['name']} ({i['location']})")
                self.sendDataToVm(self.vmUrlExp, vmStr)

            # 发送价格数据
            vmStr = json.dumps(metric)
            # print(
            #     f"Sending price data for {i['name']} ({i['location']}): {metric['values'][0]}"
            # )
            self.sendDataToVm(self.vmUrlImport, vmStr)

    def getData(self, url):
        try:

            payload = ""
            headers = {"Content-Type": "application/json"}
            # print(urlIneed, payload, headers)
            resp = requests.post(url, data=payload, headers=headers)
            # if resp.status_code != 200 and retry > 0  :
            # self.tigger_ineed()
            # print(idc +' ' + appid    + "  error : " +   str(r.content) + ' get ins_list error , please manunal check' )
            # return
            str1 = str(resp.content, encoding="utf-8")
            data = json.loads(str1)
            # print("all insList len is ", len(data), "   ",data)

            return data
        except Exception as e:
            print(traceback.print_exc())
            return ""

    def sendDataToVm(self, url, data):
        try:
            headers = {
                "Content-Type": "text/plain",  # VictoriaMetrics expects text/plain for line protocol
            }

            # Send data with retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print("sendDataToVm3", url, data)
                    resp = requests.post(
                        url,
                        data=data,
                        headers=headers,
                        timeout=10,  # Add timeout to prevent hanging
                    )
                    resp.raise_for_status()  # Raise exception for 4XX/5XX status codes

                    if (
                        resp.status_code == 204
                    ):  # VictoriaMetrics returns 204 on successful write
                        return True

                    print(f"Unexpected response: {resp.status_code} - {resp.text}")
                    return False

                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:  # Last attempt
                        print(
                            f"Failed to send data after {max_retries} attempts: {str(e)}"
                        )
                        return False
                    print(f"Retry {attempt + 1}/{max_retries} after error: {str(e)}")
                    time.sleep(1)  # Wait before retry

        except Exception as e:
            print(f"Error sending data to VictoriaMetrics: {str(e)}")
            return False

    def getHistoryDataFiveDay(self):
        for i in self.historyfiveDayUrlList:
            timeStamp = int(time.time() * 1000)  # 使用毫秒时间戳
            data = self.getData(i["url"])
            if data == "":
                break

            # 构建 JSON 行格式数据
            json_lines = []

            # 遍历5天的数据
            for day_data in data["Result"]["fivedays"]:
                date = day_data.get("date", "")

                for point in day_data["priceinfos"]:
                    # 价格数据
                    price_metric = {
                        "metric": {
                            "__name__": "stock_price",  # 使用 __name__ 作为指标名
                            "stock_name": i["name"],
                            "location": i["location"],
                            "date": date,
                        },
                        "values": [float(point.get("price", 0))],
                        "timestamps": [
                            int(point.get("time", 0)) * 1000
                        ],  # 确保是毫秒时间戳
                    }
                    json_lines.append(json.dumps(price_metric))

                    # 成交量数据
                    if "volume" in point:
                        volume_metric = {
                            "metric": {
                                "__name__": "stock_volume",  # 使用独立的指标名
                                "stock_name": i["name"],
                                "location": i["location"],
                                "date": date,
                            },
                            "values": [float(point.get("volume", 0))],
                            "timestamps": [int(point.get("time", 0)) * 1000],
                        }
                        json_lines.append(json.dumps(volume_metric))

            # 每行发送一个数据点
            for line in json_lines:
                # print(f"Sending data point: {line}")
                success = self.sendDataToVm(self.vmUrlImport, line)
                if not success:
                    print(f"Failed to send data point: {line}")


def isNonTradingTime():
    now = localtime()
    now_time = strftime("%H:%M:%S", now)

    # 检查是否在 A 股交易时间（9:30-11:30, 13:00-15:00）之外
    trading_hours_morning = "09:30:00" <= now_time <= "11:30:00"
    trading_hours_afternoon = "13:00:00" <= now_time <= "15:00:00"

    # 如果是工作日（周一到周五）且不在交易时间
    if now.tm_wday < 5 and not (trading_hours_morning or trading_hours_afternoon):
        return True

    # 如果是周末
    if now.tm_wday >= 5:
        return True

    return False


if __name__ == "__main__":
    urlList = [
        {
            "url": "http://finance.pae.baidu.com/vapi/stockshort?code=09888&market=hk&finClientType=pc",
            "name": "baidu",
            "location": "hk",
        },
        {
            "url": "https://finance.pae.baidu.com/vapi/stockshort?code=BIDU&market=us&finClientType=pc",
            "name": "baidu",
            "location": "us",
        },
    ]
    historyfiveDayUrlList = [
        {
            "url": "https://finance.pae.baidu.com/selfselect/getstockquotation?code=09888&all=1&ktype=1&isIndex=false&isBk=false&isBlock=false&isFutures=false&stockType=hk&group=quotation_fiveday_hk&finClientType=pc",
            "name": "baidu",
            "location": "hk",
        },
        {
            "url": "https://finance.pae.baidu.com/selfselect/getstockquotation?code=BIDU&all=1&ktype=1&isIndex=false&isBk=false&isBlock=false&isFutures=false&stockType=us&group=quotation_fiveday_us&finClientType=pc",
            "name": "baidu",
            "location": "us",
        },
    ]
    task = stock(urlList, historyfiveDayUrlList, "http://localhost:8428/api/v1/import")
    task.getNowData()

    # 创建消息发送器实例
    message_sender = MessageSender()

    # 发送消息
    message_sender.send_feishu_message("vm done")

# if isNonTradingTime():  # 非交易时间时同步5天数据
#     task.getHistoryDataFiveDay()
# else:
#     task.getNowData()
