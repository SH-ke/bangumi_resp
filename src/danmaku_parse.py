import json
import requests
from dm_pb2 import DmSegMobileReply
from google.protobuf.json_format import MessageToJson
 
 
def dm_real_time():
    params = {
        "type": 1, 
        "oid": 168855206, 
        "pid": 98919207, 
        "segment_index": 1, 
        }
    url_real_time = 'https://api.bilibili.com/x/v2/dm/web/seg.so'
    resp = requests.get(url_real_time, params=params)
 
    DM = DmSegMobileReply() # 导入 protoc 结构体
    DM.ParseFromString(resp.content) # 解析字符串
    data_dict = json.loads(MessageToJson(DM)) # 弹幕文本转json

    # 若返回值为空 则 return
    if not data_dict:
        print("弹幕分片超出上限")
        return 

    # data_dict["elems"] 数据结构为列表，其中的每个元素是一个字典
    # 字典中存储了每条弹幕的信息，弹幕结构体详见 dm.proto 文件
    print("弹幕总数 = ", len(data_dict["elems"]))
    dm_list = data_dict["elems"]
    for k, v in dm_list[0].items():
        print(f"k = {k}, v = {v}")

    # 保存弹幕文件为json
    with open("target/dm_sgbl.json", "w", encoding="utf8") as f:
        json.dump({
            "elems": dm_list, 
        }, f, indent=4)

    # 直接保存二进制文件
    with open("target/dm_sgbl.seg.so", "wb") as f:
        f.write(resp.content)
 
 
if __name__ == '__main__':
    dm_real_time()