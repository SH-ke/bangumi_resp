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


async def season_urls(ep: dict, info_list: list, credential: Credential) -> None:
    bvid = ep["bvid"]
    videoName = ep["share_copy"].split()[-1] # 视频名称
    p = ep["title"] # 视频序号

    # 获取视频、音频链接
    # 实例化视频对象
    v = video.Video(bvid=bvid, credential=credential)
    # 获取视频下载链接
    try:
        url = await v.get_download_url(0)
    except ResponseCodeException:
        print("非大会员无法访问视频文件，但弹幕文件可以访问")
    finally:
        url = {
            "dash": {
                "video" : [{"baseUrl": ''}], 
                "audio" : [{"baseUrl": ''}], 
            }
        }

    # 视频轨链接
    video_url = url["dash"]["video"][0]['baseUrl']
    # 音频轨链接
    audio_url = url["dash"]["audio"][0]['baseUrl']
    # print(f"video = {video_url}, audio = {audio_url}")

    # 创建 dict 写入 json 
    # 序号、标题、视频链接、音频链接
    info =  {
        'p': int(p), 
        'bvid': bvid, 
        'aid': ep["aid"], 
        'cid': ep["cid"], 
        'name': videoName, 
        'video_url': video_url, 
        'audio_url': audio_url, 
        'duration': ep["duration"], 
    }
    info_list.append(info)
    print(f"[info | resp done] bvid = {bvid}, p = {p}, name = {videoName}")


async def season_task(ep_id: str) -> dict:
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
    # 获取番剧名称
    title = result["season_title"]
    print("{:+^20}".format(f"【{title}】"))
    
    # 并行抓取 单集序号、标题、bvid cid aid 视频数据、音频数据
    info_list = []
    tasks = []
    for ep in result["episodes"]:
        tasks.append(asyncio.create_task(season_urls(ep, info_list, credential)))

    await asyncio.wait(tasks) # 分配协程任务

    # info_list 按分集序号排序
    info_list = sorted(info_list, key=lambda x: x["p"])

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

async def main() -> None:
    id_str = "103923"
    # id_str = "BV1tV411U7N3"
    isSave = True

    '''
    三国   327584
    西游   327107
    西游续 327339

    埃罗芒阿 103923 / 373847
    修罗场 65401
    魔禁1 83815
    龙与虎 66547
    日常 15185

    CSAPP BV1tV411U7N3
    '''
    # season id 和 bvid 的正则判断
    ep_id_obj = re.compile(r"^\d{5,6}$")
    bvid_obj = re.compile(r"^BV[a-zA-Z0-9]{10}$")

    if ep_id_obj.match(id_str):
        print("是番剧")
        task_json = await season_task(id_str)
    elif bvid_obj.match(id_str):
        print("是playlist")
        task_json = await playlist_task(id_str)
    else:
        print("暂不支持该种解析")
        return

    if isSave:
        with open(f"target/task_{id_str}.json", "w", encoding="utf8") as f:
            json.dump(task_json, f, indent=4, ensure_ascii=False)

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
    # 番剧、电视剧使用 ep_id 检索，一个电视剧对应多个 BV 号；
    # 视频列表都只有一个 BV 号