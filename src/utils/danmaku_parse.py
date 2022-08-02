import asyncio, aiohttp, json
from fake_useragent import UserAgent
from dm_pb2 import DmSegMobileReply
from google.protobuf.json_format import MessageToJson
 
# 弹幕下载函数 -> 批量 -> 异步协程
# ToDo 编写异步协程 弹幕下载程序


# 异步协程【seg.so接口响应】
# 单次请求一个seg.so文件，是协程下载的最小任务单元
async def seg_so_resp(sess: aiohttp.ClientSession, params: dict, HEADERS: dict, 
                    url: str, DM: DmSegMobileReply, 
                    name, save_json=True, save_so=False) -> bool:
    async with sess.get(url, params=params, headers=HEADERS) as resp:
        # 一次性获取弹幕二进制文件
        # 不用担心内存问题，弹幕文件本来就不大，而且已经360秒做了分块，可以一次性获取
        content = await resp.content.read()
        # 若返回值为空 则 return
        if not content:
            print("弹幕分片超出上限")
            return False
    
        DM = DmSegMobileReply() # 导入 protoc 结构体
        DM.ParseFromString(content) # 解析字符串
        data_dict = json.loads(MessageToJson(DM)) # 弹幕文本转json

        # data_dict["elems"] 数据结构为列表，其中的每个元素是一个字典
        # 字典中存储了每条弹幕的信息，弹幕结构体详见 dm.proto 文件
        # print("弹幕总数 = ", len(data_dict["elems"]))
        dm_list = data_dict["elems"]

        # 保存弹幕文件为json
        if save_json:
            with open(f"target/dm/dm_{name}_{params['segment_index']}.json", "w", encoding="utf8") as f:
                json.dump({
                    "elems": dm_list, 
                }, f, indent=4, ensure_ascii=False)

        # 直接保存二进制文件
        if save_so:
            with open(f"target/dm/dm_{name}_{params['segment_index']}.seg.so", "wb") as f:
                f.write(content)
    
        print(f"{name}_{params['segment_index']}")
    return True


# 主函数【弹幕下载】
# 下载 task_xx.json 中的所有弹幕任务 开辟多个异步协程任务[seg_so_resp] 
async def dmk_task(id_str: str) -> None:
    with open(f"target/task/task_{id_str}.json", "r", encoding="utf8") as f:
        dic = json.load(f)

    ua = UserAgent()
    HEADERS = {
        "User-Agent": ua.random, 
    }
    url = 'https://api.bilibili.com/x/v2/dm/web/seg.so'
    DM = DmSegMobileReply() # 导入 protoc 结构体
    # 遍历 task_list 下载番剧分集的弹幕
    tasks = [] # 协程任务列表
    async with aiohttp.ClientSession() as sess:
        for ep in dic["info_list"]:
            # status = True # 若返回值为空 则跳过循环
            # 弹幕每 360s 为一个文件，通过视频总时长，计算出一共有多少个文件
            # print("seg.so file num is ", int(ep["duration"]/360*1e-3))
            for i in range(int(ep["duration"]/360*1e-3) + 1):
                HEADERS["User-Agent"] = ua.random
                params = {
                    "type": 1, 
                    "oid": ep["cid"], 
                    "pid": ep["aid"], 
                    "segment_index": i+1, 
                }
                tasks.append(asyncio.create_task(seg_so_resp(sess, params, HEADERS, url, DM, ep["name"])))

            # 测试一个视频
            # break
        await asyncio.wait(tasks)

 
if __name__ == '__main__':
    from datetime import datetime
    # os.system('chcp 65001') # 控制台中文编码

    start = datetime.now()
    # 主入口
    id_str = "327584"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dmk_task(id_str))

    end = datetime.now()
    print(f"共耗时{end - start}")


    ## 断点续传 check_point
    # 1. 根据 task_xxx.json 设计check_point_xxx.json
    # creat()
    '''
// check point json
{
    list: "", # task_list.json的绝对路径
    tasks: [
        {
            name:, 
            id:, 
            dmk: True, # 已下载
            video: True, 
            audio: Fase, # 未执行
            merge: False, # 未执行
        },     
    ]
}
    '''

    # 2. run_check_point()
    # 获取task_list文件路径 -> 遍历tasks 列表 -> 将对应任务加入tasks列表

    # 3. finish()
    # 将对应任务置为 True 

    # 4. is_finished()
    # 判断所有任务是否完成

    # 5. merge_signal()
    # 合并任务的信号，每次完成视频、音频的任务后判断一次
    # 判断此视频的视频、音频文件是否下载完成
    # 若为False 函数直接返回 False
    # 若为True 发送信号，开辟线程任务【合并音频、视频文件】

    # 6. merge()
    # 开辟线程 执行合并任务

    # 7. ass_parse()
    # 弹幕解析任务 将json格式的弹幕数据转化为ass格式