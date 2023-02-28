import requests
import traceback,json,datetime,time
from time import strftime, localtime

        
class node_autobounce_task(object):

    def __init__(self, urlList, mess, vmUrl, historyfiveDayUrlList, vmUrlExp):
        self.urlList = urlList
        self.vmUrl = vmUrl
        self.historyfiveDayUrlList = historyfiveDayUrlList
        self.vmUrlExp = vmUrlExp
        return
    
    def getAllData(self):
        for i in (self.urlList):
            timeStamp =  time.time()
            data = self.getData(i["url"])
            if data == "":
                break
            #stock_baidu{location="us",name="baidu",type="now"}
            vmStr = 'stock,type=now,name=%s,location=%s baidu=%s'  \
            % (i["name"], i["location"], data['Result'][0]['TplData']['result']['price'] )
            print(vmStr, datetime.datetime.now())
            self.sendDataToVm(self.vmUrl, vmStr)
            
        return vmStr
    
    def getData(self, url):
        try:
           
            payload=''
            headers = {
                'Content-Type': 'application/json'
            }
            #print(urlIneed, payload, headers)
            resp = requests.post(url, data=payload, headers=headers)            
            #if resp.status_code != 200 and retry > 0  : 
                #self.tigger_ineed()
                #print(idc +' ' + appid    + "  error : " +   str(r.content) + ' get ins_list error , please manunal check' )
                #return
            str1=str(resp.content, encoding = "utf-8")
            data=json.loads(str1)
            #print("all insList len is ", len(data), "   ",data)    

           
            return data
        except Exception as e:
            print(traceback.print_exc())
            return ""
    
    def sendDataToVm(self, url,  data):
            payload=data
            headers = {
                'Content-Type': 'text'
            }
            #print(urlIneed, payload, headers)
            resp = requests.post(url, data=payload, headers=headers)   
            str1=str(resp.content, encoding = "utf-8")
              
            print(str1)

    def getHistoryData(self):
        for i in (self.historyfiveDayUrlList):
            timeStamp =  time.time()
            data = self.getData(i["url"])
            if data == "":
                break
            vmStr=""
            for  d in data["Result"]["fivedays"]:
                print(d)
                for dPont in d["priceinfos"]:
                    print(dPont)
                    #stock{type="fiveDay"}
                    vmStr += 'stock{type="fiveDay",name="%s",location="%s"} %s %s\n'  \
                    % (i["name"], i["location"], dPont["price"], dPont["time"])
            print(vmStr)
            self.sendDataToVm(self.vmUrlExp, vmStr)

def isFriday():
    now_time = strftime("%H:%M:%S", localtime())
    print(now_time)
    if localtime().tm_wday == 4 and now_time == "17:00:00":
        return True
    return False
        

if __name__ == '__main__':
    urlList = [{"url":"http://finance.pae.baidu.com/vapi/stockshort?code=09888&market=hk&finClientType=pc","name":"baidu","location":"hk"}, 
               {"url":"https://finance.pae.baidu.com/vapi/stockshort?code=BIDU&market=us&finClientType=pc","name":"baidu","location":"us"}]
    
    
    historyfiveDayUrlList = [{"url":"https://finance.pae.baidu.com/selfselect/getstockquotation?code=09888&all=1&ktype=1&isIndex=false&isBk=false&isBlock=false&isFutures=false&stockType=hk&group=quotation_fiveday_hk&finClientType=pc","name":"baidu","location":"hk"},
                      {"url":"https://finance.pae.baidu.com/selfselect/getstockquotation?code=BIDU&all=1&ktype=1&isIndex=false&isBk=false&isBlock=false&isFutures=false&stockType=us&group=quotation_fiveday_us&finClientType=pc","name":"baidu","location":"us"}]
    task = node_autobounce_task(urlList, "", 'http://localhost:8428/write',  historyfiveDayUrlList, "http://localhost:8428/api/v1/import/prometheus")
    task.getAllData()
    if isFriday() :
        task.getHistoryData()

    while True:
        task.getAllData()
        time.sleep(1)

