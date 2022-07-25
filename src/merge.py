import os
import re


path = "D:/DataBase_SHke_dev/Download_SHke_dev/Motrix/西游记续集"
# FFMPEG 路径，查看：http://ffmpeg.org/
FFMPEG_PATH = "ffmpeg"
os.system('chcp 65001') # 控制台中文编码
os.chdir(path)

merge_set = set()
for file in os.listdir(path):
	if file[-4:] == ".m4s":
		# print(file[11:-4])
		merge_set.add(file[11:-4])

for name in merge_set:
	os.system(f'{FFMPEG_PATH}.exe -i video_temp_{name}.m4s -i audio_temp_{name}.m4s -vcodec copy -acodec copy ../西游记续集_res/{name}.mp4')