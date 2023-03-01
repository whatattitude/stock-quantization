#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2020 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Description:
Authors: wangyu(wangyu69@baidu.com)
Date:    2020/12/22
"""
from math import fabs
from re import M
import traceback

import subprocess
import time,json
import configparser
import requests
from datetime import datetime, timedelta
import toml
import os
from pprint import pprint
import craw


class readConf(object):

    def __init__(self, confPath, hiToken, hiList):
        self.hiToken = hiToken
        self.hiList = hiList
        self.configDict = self.read_conf(confPath)
        return
    
    
    def send_hi_robot_message(self, message):
        """
        发送hi-rebot消息
        :param : toid_list type:list hi群list
        :param : webhook   type:str  hi群新建机器人webhook
        :param : message_list   type:list  消息list，
        message_list = [
        {
            "content": "大家好，这是来自机器人的测试消息，请忽略\n",
            "type": "TEXT"
        }]
        :return:
        :rtype:
        """
        url = self.hiToken
        headers = {
            "Content-Type": "application/json;"
        }
        message_list = [
            {
                "content": message,
                "type": "TEXT"
            }
        ]
        data = {
            "message": {
                "header": {
                    "toid": self.hiList
                },
                "body": message_list
            }
        }
        data = json.dumps(data)
        #print(data)
        try:
            res = requests.post(url, headers=headers, data=data)
            #print("=======send_hi_robot_message========")
            ##print(data,headers,url)
            #print (str(res))
        except Exception:
            print(str(traceback.format_exc()).encode('utf-8').decode('latin-1'))

    
    def read_conf(self, confPath):
        dictionary = toml.load(os.path.expanduser(confPath))
        print(dictionary)
        return dictionary

   

if __name__ == '__main__':
    
    hiToken = "http://apiin.im.baidu.com/api/msg/groupmsgsend?access_token=d5f9c21ea91973e3c7d3be0011ade5ca1"
    hiList = [7957720]
    taskConf = readConf("./conf/conf.toml", hiToken, hiList)
    #print(task.configDict)


    while True:

        for i in taskConf.configDict["task"]:
            urlList = []
            historyfiveDayUrlList = []
            urlListItem={}
            urlListItem["name"]=i["name"]
            urlListItem["location"]=i["location"]
            urlListItem["url"]=i["url"]
            urlList.append(urlListItem)
            historyfiveDayUrlListItem={}
            historyfiveDayUrlListItem["name"]=i["name"]
            historyfiveDayUrlListItem["location"]=i["location"]
            historyfiveDayUrlListItem["url"]=i["historyfiveDayUrl"]
            historyfiveDayUrlList.append(historyfiveDayUrlListItem)
        task = craw.stock(urlList, "", 'http://localhost:8428/write',  historyfiveDayUrlList, "http://localhost:8428/api/v1/import/prometheus")
        task.getAllData()
        if craw.isFriday() :
            task.getHistoryData()

        time.sleep(1)
 
    '''
    urlList = [{"url":"http://finance.pae.baidu.com/vapi/stockshort?code=09888&market=hk&finClientType=pc","name":"baidu","location":"hk"}, 
               {"url":"https://finance.pae.baidu.com/vapi/stockshort?code=BIDU&market=us&finClientType=pc","name":"baidu","location":"us"}]
    historyfiveDayUrlList = [{"url":"https://finance.pae.baidu.com/selfselect/getstockquotation?code=09888&all=1&ktype=1&isIndex=false&isBk=false&isBlock=false&isFutures=false&stockType=hk&group=quotation_fiveday_hk&finClientType=pc","name":"baidu","location":"hk"},
                      {"url":"https://finance.pae.baidu.com/selfselect/getstockquotation?code=BIDU&all=1&ktype=1&isIndex=false&isBk=false&isBlock=false&isFutures=false&stockType=us&group=quotation_fiveday_us&finClientType=pc","name":"baidu","location":"us"}]
    task = stock(urlList, "", 'http://localhost:8428/write',  historyfiveDayUrlList, "http://localhost:8428/api/v1/import/prometheus")
    task.getAllData()
    if isFriday() :
        task.getHistoryData()

    while True:
        task.getAllData()
        time.sleep(1)
     '''
