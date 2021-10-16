import urllib.error
import urllib.request
import json
import re
import os
import sys
import html

BASE_URL = {
    'SONG_BASE': 'https://node.kg.qq.com/play?s=%s',
    'UGC_BASE': 'https://node.kg.qq.com/cgi/fcgi-bin/kg_ugc_get_homepage?jsonpCallback=callback_0&outCharset=utf-8&type=get_ugc&start={0}&num=8&share_uid={1}',
    }

RE_PATTERNS = {
    'song': re.compile(r'^(http://|https://|)node.kg.qq.com/play'),
    'user': re.compile(r'^(http://|https://|)node.kg.qq.com/personal'),
    'playlist': re.compile(r'^(http://|https://|)node.kg.qq.com/personal'),
    }

CURR_DIR = os.path.dirname(sys.argv[0])
DOWNLOAD_FOLDER = os.path.join(CURR_DIR, 'Downloads')

def init():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.mkdir(DOWNLOAD_FOLDER)
    

def matchUrl(url):
    '''
    parse the url and decide the logic to extract info
    @return <int>: 1 if a single song; 2 if a user; 3 if playlist
    '''
    if RE_PATTERNS['song'].match(url):
        return 1
    if RE_PATTERNS['user'].match(url):
        return 2
    if RE_PATTERNS['playlist'].match(url):
        return 3

def getSongInfo(shareid):
    '''
    @param shareid: the song id in url
    '''
    song_url = BASE_URL['SONG_BASE'] % shareid
    try:
        request = urllib.request.urlopen(song_url)
    except urllib.error.URLError as e:
        print('cannot connect to Internet, check connection')
        exit()
        
    html = request.read().decode('utf-8')
    data = getWindowData(html)
    return data


def getWindowData(htmlcontent):
    '''
    extract json data of the webpage
    @param html <str>: the raw html text to extract
    @return <dict>
    '''
    try:
        windowData_text = html.unescape(re.search(r'(?<=window\.__DATA__ =).+(?=;\s\<\/script\>)', htmlcontent).group())
        windowData = json.loads(windowData_text)
        
    except json.decoder.JSONDecodeError:
        raise Exception('cannot parse website data')
    return windowData


def getShareids(uid, ugc_total_count):
    '''
    
    '''
    shareid_list = []
    for i in range(1, ugc_total_count+1):
        url = BASE_URL['UGC_BASE'].format(i, uid)
        request = urllib.request.urlopen(url)
        html = request.read().decode('utf-8')
        ugclist = json.loads(html[11:-1])['data']['ugclist']
        for entry in ugclist:
            shareid_list.append(entry['shareid'])
    return shareid_list

def downloadSong(data):
    '''
    
    '''
    print('Downloading...')
    resource_url = data['detail']['playurl']
    filename = '%s - %s.m4a' % (data['detail']['nick'],
                                    data['detail']['song_name'])
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    urllib.request.urlretrieve(resource_url, file_path)
    print('Finished.')
    print('File saved at %s' % file_path)


def exit():
    '''
    wait for user input and exit the program
    '''
    input('Press enter to exit...')
    quit()

def main():
    '''
    entry
    '''
    init()
    url = input('请输入歌曲 URL : ')
    url = re.sub(r'\s', r'', url)
    url_type = matchUrl(url)
    if url_type == 1:
        shareid = re.search(r'(?<=play\?s\=)([^&]*)', url).group()
        data = getSongInfo(shareid)
        
        print('找到以下歌曲:')
        print('='*48)
        print('曲名   : %s' % data['detail']['song_name'])
        print('歌手昵称: %s' % data['detail']['kg_nick'])
        print('原唱   : %s' % data['detail']['singer_name'])
        print('='*48)

        cmd = input('输入 Y 并换行开始下载，输入 N 换行退出\n')
        if cmd == 'Y':
            downloadSong(data)
        exit()
        return 0
    
    if url_type == 2:
        try:
            request = urllib.request.urlopen(url)
        except urllib.error.URLError as e:
            print('cannot connect to Internet, check connection')
            exit()
        html = request.read().decode('utf-8')
        data = getWindowData(html)
        count = int(data['data']['ugc_total_count'])
        
        print('找到以下歌手:')
        print('='*48)
        print('昵称   : %s' % data['data']['nickname'])
        print('歌曲数量: %d' % count)
        print('='*48)

        cmd = input('输入 Y 并换行下载所有歌曲，输入 N 换行退出\n')
        if cmd == 'Y':
            uid = re.search(r'(?<=uid=).+&*', url).group()
            shareids = getShareids(uid, count)
            for shareid in shareids:
                data = getSongInfo(shareid)
                downloadSong(data)
        exit()

if __name__ == '__main__':
    main()
    
