import requests
from fake_useragent import UserAgent
# import csv


base_url = "http://httpbin.org/ip"
ua = UserAgent()
HEADERS = {
    "User-Agent": ua.random, 
}
proxy = {
    "http": "socks5://113.93.241.99:44844", 
}

resp = requests.get(base_url, headers=HEADERS, proxies=proxy)
# ip_resp = resp.text # 获取网页源代码
ip_resp = resp.json()
resp.close() # 关闭访问

print("当前ip --", ip_resp["origin"])