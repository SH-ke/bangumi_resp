from fake_useragent import UserAgent
import requests
import asyncio
from bilibili_api import video, Credential
import aiohttp
import os

SESSDATA = ""
BILI_JCT = ""
BUVID3 = ""
down_path = "D:/DataBase_SHke_dev/Download_SHke_dev/Motrix"
ep_id = "327339"
'''
三国   327584
西游   327107
西游续 327339
'''

# FFMPEG 路径，查看：http://ffmpeg.org/
FFMPEG_PATH = "ffmpeg"


def mkPlaylist(title):
    # 新建文件夹
    if ' ' in title:
        title = title.replace(' ', '')
    dir = f'{down_path}/{title}/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    os.chdir(dir)



async def aioDownload(sess, video_url, audio_url, HEADERS, videoName):
    # 下载视频流
    async with sess.get(video_url, headers=HEADERS) as resp:
        length = resp.headers.get('content-length')
        with open(f'video_temp_{videoName}.m4s', 'wb') as f:
            process = 0
            while True:
                chunk = await resp.content.read(1024)
                if not chunk:
                    break

                process += len(chunk)
                print(f'\r下载视频流 {process} / {length}', end='')
                f.write(chunk)

    # 下载音频流
    async with sess.get(audio_url, headers=HEADERS) as resp:
        length = resp.headers.get('content-length')
        with open(f'audio_temp_{videoName}.m4s', 'wb') as f:
            process = 0
            while True:
                chunk = await resp.content.read(1024)
                if not chunk:
                    break

                process += len(chunk)
                print(f'\r下载音频流 {process} / {length}', end='')
                f.write(chunk)

    # # 混流
    # os.system(f'{FFMPEG_PATH}.exe -i video_temp_{videoName}.m4s -i audio_temp_{videoName}.m4s -vcodec copy -acodec copy {videoName}.mp4')

    # # 删除临时文件
    # os.remove(f"video_temp_{videoName}.m4s")
    # os.remove(f"audio_temp_{videoName}.m4s")

    # print(f'\r已下载为：{videoName}.mp4')


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
    print(f"title = {title}")
    mkPlaylist(title)
    
    eps = result["episodes"]
    # [25, 27, 31, 32, 48]
    # eps = [result["episodes"][idx-1] for idx in [25]]
    block = 3 # 每次下3集
    loops = [eps[idx:idx+block] for idx in range(0, len(eps), block)]
    # 分配异步任务
    tasks = []
    for loop in loops:
        async with aiohttp.ClientSession() as sess:
            for ep in loop:
                bvid = ep["bvid"]
                videoName = ep["share_copy"].split()[-1] # 视频名称
                p = ep["title"] # 视频序号
                if ' ' in videoName:
                    videoName = videoName.replace(' ', '')
                if '/' in videoName:
                    videoName = videoName.replace('/', '-')
                if index:
                    videoName = f"P{p}_{videoName}"

                v = video.Video(bvid=bvid, credential=credential)
                print(f"\nname = {videoName}, bvid = {bvid}")
                # 获取视频下载链接
                url = await v.get_download_url(0)
                # 视频轨链接
                video_url = url["dash"]["video"][0]['baseUrl']
                # 音频轨链接
                audio_url = url["dash"]["audio"][0]['baseUrl']
                # 添加aio任务
                headers["User-Agent"] = ua.random
                tasks.append(asyncio.create_task(aioDownload(sess, video_url, audio_url, headers, videoName)))
            await asyncio.wait(tasks)
        
        print("{:+^50}".format(f" part = {p} done "))




if __name__ == '__main__':
    from datetime import datetime
    os.system('chcp 65001') # 控制台中文编码

    start = datetime.now()
    # 主入口
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end = datetime.now()
    print(f"共耗时{end - start}")