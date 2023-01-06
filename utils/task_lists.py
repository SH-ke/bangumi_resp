import re
from fake_useragent import UserAgent
import requests
import asyncio
from bilibili_api import video, Credential
from bilibili_api.exceptions.ResponseCodeException import ResponseCodeException
import json


SESSDATA = ""
BILI_JCT = ""
BUVID3 = ""

# FFMPEG 路径，查看：http://ffmpeg.org/
FFMPEG_PATH = "ffmpeg"


async def season_urls(p: int, info_list: list, credential: Credential) -> None:
    # 获取视频、音频链接
    # 实例化视频对象
    v = video.Video(bvid=info_list[p]["bvid"], credential=credential)
    # 获取视频下载链接
    try:
        url = await v.get_download_url(0)
    except ResponseCodeException:
        print("非大会员无法访问视频文件，但弹幕文件可以访问")
        return

    # 视频轨链接
    info_list[p]["video_url"] = url["dash"]["video"][0]['baseUrl']
    # 音频轨链接
    info_list[p]["audio_url"] = url["dash"]["audio"][0]['baseUrl']
    print("[info] resp done: bvid = {}, p = {:>4}, name = {}".format(info_list[p]["bvid"], p, info_list[p]["name"]))


async def season_task(ep_id: str) -> dict:
    # 实例化 Credential 类
    credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)
    url = f"https://api.bilibili.com/pgc/view/web/season?ep_id={ep_id}"
    ua = UserAgent()
    headers = {
        "User-Ageny": ua.random,
        "Referer": "https://www.bilibili.com/", 
    }
    resp = requests.get(url, headers=headers)
    result = resp.json()["result"]
    resp.close()
    # 获取番剧名称
    title = result["season_title"]
    print("{:+^20}".format(f"【{title}】"))
    
    # 解析 单集序号、标题、bvid cid aid
    info_list = []
    for p, ep in enumerate(result["episodes"]):
        info_list.append({
            'p': p, 
            'bvid': ep["bvid"], 
            'aid': ep["aid"], 
            'cid': ep["cid"], 
            'name': ep["long_title"], 
            'video_url': '', 
            'audio_url': '', 
        'duration': ep["duration"], 
        })
    # 并行抓取 视频数据、音频数据
    tasks = []
    for idx, ep in enumerate(result["episodes"]):
        tasks.append(asyncio.create_task(season_urls(idx, info_list, credential)))

    await asyncio.wait(tasks) # 分配协程任务
    return {
        "title": title, 
        "info_list": info_list, 
    }


async def playlist_urls(v: video, p: int, info_list: list) -> None:
    # 获取视频下载链接
    url = await v.get_download_url(p)
    # 视频轨链接
    video_url = url["dash"]["video"][0]['baseUrl']
    # 音频轨链接
    audio_url = url["dash"]["audio"][0]['baseUrl']

    info_list[p]["video_url"] = video_url
    info_list[p]["audio_url"] = audio_url


async def playlist_task(bvid: str) -> list:
    # 实例化 Credential 类
    credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)
    # 实例化 Video 类
    v = video.Video(bvid=bvid, credential=credential)
    # 新建文件夹
    info = await v.get_info() # 获取Playlist信息

    # 并行抓取 单集序号、标题、bvid cid aid 
    info_list = []
    for p, ep in enumerate(info["ugc_season"]["sections"][0]["episodes"]):
        info_list.append({
            'p': p, 
            'bvid': ep["bvid"], 
            'aid': ep["aid"], 
            'cid': ep["cid"], 
            'name': ep["title"], 
            'video_url': '', 
            'audio_url': '', 
            'duration': ep["page"]["duration"],
        })

    # 视频数据、音频数据 异步协程
    tasks = []
    for p in range(info['videos']): # 播放列表集数 info['videos']
        tasks.append(asyncio.create_task(playlist_urls(v, p, info_list)))
    await asyncio.wait(tasks) # 分配协程任务

    return {
        "title": info["ugc_season"]["title"], 
        "info_list": info_list, 
    }


# 主函数【创建任务列表】
# 判别id号的类别使用合适的解析方式下载，目前支持两种解析方式 [season_task/playlist_task]
async def type_match(id_str="327584", isSave=True) -> None:
    '''
    三国   327584
    西游   327107
    西游续 327339
    红楼梦 327871

    埃罗芒阿 103923 / 373847
    修罗场 65401
    魔禁1 83815
    龙与虎 66547
    日常 15185
    奇蛋物语 374357
    ubw 29137 / 45745
    fz 29923 / 13867 / 105055
    小林 98606 / 445875

    CSAPP BV1tV411U7N3
    '''
    # season id 和 bvid 的正则判断
    ep_id_obj = re.compile(r"^\d{5,6}$")
    bvid_obj = re.compile(r"^BV[a-zA-Z0-9]{10}$")

    if ep_id_obj.match(id_str):
        print("eposide id")
        task_json = await season_task(id_str)
    elif bvid_obj.match(id_str):
        print("bvid")
        task_json = await playlist_task(id_str)
    else:
        print("暂不支持该种解析")
        return

    print("请求收集完毕！")
    if isSave:
        with open(f"target/task/info_{id_str}.json", "w", encoding="utf8") as f:
            json.dump(task_json, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    from datetime import datetime
    # os.system('chcp 65001') # 控制台中文编码

    start = datetime.now()
    # 主入口
    loop = asyncio.get_event_loop()
    loop.run_until_complete(type_match())

    end = datetime.now()
    print(f"共耗时{end - start}")
