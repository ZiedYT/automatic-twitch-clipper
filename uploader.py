from streamable import streamableUploader
from imgur import imgur

class uploader:
    def __init__(self,streamableLogin,streamablePass,imgurClient) -> None:
        self.streamableLogin=streamableLogin
        self.streamablePass=streamablePass
        self.imgurClient=imgurClient
        self.imgur = imgur(clientID=self.imgurClient)
        self.streamable = streamableUploader(streamableLogin,streamablePass)

    def uploadFile(self,filePath,videoTitle,parent=""):
        try:
            url = self.imgur.uploadFile(filePath,videoTitle)
            return url
        except Exception as e:
            print("couldnt use imgur",str(e))
            url = self.streamable.uploadFile(filePath,videoTitle)
            self.streamable.waitForUpload(url)
            return url