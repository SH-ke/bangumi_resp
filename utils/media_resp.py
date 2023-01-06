from fake_useragent import UserAgent
import asyncio, aiohttp, json


# FFMPEG 路径，查看：http://ffmpeg.org/
FFMPEG_PATH = "ffmpeg"


async def media_download(sess: aiohttp.ClientSession, media_url: str, 
                    HEADERS: dict, type: str, bvid: str) -> None:
    if not media_url:
        return
    # 下载媒体流
    async with sess.get(media_url, headers=HEADERS) as resp:
        length = resp.headers.get('content-length')
        with open(f'target/media/{type}_temp_{bvid}.m4s', 'wb') as f:
            process = 0
            while True:
                chunk = await resp.content.read(1024)
                if not chunk:
                    break

                process += len(chunk)
                print(f'\r下载媒体流 {type} {process} / {length}', end='')
                f.write(chunk)


async def main(index=True):
    from check_point import CheckPoint
    ua = UserAgent()
    headers = {
        "User-Ageny": ua.random,
        "Referer": "https://www.bilibili.com/", 
    }
    # 创建任务
    id_str = "103923"
    ckpt = CheckPoint(id_str)
    await ckpt.create()
    # 读取任务
    with open(f"./target/task/info_{id_str}.json", "r", encoding="utf") as f:
        infos = json.load(f)["info_list"]
    # 分配异步任务
    tasks = []
    async with aiohttp.ClientSession() as sess:
        for t in infos:
            # print(t)
            # 添加aio任务
            headers["User-Agent"] = ua.random
            tasks.append(asyncio.create_task(media_download(
                sess, t["video_url"], headers, "video", t["bvid"]
                )))
            tasks.append(asyncio.create_task(media_download(
                sess, t["audio_url"], headers, "audio", t["bvid"]
                )))
            # break
        await asyncio.wait(tasks)


if __name__ == '__main__':
    from datetime import datetime
    # os.system('chcp 65001') # 控制台中文编码

    start = datetime.now()
    # 主入口
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end = datetime.now()
    print(f"共耗时{end - start}")