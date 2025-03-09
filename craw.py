import requests
import traceback, json, datetime, time
from time import strftime, localtime
from message import MessageSender
import urllib.parse
import logging

logger = logging.getLogger(__name__)

class stock(object):

    def __init__(self, stock_configs):
        """
        初始化股票监控
        :param stock_configs: 股票配置列表 [{"name": "baidu", "location": "hk"}, ...]
        :param vmUrlImport: VictoriaMetrics导入URL
        """
        self.token = "D43BF722C8E33BDC906FB84D85E326E8"
        self.vmUrlImport =  "http://localhost:8428/api/v1/import"
        self.urlList = []
        self.historyfiveDayUrlList = []
        
        # 遍历配置，生成URL列表
        for config in stock_configs:
            stock_name = config["name"]
            market_type = self.convert_location_to_market(config["location"])
            
            # 查询股票代码
            stock_code = self.get_stock_code_by_market(stock_name, market_type)
            if not stock_code:
                logging.warning(f"No stock code found for {stock_name} in {market_type}")
                continue
                
            # 生成实时数据URL
            realtime_url = self.generate_realtime_url(stock_code, config["location"])
            self.urlList.append({
                "url": realtime_url,
                "name": stock_name,
                "location": config["location"]
            })
            
            # 生成5日历史数据URL
            history_url = self.generate_history_url(stock_code, config["location"])
            self.historyfiveDayUrlList.append({
                "url": history_url,
                "name": stock_name,
                "location": config["location"]
            })
            
        logging.info(f"Initialized with {len(self.urlList)} stocks")
        self.stock_map = self.init_stock_map()

    def init_stock_map(self):
        """初始化股票名称到代码的映射"""
        try:
            # 百度股票搜索API
            search_url = "https://finance.pae.baidu.com/vapi/stocksearch"
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            stock_map = {}
            for stock_info in self.urlList:
                stock_name = stock_info["name"]
                if stock_name not in stock_map:
                    # 搜索股票
                    params = {"wd": stock_name, "finClientType": "pc"}
                    response = requests.get(search_url, params=params, headers=headers)
                    data = response.json()
                    
                    if data.get("Result"):
                        for item in data["Result"]:
                            # 存储不同市场的代码
                            if item.get("StockMarket") == "hk":
                                stock_map[f"{stock_name}_hk"] = item.get("StockCode")
                            elif item.get("StockMarket") == "us":
                                stock_map[f"{stock_name}_us"] = item.get("StockCode")
                            elif item.get("StockMarket") == "sh" or item.get("StockMarket") == "sz":
                                stock_map[f"{stock_name}_cn"] = item.get("StockCode")
            
            logger.info(f"Initialized stock map: {stock_map}")
            return stock_map
            
        except Exception as e:
            logger.error(f"Error initializing stock map: {str(e)}")
            return {}

    def get_stock_code(self, name, market):
        """
        获取股票代码
        :param name: 股票名称
        :param market: 市场(hk/us/cn)
        :return: 股票代码
        """
        key = f"{name}_{market}"
        return self.stock_map.get(key)

    def update_stock_code(self, name, market):
        """
        更新特定股票的代码
        :param name: 股票名称
        :param market: 市场(hk/us/cn)
        """
        try:
            search_url = "https://finance.pae.baidu.com/vapi/stocksearch"
            params = {"wd": name, "finClientType": "pc"}
            headers = {"Content-Type": "application/json"}
            
            response = requests.get(search_url, params=params, headers=headers)
            data = response.json()
            
            if data.get("Result"):
                for item in data["Result"]:
                    if item.get("StockMarket") == market:
                        self.stock_map[f"{name}_{market}"] = item.get("StockCode")
                        logger.info(f"Updated stock code for {name}_{market}: {item.get('StockCode')}")
                        return item.get("StockCode")
            
            logger.warning(f"No stock code found for {name} in market {market}")
            return None
            
        except Exception as e:
            logger.error(f"Error updating stock code for {name}_{market}: {str(e)}")
            return None

    def convert_location_to_market(self, location):
        """转换location到市场类型"""
        market_map = {
            "hk": "港股",
            "us": "美股",
            "ab": "A股",
            "sh": "沪A",
            "sz": "深A"
        }
        return market_map.get(location, "")

    def generate_realtime_url(self, code, location):
        """生成实时数据URL"""
        base_url = "https://finance.pae.baidu.com/vapi/stockshort"
        return f"{base_url}?code={code}&market={location}&finClientType=pc"

    def generate_history_url(self, code, location):
        """生成历史数据URL"""
        base_url = "https://finance.pae.baidu.com/selfselect/getstockquotation"
        return f"{base_url}?code={code}&all=1&ktype=1&isIndex=false&isBk=false&isBlock=false&isFutures=false&stockType={location}&group=quotation_fiveday_{location}&finClientType=pc"

    def search_stock_code(self, stock_name):
        """
        通过东方财富接口搜索股票代码
        :param stock_name: 股票名称
        :return: 字典列表，包含股票代码、市场等信息
        """
        try:
            # URL编码股票名称
            encoded_name = urllib.parse.quote(stock_name)
            url = f"https://searchapi.eastmoney.com/api/suggest/get"
            params = {
                "input": stock_name,
                "type": "14",
                "token": self.token
            }
            headers = {
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.eastmoney.com/"
            }

            response = requests.get(url, params=params, headers=headers)
            data = response.json()

            if "QuotationCodeTable" in data and "Data" in data["QuotationCodeTable"]:
                results = []
                for item in data["QuotationCodeTable"]["Data"]:
                    stock_info = {
                        "code": item.get("Code"),                    # 股票代码
                        "name": item.get("Name"),                    # 股票名称
                        "market": item.get("SecurityTypeName"),      # 市场类型（A股、港股、美股）
                        "market_code": item.get("Market"),           # 市场代码
                        "security_type": item.get("SecurityType")    # 证券类型
                    }
                    results.append(stock_info)
                
                logging.info(f"Found {len(results)} results for {stock_name}: {results}")
                return results
            else:
                logging.warning(f"No results found for {stock_name}")
                return []

        except Exception as e:
            logging.error(f"Error searching stock code for {stock_name}: {str(e)}")
            return []

    def get_stock_code_by_market(self, stock_name, market_type="A股"):
        """
        根据股票名称和市场类型获取股票代码
        :param stock_name: 股票名称
        :param market_type: 市场类型（A股、港股、美股）
        :return: 股票代码或None
        """
        results = self.search_stock_code(stock_name)
        for result in results:
            if result["market"] == market_type:
                return result["code"]
        return None

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
    # 简化的配置
    stock_configs = [
        {
            "name": "大位科技",
            "location": "sh"
        },
         {
            "name": "五洲新春",
            "location": "sh"
        },
         {
            "name": "拓维信息",
            "location": "sz"
        },
         {
            "name": "华友钴业",
            "location": "sh"
            },
         {
            "name": "华映科技",
            "location": "sz"
        }

    ]
    # 创建任务列表
    tasks = []
    for config in stock_configs:
        try:
            task = stock([config])
            if task.urlList:  # 只添加成功初始化的任务
                tasks.append(task)
            else:
                logging.warning(f"Failed to initialize task for {config['name']} ({config['location']})")
        except Exception as e:
            logging.error(f"Error creating task for {config}: {str(e)}")
    
    logging.info(f"Initialized {len(tasks)} tasks")
        # 主循环
    while True:
        for task in tasks:
            try:
                task.getNowData()
            except Exception as e:
                logging.error(f"Error getting data for task: {str(e)}")
        time.sleep(1)

    # 创建消息发送器实例
    message_sender = MessageSender()

    # 发送消息
    message_sender.send_feishu_message("vm done")

# if isNonTradingTime():  # 非交易时间时同步5天数据
#     task.getHistoryDataFiveDay()
# else:
#     task.getNowData()
