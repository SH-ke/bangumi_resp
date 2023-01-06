import os, json, subprocess


FFMPEG_PATH = "ffmpeg"

def merge(bvid: str):
	audio = f"target/media/video_temp_{bvid}.m4s"
	video = f"target/media/audio_temp_{bvid}.m4s"
	merged_file = f"target/media/{bvid}.mp4"
	if os.path.isfile(merged_file):
		return
	subprocess.Popen(f'{FFMPEG_PATH}.exe -i {audio} -i {video} -vcodec copy -acodec copy {merged_file}', 
					stdout=subprocess.PIPE)
	# os.system(f'{FFMPEG_PATH}.exe -i {audio} -i {video} -vcodec copy -acodec copy {merged_file}')


def main():
	ep_id = "103923"
	with open(f"./target/task/task_{ep_id}.json", "r", encoding="utf") as f:
		tasks = json.load(f)["tasks"]
	with open(f"./target/task/info_{ep_id}.json", "r", encoding="utf") as f:
		infos = json.load(f)["info_list"]

	for t in tasks:
		if not t["merge"]:
			bvid = infos[t["id"]]["bvid"]
			merge(bvid)
			print(f"{bvid} 完成")
			# break


if __name__ == "__main__":
	from datetime import datetime

	start = datetime.now()
	main()

	end = datetime.now()
	print(f"共计耗时 {end-start}")