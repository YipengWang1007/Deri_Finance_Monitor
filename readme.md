环境：Python 3.7: web3, json, logging, traceback, time, datetime, csv, abc, typing, matplotlib 
公司原先封装代码：Chain.py, Preference.py 
监控系统主要脚本：monitor.py, netValue.py, dingding.py

monitor.py: 主要框架来自于web3.py官方说明文档，通过设定区块区间和abi 信息，链地址信息等获取智能
合约上的特定交易信息，输出格式为json。通过 维护静态对象，实现预防宕机和重启回溯功能。

netValue.py: 对获取的原始数据进行初步分析，目前支持追踪用户每次平仓 操作(加仓仅追踪平均持仓成本，
利润不发生实际改变)发生时的利润变化， 后续可以添加更多算法追踪账号盈利状态。当前支持matplotlib可
视化输出 账户盈利变化情况。

dingding.py: 基于钉钉群机器人助手的消息推送脚本，所有异常判断算法 加在这个文件内， 触发异常时会自
动向指定钉钉群推送交易异常警报。
