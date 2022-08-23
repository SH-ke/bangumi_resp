import requests
import re
# import csv


base_url = "https://www.bilibili.com/bangumi/play/ss835"
# base_url = "https://m.dytt8.net/index2.htm"

headers = {"User-Agent": "Mozilla/5.0"}
# resp = requests.get(base_url, verify=False) # 阻止验证
resp = requests.get(base_url) # 阻止验证
# resp.encoding = "gbk" # 更改字符集
page_content = resp.text # 获取网页源代码
resp.close() # 关闭访问

# print(page_content)

ep_id_obj = re.compile(r"last_ep_id:(.*?),")
name_obj = re.compile(r"\"name\": \"(.*?)\"")
print(ep_id_obj.search(page_content))
name = name_obj.search(page_content)
print(name)