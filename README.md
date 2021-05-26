# 介绍

fingermp是一款高效易用的web指纹识别工具，目前只支持首页识别，利用Wappalyzer的匹配规则（可自行编写规则）。

通过asyncio异步框架，提高web请求并发效率

在指纹规则比较大的时候（本项目不提供内部指纹规则）解析速率比较慢，fingermap通过进程绕过GIL的限制利用多核进行计算

# 使用

```python
  λ python fingerMap.py -h
    @Tool    :   fingerMap
    @Author  :   coffee time
    @Version :   1.0
    @Desc    :   一款web指纹识别工具
usage: fingerMap.py [-h] [-c COROUTINENUM] [-f FILE] [-v VERSION] [-u URL]optional arguments:
-h, --help            show this help message and exit
-c COROUTINENUM, --coroutineNum COROUTINENUM
协程并发数量
-f FILE, --file FILE  url文件
-v VERSION, --version VERSION
是否查询版本,0为不查询，1为查询
-u URL, --url URL     url
```

# 快速使用

单个url

```python
python fingerMap.py -u https://www.baidu.com
```

批量扫描

```python
python fingerMap.py -f test.txt
```

# todo

添加插件模式突破首页识别，更深度识别资产指纹。



# 致谢声明

fingermap在编写过程中，主要是对的优秀开源【python-Wappalyzer】进行封装改造

* **[python-Wappalyzer](https://github.com/chorsley/python-Wappalyzer)**
