import json, asyncio, aiohttp, os
from fake_useragent import UserAgent
from danmaku_parse import seg_so_resp
from task_lists import type_match
from media_resp import media_download


class CheckPoint:
    def __init__(self, id: str) -> None:
        self.cut = 360 * 1e3
        self.id = id
        self.task_json_path = f"./target/task/task_{id}.json"
        self.info_json_path = f"./target/task/info_{id}.json"


    def headers(self) -> dict:
        ua = UserAgent()
        return {
            "User-Agent": ua.random, 
        }
    
    async def create(self, type="") -> bool:
        # 1. 根据 task_xxx.json 设计check_point_xxx.json
        # 若没有 task_xxx.json 文件，则创建
        print(os.path.isfile(self.info_json_path))
        if not os.path.isfile(self.info_json_path):
            print("create info json")
            # loop = asyncio.get_event_loop()
            # loop.run_until_complete(type_match(id_str=self.id))
            await type_match(id_str=self.id)
            print("info json done")

        with open(self.info_json_path, 'r', encoding="utf") as f:
            data = json.load(f)
        
        tasks = []
        for idx, info in enumerate(data["info_list"]):
            task = {
                "name": info["name"],  
                "id": idx, 
                "dmk": False, 
                "video": False, 
                "audio": False, 
                "merge": False, 
                "dmk_list": [False] * int(info["duration"]/self.cut + 1), 
            }
            # 若没有视频链接则默认不下载
            if not info["video_url"]:
                task["video"] = True
            if not info["audio_url"]:
                task["audio"] = True
            tasks.append(task)

        if type == "video":
            for t in tasks:
                t["dmk"] = True
        elif type == "dmk":
            for t in tasks:
                t["video"] = t["audio"] = t["merge"] = True
        else:
            pass

        # 保存check_point.json
        with open(self.task_json_path, "w", encoding="utf") as f:
            json.dump({
                "title": data["title"], 
                "tasks": tasks, 
            }, f, indent=4, ensure_ascii=False)
        return True


    def tasks_match(self, task: dict, ep: dict, sess: str) -> list:
        tasks = []
        # 弹幕任务
        # print("task match", task["name"])
        if task["dmk"] is False:
            # 弹幕 api
            url = 'https://api.bilibili.com/x/v2/dm/web/seg.so'
            # 一个视频有多个弹幕文件，遍历
            for i in range(int(ep["duration"]/self.cut + 1)):
                params = {
                    "type": 1, 
                    "oid": ep["cid"], 
                    "pid": ep["aid"], 
                    "segment_index": i+1, 
                }
                # print("task append", ep["aid"], i)
                tasks.append(asyncio.create_task(
                    self.seg_so_resp(task["id"], sess, params, url, ep["bvid"]))
                    )
        if not task["video"]:
            tasks.append(asyncio.create_task(media_download(
                sess, ep["audio_url"], self.headers, "audio", ep["bvid"]
                )))
        if not task["audio"]:
            tasks.append(asyncio.create_task(media_download(
                sess, ep["audio_url"], self.headers, "audio", ep["bvid"]
                )))

        return tasks

    async def run_check_point(self):
        # 读取任务
        with open(self.task_json_path, "r", encoding="utf") as f:
            resps = json.load(f)["tasks"]
        # 读取url
        with open(self.info_json_path, "r", encoding="utf") as f:
            infos = json.load(f)["info_list"]
        # 分配异步协程任务
        tasks = [] # 异步协程任务列表
        async with aiohttp.ClientSession() as sess:
            for t in resps:
                idx = t["id"]
                ep = infos[idx]
                tasks.extend(self.tasks_match(t, ep, sess))
                print(f"task num : {len(tasks)}")

                # 测试一个视频
                break
            await asyncio.wait(tasks)


    async def run(self):
        # 调用异步协程 多次
        for _ in range(3):
            await self.run_check_point()

            # 若任务完成，则退出
            if self.is_finish():
                break


    async def seg_so_resp(self, idx: int, sess: aiohttp.ClientSession, 
                        params: dict, url: str, name: str) -> None:
        await seg_so_resp(sess, params, self.headers(), url, name)
        self.finish(idx, "dmk", params["segment_index"])


    def finish(self, idx: int, key: str, dmk_idx=0) -> None:
        # 将完成的任务置True 
        with open(self.task_json_path, "r", encoding="utf") as f:
            data = json.load(f)
        # 假定是某个弹幕任务下载完成
        if key == "dmk" and dmk_idx:
            data["tasks"][idx]["dmk_list"][dmk_idx-1] = True
            # 若此视频的弹幕军下载完成，则将 dmk 置 True
            if all(data["tasks"][idx]["dmk_list"]):
                data["tasks"][idx]["dmk"] = True
        # 考虑 video audio merge 的情况
        data["tasks"][idx][key] = True
        # 修改完成，存入task.json
        with open(self.task_json_path, "w", encoding="utf") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


    def is_finish(self) -> bool:
        # 判断是否所有任务都为 True【已完成】
        with open(self.task_json_path, "r", encoding="utf") as f:
            tasks = json.load(f)["tasks"]

        for t in tasks:
            # 获取任务列表中的所有 bool 值，作为判据
            # 若所有均为true 则任务全部完成
            judge = [v for v in t.values() if type(v) is bool]
            if not all(judge):
                # print("not finish !!")
                # print("扫描至", t["name"])
                return False

        print("finish ")
        return True


async def main():
    # ubw 29137 / 45745
    # fz 29923 / 13867 / 105055
    # 小林 98606 / 445875
    ckpt = CheckPoint("29923")
    await ckpt.create(type="")
    await ckpt.run()


if __name__ == '__main__':
    from datetime import datetime
    # os.system('chcp 65001') # 控制台中文编码

    start = datetime.now()
    # 主入口
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    end = datetime.now()
    print(f"共耗时{end - start}")
