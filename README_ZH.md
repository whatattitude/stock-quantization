
[英文](README.md) | 中文

## 📖 简介

一个秒级实时自动抓取每天股价变化并存入时序数据库（victoriametrics）的脚本

## 🚀 功能：

- 实时抓取百度股市通中的股票价格  （精度秒级）
- 周级备份百度股市的股票的价格 (精度分钟级)

## 目录结构

- victoria-metrics-prod 时序型数据库二进制文件
- craw.py 抓取脚本
- conf.py 跟进配置文件生成抓取任务&周期抓取的脚本
- conf/conf.toml 抓取任务配置文件

##  使用

- 克隆仓库到本地`git clone https://github.com/whatattitude/stock-quantization.git`
- 使用默认配置启动时序数据库`./victoria-metrics-data`
- 更新conf.toml里面配置【当前仅支持百度股市通接口--https://gushitong.baidu.com/stock/us-BIDU】
- 执行`python3 conf.py`

### 配置文件说明
```
name="baidu"  股票名称
location="us"   港股、美股、或者A股 【股票类型标注】
historyfiveDayUrl="https://finance.pae.baidu.com/selfselect/getstockquotation?code=BIDU&all=1&ktype=1&isIndex=false&isBk=false&isBlock=false&isFutures=false&stockType=us&group=quotation_fiveday_us&finClientType=pc"  近5日股票数据获取接口
url="https://finance.pae.baidu.com/vapi/stockshort?code=BIDU&market=us&finClientType=pc"  今日股票数据获取接口
prometheusWrite="http://localhost:8428/write"  本机时序型数据库写入接口，不建议修改
prometheusExport= "http://localhost:8428/api/v1/import/prometheus" 本机时序型数据库写入接口，不建议修改
```
### 数据可视化
- vm-ui 本机时序数据库自带可视化网址:
``` go
http://localhost:8428/vmui/?#/?g0.expr=%7B__name__%21%3D%22%22%2Ctype%3D%22now%22%7D&g0.range_input=6h&g0.end_input=2023-02-28T09%3A19%3A46&g0.relative_time=last_6_hours
```
