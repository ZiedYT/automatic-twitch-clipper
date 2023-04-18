import requests
import json

class imgur:
    def __init__(self,clientID):
        self.clientID=clientID
    
    def uploadFile(self,path,videotitle,parent=""):
        url = "https://api.imgur.com/3/upload"
        payload = {
            'title': videotitle,
            'description': videotitle
        }
        payload['type'] = 'file'

        files = {'video': open(path, 'rb') }
        payload['disable_audio'] = 0
         
        headers = {
        'Authorization': 'Authorization: Client-ID {}'.format(self.clientID)
        }

        response = requests.request("POST", url, headers=headers, data = payload, files = files)
        response_data=json.loads(response.text) 
        link = response_data["data"]["mp4"] 
        print(response_data)
        if( link[-1]=="."):
            link=link[:-1]
        return link
    
    def waitForUpload(self,url):
        return