# 在此基础上修改：https://github.com/T-K-233/KG-Downloader

# 主要修改内容有
# 根据本地目录存有歌曲链接的文件批量读取和下载JSON、歌曲、专辑图片
# 增加超时判定和自动重试,一定要成功后才会进行下一条。
# 增加同名文件判定，会自动编号 #2 #3 #4......特别注意我这里把m4a和mp4视为一样来排序，例如abc.m4a, abc #2.mp4, abc #3.mp4
# 因为个人习惯去掉了命令行执行功能，需要在代码里自行设定相关参数

# 无关痛痒的备注
# JSON文件里还有另外一个链接，下载下来是MP4格式，但是和m4a的md5是一样的。查看真实格式后发现似乎就是是音频？

# 你需要设置的地方有？
# interrupted_line：重启点行数，默认一开始就是0
# links_file_path：包含了K歌歌曲链接文件，这里默认在同文件夹下
# DOWNLOAD_PATH：设置下载目录名，这里默认为同文件夹下的downloads-temp文件夹，没有就创建。
# 特别注意点：有部分歌曲的名字比较奇怪，不知道为何不能保存，需要手动添加判定在download()方法里面。
# 中断后记得记下位置，设置上面的重启点即可继续。


import os
import json
import requests

import time
import random


class Downloader:
    DOWNLOAD_PATH = "downloads-temp"
    TEXT_BEFORE_JSON = "window.__DATA__ = "
    TEXT_AFTER_JSON = "; </script>"

    def __init__(self, download_path=None):
        if download_path:
            self.download_path = download_path
        else:
            self.download_path = self.DOWNLOAD_PATH
        self.data = {}

    def checkFolder(self):
        # 获取代码文件所在的目录路径
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # 要判定的目录名称
        directory_name = self.download_path

        # 构建目录的完整路径
        directory_path = os.path.join(current_directory, directory_name)

        # 判定目录是否存在
        if os.path.exists(directory_path):
            print("目录已存在，继续执行相应操作。")
        else:
            print("目录不存在，将创建新目录。")
            # 创建新目录
            os.makedirs(directory_path)
            print("目录创建成功。")

    def parse(self, uri):
        print("Parsing {0}...".format(uri))
        # max_attempts = 3  # 最大尝试次数
        timeout = 10  # 请求超时时间（秒）

        attempts = 0  # 当前尝试次数
        # while attempts < max_attempts:
        while True:
            try:
                response = requests.get(uri, timeout=timeout)
                break  # 成功获取响应，退出循环
            except requests.exceptions.Timeout:
                print("Request timeout. Retrying...")
                attempts += 1
                print(f"第{attempts}次尝试失败")
                wait_time2 = random.uniform(1.0, 10.0)  # 设置等待时间范围（1秒到10秒之间）
                time.sleep(wait_time2)  # 等待后重新尝试
            except requests.exceptions.RequestException as e:
                print("An error occurred during the request:", str(e))
                attempts += 1
                wait_time2 = random.uniform(1.0, 10.0)  # 设置等待时间范围（1秒到10秒之间）
                time.sleep(wait_time2)  # 等待后重新尝试
        else:
            print("Max attempts reached. Exiting.")

        if response is not None:
            content = response.text

            start_idx = content.find(self.TEXT_BEFORE_JSON)
            content = content[start_idx + len(self.TEXT_BEFORE_JSON):]

            end_idx = content.find(self.TEXT_AFTER_JSON)
            content = content[:end_idx]

            self.data = json.loads(content)
            print(self.data)

            playurl = self.data.get("detail").get("playurl")
            song_name = self.data.get("detail").get("song_name")

            playurl_video = self.data.get("detail").get("playurl_video")

            print(
                "Found song \"{0}\" with playurl: {1} and playurl_video: {2}".format(song_name, playurl, playurl_video))

            cover = self.data.get("detail").get("cover")

            print("Found song \"{0}\" with image {1}".format(song_name, cover))

            # 保存到同名JSON文件
            if (
                    song_name == "How Does A Moment Last Forever(From &amp;quot;Beauty and the Beast&amp;quot;/Soundtrack Version)"):
                output_file_path = self.get_unique_file_path(
                    os.path.join(self.download_path, "How Does A Moment Last Forever[?]" + ".json"))
                with open(output_file_path, 'w') as output_file:
                    json.dump(self.data, output_file, indent=4)
            elif song_name == "Beauty and the Beast(From &amp;quot;Beauty and the Beast&amp;quot;/Soundtrack Version)":
                output_file_path = self.get_unique_file_path(
                    os.path.join(self.download_path, "Beauty and the Beast[?]" + ".json"))
                with open(output_file_path, 'w') as output_file:
                    json.dump(self.data, output_file, indent=4)
            else:
                output_file_path = self.get_unique_file_path(os.path.join(self.download_path, song_name + ".json"))
                with open(output_file_path, 'w') as output_file:
                    json.dump(self.data, output_file, indent=4)

    def download(self):
        song_name = self.data.get("detail").get("song_name")

        # 下载m4a歌曲/mp4视频
        playurl = self.data.get("detail").get("playurl")
        playurl_video = self.data.get("detail").get("playurl_video")

        # 请注意有的歌曲名会报错，例如下面这两个，执行会被打断，这时候在下面格式添加歌曲名保存修改逻辑就行
        if (
                song_name == "How Does A Moment Last Forever(From &amp;quot;Beauty and the Beast&amp;quot;/Soundtrack Version)"):
            song_name = "How Does A Moment Last Forever[?]"
        if song_name == "Beauty and the Beast(From &amp;quot;Beauty and the Beast&amp;quot;/Soundtrack Version)":
            song_name = "Beauty and the Beast[?]"
        if playurl != "":
            print("Downloading...")
            response = requests.get(playurl)
            output_file_path = self.get_unique_file_path(os.path.join(self.download_path, song_name + ".m4a"))
            with open(output_file_path, "wb") as f:
                f.write(response.content)
            print("Finished.")
        # 如果是视频，那么是没有playurl的，只有playrul_video
        else:
            print("Downloading...VIDEO")
            response = requests.get(playurl_video)
            output_file_path = self.get_unique_file_path(os.path.join(self.download_path, song_name + ".mp4"))
            with open(output_file_path, "wb") as f:
                f.write(response.content)
            print("Finished.VIDEO")

        # 下载专辑图片，这里获取的是JSON里面能找到的最大图JPG
        cover = self.data.get("detail").get("cover")
        playurl = cover
        if (
                song_name == "How Does A Moment Last Forever(From &amp;quot;Beauty and the Beast&amp;quot;/Soundtrack Version)"):
            song_name = "How Does A Moment Last Forever[?]"
        if song_name == "Beauty and the Beast(From &amp;quot;Beauty and the Beast&amp;quot;/Soundtrack Version)":
            song_name = "Beauty and the Beast[?]"

        print("Downloading...")
        response = requests.get(playurl)
        # output_file_path = self.get_unique_file_path(os.path.join(self.download_path, song_name))
        output_file_path = self.get_unique_file_path(os.path.join(self.download_path, song_name + ".jpg"))

        with open(output_file_path, "wb") as f:
            f.write(response.content)
        print("Finished.")

    # 单独下载专辑图的两个函数，根据情况自行使用。
    def parse_cover(self, uri):
        print("Parsing {0}...".format(uri))
        max_attempts = 3  # 最大尝试次数
        timeout = 10  # 请求超时时间（秒）

        attempts = 0  # 当前尝试次数
        # while attempts < max_attempts:
        while True:
            try:
                response = requests.get(uri, timeout=timeout)
                break  # 成功获取响应，退出循环
            except requests.exceptions.Timeout:
                print("Request timeout. Retrying...")
                attempts += 1
                print(f"第{attempts}次尝试失败")
                wait_time2 = random.uniform(1.0, 10.0)  # 设置等待时间范围（1秒到3秒之间）
                time.sleep(wait_time2)  # 等待1秒后重新尝试
            except requests.exceptions.RequestException as e:
                print("An error occurred during the request:", str(e))
                attempts += 1
                wait_time2 = random.uniform(1.0, 10.0)  # 设置等待时间范围（1秒到3秒之间）
                time.sleep(wait_time2)  # 等待1秒后重新尝试
        else:
            print("Max attempts reached. Exiting.")

        if response is not None:
            content = response.text

            start_idx = content.find(self.TEXT_BEFORE_JSON)
            content = content[start_idx + len(self.TEXT_BEFORE_JSON):]

            end_idx = content.find(self.TEXT_AFTER_JSON)
            content = content[:end_idx]

            self.data = json.loads(content)
            print(self.data)

            playurl = self.data.get("detail").get("playurl")
            song_name = self.data.get("detail").get("song_name")

            playurl_video = self.data.get("detail").get("playurl_video")

            cover = self.data.get("detail").get("cover")

            print("Found song \"{0}\" with image {1}".format(song_name, cover))


    def download_cover(self):
        # playurl = self.data.get("detail").get("playurl")
        song_name = self.data.get("detail").get("song_name")
        # playurl_video = self.data.get("detail").get("playurl_video")
        cover = self.data.get("detail").get("cover")
        playurl = cover
        if (
                song_name == "How Does A Moment Last Forever(From &amp;quot;Beauty and the Beast&amp;quot;/Soundtrack Version)"):
            song_name = "How Does A Moment Last Forever[?]"
        if song_name == "Beauty and the Beast(From &amp;quot;Beauty and the Beast&amp;quot;/Soundtrack Version)":
            song_name = "Beauty and the Beast[?]"

        print("Downloading...")
        response = requests.get(playurl)
        # output_file_path = self.get_unique_file_path(os.path.join(self.download_path, song_name))
        output_file_path = self.get_unique_file_path(os.path.join(self.download_path, song_name + ".jpg"))

        with open(output_file_path, "wb") as f:
            f.write(response.content)
        print("Finished.")


    # 对于重名的歌曲，赋予编号
    # 更正逻辑：对于m4a和mp4我们应该认为是一回事儿，防止出现编号错误。
    # 例如已经有Song.mp4，后面有一个Song.m4a应该被命名为Song #2.m4a才对。
    # 这样保证JSON，音乐，专辑图片名字是一致的。
    def get_unique_file_path(self, file_path):

        file_name, file_extension = os.path.splitext(file_path)
        # print(file_extension)
        if file_extension == '.mp4':
            # print("found mp4")
            file_path = file_name + '.m4a'
            if os.path.exists(file_path):
                # file_name, file_extension = os.path.splitext(file_path)
                index = 2
                while os.path.exists(file_path):
                    file_path = f"{file_name} #{index}{file_extension}"
                    print(file_path)
                    index += 1
                file_name, file_extension = os.path.splitext(file_path)
                file_path = file_name+'.mp4'
        else:
            if os.path.exists(file_path):
                file_name, file_extension = os.path.splitext(file_path)
                index = 2
                while os.path.exists(file_path):
                    file_path = f"{file_name} #{index}{file_extension}"
                    index += 1
        return file_path


if __name__ == "__main__":
    #重启点
    interrupted_line = 0  #
    #含有链接的文件
    links_file_path = "lines-temp.md"
    # links_file_path = "lines-3413xxxxxxFeixiang.md"

    with open(links_file_path, 'r') as file:
        urls = file.readlines()

    dl = Downloader()
    dl.checkFolder()
    count = 0

    for url in urls:
        count = count + 1
        if (count < interrupted_line):
            pass
        else:
            # 生成随机等待时间
            # wait_time = random.uniform(1.0, 5.0)  # 设置等待时间范围（1秒到3秒之间）

            # 执行等待
            # time.sleep(wait_time)

            print(f"现在开始第 {count} 行")

            uri = url.strip()
            dl.parse(uri)
            dl.download()
            # dl.parse_cover(uri)
            # dl.download_cover()
            print(f"第 {count} 行下载完毕")