import os
import json

import requests



class Downloader:
    DOWNLOAD_PATH = "downloads"
    TEXT_BEFORE_JSON = "window.__DATA__ = "
    TEXT_AFTER_JSON = "; </script>"

    def __init__(self, download_path=None):
        if download_path:
            self.download_path = download_path
        else:
            self.download_path = self.DOWNLOAD_PATH
        self.data = {}

    def parse(self, uri):
        print("Parsing {0}...".format(uri))
        response = requests.get(uri)
        content = response.text

        start_idx = content.find(self.TEXT_BEFORE_JSON)
        content = content[start_idx+len(self.TEXT_BEFORE_JSON):]

        end_idx = content.find(self.TEXT_AFTER_JSON)
        content = content[:end_idx]

        self.data = json.loads(content)
        
        playurl = self.data.get("detail").get("playurl")
        song_name = self.data.get("detail").get("song_name")
        print("Found song \"{0}\" with playurl: {1}".format(song_name, playurl))
        
    def download(self):
        playurl = self.data.get("detail").get("playurl")
        song_name = self.data.get("detail").get("song_name")
        
        print("Downloading...")
        response = requests.get(playurl)
        with open(os.path.join(self.download_path, song_name+".m4a"), "wb") as f:
            f.write(response.content)
        print("Finished.")
        
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="KG Downloader")
    parser.add_argument("url", type=str, help="the URI of the song page")

    args = parser.parse_args()

    if not args.url:
        parser.error("Please provide a URL using --url")

    uri = args.url
    
    dl = Downloader()
    dl.parse(uri)
    dl.download()
