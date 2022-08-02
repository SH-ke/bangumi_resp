import json
from danmaku_parse import seg_so_resp


class CheckPoint:
    def __init__(self) -> None:
        self.cut = 360 * 1e3
    
    def create(self, id):
    # 1. 根据 task_xxx.json 设计check_point_xxx.json
        path = f"target/task/info_{id}.json"
        with open(path, 'r', encoding="utf") as f:
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
            tasks.append(task)

        # 保存check_point.json
        with open(f"./target/task/task_{id}.json", "w", encoding="utf") as f:
            json.dump({
                "title": data["title"], 
                "tasks": tasks, 
            }, f, indent=4, ensure_ascii=False)



if __name__ == '__main__':
    from datetime import datetime
    # os.system('chcp 65001') # 控制台中文编码

    start = datetime.now()
    # 主入口
    cp = CheckPoint()
    cp.create("327871")

    end = datetime.now()
    print(f"共耗时{end - start}")

''' '''
    ## 断点续传 check_point
    # 1. 根据 task_xxx.json 设计check_point_xxx.json
    # creat()
'''
// check point json
{
    list: "", # task_list.json的绝对路径
    title:
    tasks: [
        {
            name:, 
            id:, 
            dmk: True, # 已下载
            video: True, 
            audio: Fase, # 未执行
            merge: False, # 未执行
            dmk_list: [0, 0, 0], # 弹幕的下载列表
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