import json
import requests
from dm_pb2 import DmSegMobileReply
from google.protobuf.json_format import MessageToJson
 
 
b_web_cookie = 'SESSDATA=fd25e2e6%2C1660373048%2C287c9%2A21;'
 
 
def get_date_list():
    url = "https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=168855206&month=2022-02"
    headers = {
        'cookie': b_web_cookie
    }
    response = requests.get(url, headers=headers)
    print(json.dumps(response.json(), ensure_ascii=False, indent=4))
 
 
def dm_real_time():
    url_real_time = 'https://api.bilibili.com/x/v2/dm/web/seg.so?type=1&oid=168855206&pid=98919207&segment_index=1'
    resp = requests.get(url_real_time)
 
    DM = DmSegMobileReply()
    DM.ParseFromString(resp.content)
    data_dict = json.loads(MessageToJson(DM))
    # print(data_dict)
    # list(map(lambda x=None: print(x['content']), data_dict.get('elems', [])))

    # data_dict["elems"] 数据结构为列表，其中的每个元素是一个字典
    # 字典中存储了每条弹幕的信息，弹幕结构体详见 dm.proto 文件
    print("弹幕总数 = ", len(data_dict["elems"]))
    dm_list = data_dict["elems"]
    for k, v in dm_list[0].items():
        print(f"k = {k}, v = {v}")
 
 
def dm_history():
    url_history = 'https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid=168855206&date=2022-02-23'
    headers = {
        'cookie': b_web_cookie
    }
    resp = requests.get(url_history, headers=headers)
    DM = DmSegMobileReply()
    DM.ParseFromString(resp.content)
    data_dict = json.loads(MessageToJson(DM))
    # print(data_dict)
    list(map(lambda x=None: print(x['content']), data_dict.get('elems', [])))
 
 
if __name__ == '__main__':
    dm_real_time()
    # get_date_list()
    # dm_history()
    pass