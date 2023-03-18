![logo](logo.png)

# 全民 K 歌下载器

## 用法

```
py .\scripts\kg-download.py "https://kg.qq.com/node/play?s=id-of-your-song-page"
```

## 免责声明

该软件仅供学习交流使用

使用该软件即代表同意下列条款：

- 用户可以自由选择是否适用本软件

- 因此软件造成的知识产权侵犯问题由用户承担

- 不得用于商业用途

## 原理

全民 K 歌网页版将所有歌曲页面所要用到的信息通过一条 Javascript tag 直接从服务器加载到前端的 `window.__DATA__` 变量中, 之后再由其他的 JS 脚本进行提取和渲染:

```html
<script type="text/javascript">window.__DATA__ = {...}; </script>
```

并且, 网页似乎没有采用反爬虫措施, Python 的 `requests.get()` 可以直接访问到所有信息.

因此, 我们只需要 parse 这条 JS tag 中的 JSON 格式信息, 直接加载为 Python 字典即可读取.

这里列举一些常用的 field:

```python
{
  "shareid": "",        # 页面链接
  "detail": {
    "cover": "",        # 歌曲封面 .jpg 文件链接，可直接下载
    "nick": "",         # 用户昵称
    "playurl": "",      # 歌曲 .m4a 文件链接，可直接下载
    "score": int,       # 歌曲得分
    "singer_name": "",  # 原唱歌手名称
    "song_name": "",    # 歌曲名称
  }
}
```
