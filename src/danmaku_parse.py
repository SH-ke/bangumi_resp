import json
import requests
from dm_pb2 import DmSegMobileReply
from google.protobuf.json_format import MessageToJson
 
# 弹幕下载函数 -> 批量 -> 异步协程
# ToDo 编写异步协程 弹幕下载程序
# ToDo 观察弹幕分文件的原因 观察不同文件视频的时间分布、发布时间分布
 
def dmk_download(params: dict, name, save_json=True, save_so=False) -> bool:
    url = 'https://api.bilibili.com/x/v2/dm/web/seg.so'
    resp = requests.get(url, params=params)
 
    DM = DmSegMobileReply() # 导入 protoc 结构体
    DM.ParseFromString(resp.content) # 解析字符串
    data_dict = json.loads(MessageToJson(DM)) # 弹幕文本转json

    # 若返回值为空 则 return
    if not data_dict:
        print("弹幕分片超出上限")
        return False

    # data_dict["elems"] 数据结构为列表，其中的每个元素是一个字典
    # 字典中存储了每条弹幕的信息，弹幕结构体详见 dm.proto 文件
    print("弹幕总数 = ", len(data_dict["elems"]))
    dm_list = data_dict["elems"]
    for k, v in dm_list[0].items():
        print(f"k = {k}, v = {v}")

    # 保存弹幕文件为json
    if save_json:
        with open(f"target/dm/dm_{name}_{params['segment_index']}.json", "w", encoding="utf8") as f:
            json.dump({
                "elems": dm_list, 
            }, f, indent=4, ensure_ascii=False)

    # 直接保存二进制文件
    if save_so:
        with open(f"target/dm/dm_{name}_{params['segment_index']}.seg.so", "wb") as f:
            f.write(resp.content)
    
    return True
 

def download_task_dm(id_str: str) -> None:
    with open(f"target/task/task_{id_str}.json", "r", encoding="utf8") as f:
        dic = json.load(f)
    # 遍历 task_list 下载番剧分集的弹幕
    for ep in dic["info_list"]:
        params = {
            "type": 1, 
            "oid": ep["cid"], 
            "pid": ep["aid"], 
            "segment_index": 1, 
        }
        status = True # 若返回值为空 则跳过循环
        # 弹幕每 360s 为一个文件，通过视频总时长，计算出一共有多少个文件
        print("seg.so file num is ", int(ep["duration"]/360*1e-3))
        for i in range(int(ep["duration"]/360*1e-3) + 1):
            params["segment_index"] = i+1
            status = dmk_download(params, ep["name"])
            if not status:
                continue

        # if ep["p"] > 2:
        #     break

 
if __name__ == '__main__':
    from datetime import datetime
    # os.system('chcp 65001') # 控制台中文编码

    start = datetime.now()
    # 主入口
    id_str = "15185"
    download_task_dm(id_str)

    end = datetime.now()
    print(f"共耗时{end - start}")