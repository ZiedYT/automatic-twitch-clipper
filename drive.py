from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import os
import io
import mimetypes
import googleoauth
import requests
import time
class drive:
    def __init__(self,file) -> None:   
    # Set the API scopes
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        file=file.replace(".json","")
        # Set the credentials for the API
        self.creds = None
        if os.path.exists('{}.json'.format(file)):
            self.creds = Credentials.from_authorized_user_file('{}.json'.format(file), self.SCOPES)
        else:
            googleoauth.main('{}'.format(file))
        
    def getFolderID(self,folder):
        parent_folder_name = folder
        parent_folder_id = None

        # Check if the parent folder exists
        query = f"name='{parent_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = self.service.files().list(q=query, fields='files(id)').execute()
        if len(response['files']) > 0:
            # Parent folder exists, get the ID
            parent_folder_id = response['files'][0]['id']
        else:
            # Parent folder doesn't exist, create it and get the ID
            file_metadata = {'name': parent_folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
            parent_folder = self.service.files().create(body=file_metadata, fields='id').execute()
            parent_folder_id = parent_folder.get('id')

        return parent_folder_id
    
    def uploadFile(self,file_path,title,parentfolder="clips"):
        self.service = build('drive', 'v3', credentials=self.creds)
        parent_folder_id= self.getFolderID(parentfolder)
        file_metadata = {'name': title, 'parents': [parent_folder_id]}

        # Set the media file
        media = io.BytesIO(open(file_path, 'rb').read())
        media_mime = mimetypes.guess_type(file_path)[0]
        if media_mime is None:
            media_mime = 'application/octet-stream'
        media = MediaIoBaseUpload(media, mimetype=media_mime, chunksize=1024*1024, resumable=True)

        # Upload the video to Google Drive
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        # print(f'Video uploaded with ID: {file.get("id")}')

        # Set the folder and video to be public
        folder_permission = {'type': 'anyone', 'role': 'reader', 'allowFileDiscovery': True}
        self.service.permissions().create(fileId=parent_folder_id, body=folder_permission).execute()
        video_permission = {'type': 'anyone', 'role': 'reader'}
        self.service.permissions().create(fileId=file.get('id'), body=video_permission).execute()
        url = "https://drive.google.com/file/d/{}/view".format(file.get("id"))
        self.waitForUpload(url)
        return url
    
    def waitForUpload(self,url):
        start = time.time()
        while time.time()-start<5:
            x = requests.get(url)
            txt= x.text
            if(not (("YouTube Video Player" in txt) or ("https://lh3.googleusercontent.com/drive-viewer" in txt )  or ("drive-viewer-video-player-object-0" in txt)) ):
                print("Processing Video")
                time.sleep(1)
            else:
                print("Video done processing")
                return
        