from streamable import streamableUploader
from imgur import imgur

class uploader:
    def __init__(self,streamableLogin,streamablePass,imgurClient) -> None:
        self.streamableLogin=streamableLogin
        self.streamablePass=streamablePass
        self.imgurClient=imgurClient
        self.imgur = imgur(clientID=self.imgurClient)
        self.streamable = streamableUploader(streamableLogin,streamablePass)

    def uploadFile(self,videoTitle):
        try:
            url = self.imgur.uploadFile(videoTitle)
            return url
        except Exception as e:
            print("couldnt use imgur",str(e))
            url = self.streamable.uploadFile(videoTitle)
            self.streamable.waitForUpload(url)
            return url