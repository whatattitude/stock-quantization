
[英文](README.md) | 中文

## 📖 简介

一个秒级实时自动抓取每天股价变化并存入时序数据库（victoriametrics）的脚本

## 🚀 功能：

- 实时抓取百度股市通中的股票价格  （精度秒级）
- 周级备份百度股市的股票的价格 (精度分钟级)

## 目录结构

- victoria-metrics-prod 时序型数据库二进制文件
- craw.py 抓取脚本
- conf/task.ini 抓取任务配置文件
- conf/vm.ini 抓取任务配置文件
- log 日志

##  使用

### 命令行启动

### 配置文件说明

### 数据可视化
- vm-ui link:
``` go
http://localhost:8428/vmui/?#/?g0.expr=%7B__name__%21%3D%22%22%2Ctype%3D%22now%22%7D&g0.range_input=6h&g0.end_input=2023-02-28T09%3A19%3A46&g0.relative_time=last_6_hours
```
