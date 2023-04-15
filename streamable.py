from pystreamable import StreamableApi
import requests
import time 
class streamableUploader:
    def __init__(self,name,password) -> None:
        self.name=name
        self.password=password
        self.api=StreamableApi(name, password)

    def uplaodFile(self,filePath,videoTitle):
        info = self.api.upload_video(filePath, videoTitle)
        return info["shortcode"]

    def waitForUpload(self,url):
        while True:
            x = requests.get(url)
            txt= x.text
            if("<h1>Processing Video</h1>\n<p>We\'ll refresh this page when it\'s ready.</p>" in txt):
                # print("Processing Video")
                time.sleep(1)
            else:
                print("Video done processing")
                return
        