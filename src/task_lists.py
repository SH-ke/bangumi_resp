from fake_useragent import UserAgent
import requests
import asyncio
from bilibili_api import video, Credential
import os
import json

SESSDATA = ""
BILI_JCT = ""
BUVID3 = ""
ep_id = "327107"
'''
三国   327584
西游   327107
西游续 327339
'''

# FFMPEG 路径，查看：http://ffmpeg.org/
FFMPEG_PATH = "ffmpeg"


async def main(index=True):
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
    for ep in result["episodes"][:10]:
        bvid = ep["bvid"]
        videoName = ep["share_copy"].split()[-1] # 视频名称
        p = ep["title"] # 视频序号
        print(f"bvid = {bvid}, name = {videoName}, p = {p}")

        # 实例化视频对象
        v = video.Video(bvid=bvid, credential=credential)
        # 获取视频下载链接
        url = await v.get_download_url(0)
        # 视频轨链接
        video_url = url["dash"]["video"][0]['baseUrl']
        # 音频轨链接
        audio_url = url["dash"]["audio"][0]['baseUrl']
        # print(f"video = {video_url}, audio = {audio_url}")

        # 创建 dict 写入 json 
        # 序号、标题、视频链接、音频链接
        info = {
            'p': p, 
            'name': videoName, 
            'video_url': video_url, 
            'auu ': audio_url, 
        }
        info_list.append(info)

    return info_list


if __name__ == '__main__':
    from datetime import datetime
    os.system('chcp 65001') # 控制台中文编码

    start = datetime.now()
    # 主入口
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end = datetime.now()
    print(f"共耗时{end - start}")