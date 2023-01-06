# 极速视频下载器

本项目基于requests爬虫和bilibili_api等第三方库实现番剧和其他部分视频、弹幕数据的下载。为了提供极致的下载速度体验，特意编写此项目。

## 项目功能简介

### 列表下载

根据 `eposide id` 获取番剧、电视剧、合集播放列表的信息，通过 `eposide id` 创建一个批量下载任务，支持断点续传，支持非会员的视频、弹幕资源的批量下载。番剧和电视剧等拥有相似的接口，因此后文仅以番剧作为陈述对象。

包含模块：视频/音频异步下载、音视频合并、播放列表信息响应、断点任务创建。

1. 根据 `eposide id` 获取番剧分集列表信息
2. 创建断点下载任务
    + 下载视频、音频、弹幕数据
    + 解析弹幕数据并保存（json格式）
    + 合并音视频文件
    + 断点续传
    + 弹幕格式转换

### 番剧暴搜

每一部番剧、电视剧都拥有一个唯一的 `season id`（例如，[超炮](https://www.bilibili.com/bangumi/play/ss425) 425，[魔禁](https://www.bilibili.com/bangumi/play/ss963) 963，[三国](https://www.bilibili.com/bangumi/play/ss33626) 33626）；其中的每一集都拥有唯一的 `eposide id`（例如，魔禁 [第一集](https://www.bilibili.com/bangumi/play/ep83810) 83810，[第二集](https://www.bilibili.com/bangumi/play/ep83811) 83811，[第二十四集](https://www.bilibili.com/bangumi/play/ep83833) 83833）。

基于以上原理，又由于 `season id` `eposide id`是连续递增的整形数值，因此可以通过遍历 `eposide id` 来获取 [bilibili](https://www.bilibili.com/)的所有番剧。此种功能被命名为**番剧暴搜**，此功能的目标是实现**弹幕数据库计划**。**弹幕数据库计划**是二十一世纪前二十年中国弹幕文化的诺亚方舟。

包含模块：代理池、7z包管理

### 弹幕数据库

[bilibili](https://www.bilibili.com/)的精华在于其丰富、高质量的弹幕资源（当然，二创视频也是精华，只不过弹幕的门槛更低因此独一无二）。但由于时代变迁等诸多不可抗力原因，番剧弹幕发展势头并不令人看好。因此，本项目致力于保存大部分bilibili的番剧弹幕，建立起一个较为完备的弹幕数据库。倘若在不久的将来这些弹幕被毁于一旦，还可以在其他地方找寻到备份。因此，本项目以弹幕的诺亚方舟自居。

包含模块：代理池、7z包管理、数据库、弹幕格式转换

## 项目架构

本项目的目录结构以及各个文件的说明如下：

```json
{
    // 后续再完善
}
```

### 断点续传设计

```python

# 5. merge_signal()
# 合并任务的信号，每次完成视频、音频的任务后判断一次
# 判断此视频的视频、音频文件是否下载完成
# 若为False 函数直接返回 False
# 若为True 发送信号，开辟线程任务【合并音频、视频文件】

# 6. merge()
# 开辟线程 执行合并任务

# 7. ass_parse()
# 弹幕解析任务 将json格式的弹幕数据转化为ass格式

## 断点续传部分功能还未实现
# 1. 架构调整 所有文件重命名均以 bvid 为准，减少不必要的麻烦
# 防止 dm_fate/zero.json 此类名称的出现
# task_list中的p 出现了 '14(OVA)' '4 - 1' 需要调整
# 调整之后要对之前的版本进行兼容 adaptor/rename_dmk 
# 以 bvid 重命名文件
# 2. 添加配置文件 存储变量 路径等信息
# 3. 添加更高层级的批量操作 调研ss_id ep_id 的区别
# 寻找批量的接口 api
```

### 分集信息获取

通过 `eposide id`, `bvid` 等解析播放列表中每一集的信息。

```python
## 设计 task_list 的目的是将解析视频、音频地址的流程标准化
## 使用 task_list 目前必须为 番剧 电视剧 视频列表
# 番剧、电视剧使用 ep_id 检索，一个电视剧对应多个 BV 号；
# 视频列表都只有一个 BV 号

## season 解析思路
# ep_id -> json["result"]["episodes"]

## playlist 解析思路
# bvid -> get_info() -> json["ugc_season"]["sections"][0]["episodes"]
# 获取到 [p, aid, cid, bvid, name, duration]
# bvid -> get_download_url -> video_url, audio_url

## 统一化修改
# 信息列表响应[ep_id/bvid] -> json_parse[键值对有出入] -> 
# [p, aid, cid, bvid, (title/share_copy), (page-duration/duration)] (playlist/season)
# [此处为多次响应，应用异步协程]info_list -> video_url, audio_url

## 函数分配
# url_resp(), season_parse(), playlist_parse(), type_match()
# 为task_list 添加更新日期
# 构建弹幕数据库时需要构建一个暴搜函数，暴力搜索ep_id
```

## 项目展望

后期将计划开发基于 Django 架构的弹幕网站（弹幕视频播放器？），基于 Spring Boot, Vue, React, Rust 的相关工具也在计划中。
