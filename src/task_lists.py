from logging import critical
import re
from fake_useragent import UserAgent
import requests
import asyncio
from bilibili_api import video, Credential
import os
import json


SESSDATA = ""
BILI_JCT = ""
BUVID3 = ""

# FFMPEG 路径，查看：http://ffmpeg.org/
FFMPEG_PATH = "ffmpeg"

async def medium_urls(bvid: str, credential:critical) -> tuple:
    # 实例化视频对象
    v = video.Video(bvid=bvid, credential=credential)
    # 获取视频下载链接
    url = await v.get_download_url(0)
    # 视频轨链接
    video_url = url["dash"]["video"][0]['baseUrl']
    # 音频轨链接
    audio_url = url["dash"]["audio"][0]['baseUrl']
    # print(f"video = {video_url}, audio = {audio_url}")

    return (video_url, audio_url)


async def season_urls(ep: dict, info_list: list, credential: Credential) -> None:
    bvid = ep["bvid"]
    videoName = ep["share_copy"].split()[-1] # 视频名称
    p = ep["title"] # 视频序号
    print(f"bvid = {bvid}, p = {p}, name = {videoName}")

    # 获取视频、音频链接
    video_url, audio_url = await medium_urls(bvid, credential)

    # 创建 dict 写入 json 
    # 序号、标题、视频链接、音频链接
    info =  {
        'p': p, 
        'name': videoName, 
        'video_url': video_url, 
        'auu ': audio_url, 
    }
    info_list.append(info)

async def season_task(ep_id: str) -> list:
    # 实例化 Credential 类
    credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)
    # 实例化 Video 类
    url = f"https://api.bilibili.com/pgc/view/web/season?ep_id={ep_id}"
    ua = UserAgent()
    headers = {
        "User-Ageny": ua.random,
        "Referer": "https://www.bilibili.com/", 
    }
    resp = requests.get(url, headers=headers)
    result = resp.json()["result"]
    resp.close()
    # 剧集文件夹
    title = result["season_title"]
    print("{:+^20}".format(f"【{title}】"))
    
    info_list = []
    tasks = []
    for ep in result["episodes"]:
        tasks.append(asyncio.create_task(season_urls(ep, info_list, credential)))

    await asyncio.wait(tasks)

    return info_list


async def main() -> None:
    id_str = "327584"
    # id_str = "BV13x41167ie"
    isSave = True

    '''
    三国   327584
    西游   327107
    西游续 327339
    '''
    # 埃罗芒阿 BV13x41167ie

    # season id 和 bvid 的正则判断
    ep_id_obj = re.compile(r"^\d{6}$")
    bvid_obj = re.compile(r"^BV[a-zA-Z0-9]{10}$")

    if ep_id_obj.match(id_str):
        print("是电视剧")
        info_list = await season_task(id_str)
    elif bvid_obj.match(id_str):
        print("是bvid")
        info_list = {}
    else:
        print("暂不支持该种解析")
        return

    if isSave:
        with open(f"target/task_{id_str}.json", "w") as f:
            json.dump({
                "info_list": info_list, 
            }, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    from datetime import datetime
    # os.system('chcp 65001') # 控制台中文编码

    start = datetime.now()
    # 主入口
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    end = datetime.now()
    print(f"共耗时{end - start}")

    ## 设计 task_list 的目的是将解析视频、音频地址的流程标准化
    ## 使用 task_list 目前必须为 番剧 电视剧 视频列表
    # 电视剧使用 ep_id 检索，一个电视剧对应多个 BV 号；
    # 番剧、视频列表都只有一个 BV 号