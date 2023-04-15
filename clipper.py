import streamlink
import requests
import os
import time
import datetime
import threading
import os
import tempfile

class TwitchClipper:
    def __init__(self,channel,clippingRate,clipLength,aouth,quality="720p"):
        # global configuration
        self.oauth_token = aouth
        # user configuration
        self.username = channel
        self.clippingRate=clippingRate
        self.padding=1.5
        if(clipLength<10):
            clipLength=10
        self.clipLength=clipLength
        self.oldTime=0
        self.timeout=60
        self.quality = quality
        self.wantedQuality = quality
        self.online=False
        
        self.writing = []
        self.mutex=False
        self.session=None
        try:
            self.recorded_path=os.path.join("temp", self.username)
            if( not os.path.exists(self.recorded_path) ):
                os.makedirs(self.recorded_path)
        except:
            self.recorded_path=tempfile.TemporaryDirectory()
        print("clipper for {} started with quality {}".format(self.username,self.quality) )
        # self.startSession()

    def appendFile(self,filepath):
        while self.mutex:
            time.sleep(0.01)
        self.mutex = True
        self.writing.append(filepath)
        self.mutex = False

    def popFile(self,filepath):
        while self.mutex:
            time.sleep(0.01)
        self.mutex = True
        if( filepath in self.writing):
            index = self.writing.index(filepath)
            self.writing.pop(index)
        self.mutex = False

        
    def startSession(self):
        self.session = streamlink.Streamlink()
        self.session.set_option("http-headers", "Authorization=OAuth {}".format(self.oauth_token))
        self.session.set_option("hls-duration", self.clipLength )
        self.session.set_option("hls-segment-stream-data", True )
        self.session.set_option("hls-live-edge", 2 )        
        self.session.set_option("stream-timeout",10)

    def isLiveQuery(self):
        HEADERS = { 'client-id' : 'kimne78kx3ncx6brgo4mv6wki5h1ko' }
        GQL_QUERY = """ query($login: String) {user(login: $login) {stream {id}}}"""
        QUERY = { 'query': GQL_QUERY, 'variables': {'login': self.username} }
        response = requests.post('https://gql.twitch.tv/gql', json=QUERY, headers=HEADERS)
        dict_response = response.json()
        try:
            return True if dict_response['data']['user']['stream'] is not None else False
        except:
            return False

    def isLiveReq(self):
        contents = requests.get('https://www.twitch.tv/' +self.username).content.decode('utf-8')
        return  'isLiveBroadcast' in contents

    def isOnline(self):
        req=False
        query =True
        while ( req != query):
            query = self.isLiveQuery()
            req= self.isLiveReq()
        online=req
            
        if(online != self.online):
            self.online = online
            status = "Online"
            if( online):
                self.startSession()
            else:
                status = "Offline"
                del self.session
                self.session=None

            print("Clipper : Streamer {} is now {}".format(self.username,status) )
            self.quality=self.wantedQuality
        if(online and self.session==None):
            self.startSession()
        return online
    
    def startClip(self):
        if(not self.online):
            return "-1"     
              
        qualities = [self.quality]
        if( self.quality !="best"):
            if(not "p60" in self.quality):
                qualities.append( self.quality+"60")
            qualities.append( "best")
        recorded_filename="-1"
        streams=None 
        
        try:
            streams = self.session.streams(f"https://www.twitch.tv/{self.username}")         
        except:
            return "-1"
        # print("--") 
        for quality in qualities:
            try:
                stream = streams[quality]
                fd = stream.open()
            except:
                continue 
            if(self.quality!= quality ):
                self.quality = quality
                print("clipper of {} switched to quality {}".format( self.username,self.quality))
            recorded_filename, duration = self.saveStream(fd)
            # duration = self.get_length(recorded_filename)
            if( duration < self.clipLength/2 ):
                print(self.username,"clip was cut off, length {} instead of {}".format(duration,self.clipLength) )
                self.deleteFile(recorded_filename) 
                recorded_filename="-1"
            break

        del streams   
        return recorded_filename
            
    def saveStream(self,fd):
        filename = datetime.datetime.now().strftime("%m-%d-%Y %H-%M-%S") + ".mp4"
        filename = "".join(x for x in filename if x.isalnum() or x in [" ", "-", "_", "."])
        recorded_filename = os.path.join(self.recorded_path ,filename)
        self.appendFile(recorded_filename)
        with open(recorded_filename, "wb") as f:
            start=time.time()
            while self.online:
                try:                 
                    data = fd.read(124)
                    duration = time.time( )-start
                    if (  duration > self.clipLength ) or not data:
                        break
                    f.write(data)
                except:
                    duration = 0
                    break
            f.close()
            fd.close()
            del fd
        self.popFile(recorded_filename)
        return recorded_filename,duration
    
    def deleteFile(self,path):
        try:
            if(os.path.isfile(path)):
                os.remove(path)
        except:
            return

    def getNearestClip(self,timestamp,positionInClip=0.5):
        length= self.clipLength
        t=timestamp.timestamp()
        folderPath = os.path.join(self.recorded_path)
        timediffs=[]    
        names=[]
        timeinclip=[]
        lengths=[]
        for path in os.listdir(folderPath):
            filepath = os.path.join(folderPath, path)
            if os.path.isfile(filepath):
                filestart =datetime.datetime.strptime(  path.replace(".mp4","")  , "%m-%d-%Y %H-%M-%S").timestamp()
                # length = self.get_length(filepath)
                fileend=filestart+length
                if( t>filestart+self.padding and t<fileend-self.padding):
                    timediff=abs(  filestart +self.padding + ( length -2*self.padding) *positionInClip -t )
                    names.append(filepath)
                    timediffs.append(timediff)
                    timeinclip.append( t-filestart)
                    lengths.append( length)

        if(len(names)==0):
            return None
        
        indx = timediffs.index(min(timediffs))
        print("{} file found, poisiton in clip {}/{} in file {}".format(self.username,timeinclip[indx],lengths[indx],names[indx]) )
        return names[indx]
    def mkdir(self,folderPath):
        if(not os.path.isdir(folderPath)):
            os.mkdir(folderPath)
            
    def loop(self):
        while True:
            if( not self.loopOnce()):
                time.sleep(0.5)

    def loopOnce(self):
        currTime= time.time()
        if( self.isOnline() ):
            if( int(currTime-self.oldTime)>=int(self.clippingRate) ):
                # print("new clip")
                # print("new clip delta {} vs rate {}".format( int(currTime-self.oldTime),int(self.clippingRate) ) )
                self.oldTime =currTime
                threading.Thread(target=self.startClip).start()
                return True
            
        folderPath= self.recorded_path
        # folderPath = os.path.join(self.recorded_path)
        # self.mkdir(folderPath)
        curr= datetime.datetime.now()
        for path in os.listdir(folderPath):
            filepath = os.path.join(folderPath, path)
            if os.path.isfile(filepath):
                filetime =datetime.datetime.strptime(  path.replace(".mp4","")  , "%m-%d-%Y %H-%M-%S")
                timediff=(curr-filetime).total_seconds()
                if(timediff>self.timeout ):
                    self.deleteFile(filepath) 
        return False
