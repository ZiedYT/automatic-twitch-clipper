from chat import twitchChat,msgDetector
from clipper import TwitchClipper
from drive import drive
import time
import threading
from pathlib import Path
import os
import datetime
import pytz
import json
import glob

import shutil
try:
    shutil.rmtree("temp")
except:
    pass

class autoClipperClass:
    def __init__(self,twitchUser,chatToken, chatChannel, googleToken,recorderaouth,streamChannel=None,clippingRate=3,clipLength=13,timeZone=None,msgPosting=1,msgPause=3.5,quality="720p",msgEnding=" (automated) MrDestructoid ",spamChar="⠀"):
        self.twitchUser= twitchUser
        self.chatToken = chatToken
        self.chatChannel=chatChannel
        self.streamChannel=streamChannel
        self.recorderaouth = recorderaouth
        if(streamChannel==None):
            self.streamChannel = chatChannel


        self.clipLength=clipLength
        self.clippingRate=clippingRate
        self.timeZone=timeZone
        self.detectors=[]
        self.msgPosting=msgPosting
        self.msgPause = msgPause
        self.uploader = drive(googleToken)
        self.running = True        
        self.quality = quality
        self.msgEnding= msgEnding
        self.spamChar=spamChar
        self.chatBot=None
        self.start()

    def start(self):
        if(self.chatBot !=None):
            self.chatBot.close()
            self.chatBot=None
            
        self.chatBot =twitchChat(self.twitchUser,self.chatToken,"#"+self.chatChannel)
        # self.chatBot.sendMsg("test123")
        self.recorder=  TwitchClipper(channel=self.streamChannel,clippingRate=self.clippingRate,clipLength=self.clipLength,aouth=self.recorderaouth,quality=self.quality)
        self.linesCount=0
        self.lastRun=time.time()
        # self.chatBot.sendMsg("test")

    def addDetector(self,title,scenarios,msg=None,positionInClip=0.5,folder=None):
        if(folder==None):
            folder= self.chatChannel
        detector = msgDetector(title,scenarios,channel=self.chatChannel,msg=msg,positionInClip=positionInClip,folder=folder)
        self.detectors.append(detector)

        
    def loopOnce(self):
        lines=None
        lines= self.chatBot.spinOnce()

        try:
            self.recorder.loopOnce()
        except Exception as e: 
            print("### recorded errror at",self.streamChannel,str(e))
            time.sleep(0.1)
            return
        
        if(lines==None):
            return
        self.linesCount= (self.linesCount+len( lines ))%10000

        if(not self.recorder.online):
            time.sleep(0.1)
            return

        for detector in self.detectors:
            if(not detector.run):
                return
            # detector: msgDetector=detector
            detector.cleanOld()
            detector.spinOnce(lines)
            active,timestamp,position= detector.isActive()
            if(active):
                if(detector.run):
                    detector.run=False
                    threading.Thread(target=self.upload, args=(detector,timestamp,position,)).start()
        

    def getTime(self):
        timeZone = pytz.timezone(self.timeZone)
        loc_dt  = datetime.datetime.now(timeZone)
        fmt = '%Y-%m-%d %H:%M:%S'
        return loc_dt.strftime('%Y:%m:%d %H:%M:%S %Z %z')

    def upload(self,detector,timestamp,position):
        print("starting upload thread for",self.chatChannel,"position",position)
        print("--------")
        T=self.getTime()
        # detector:msgDetector=detector
        # timestamp=detector.instances[0]
        file = self.recorder.getNearestClip(timestamp,position)
        if(file!=None):
            filename  = Path(file).name
            detector.uploading=True
            recorderPath = os.path.join( "temp", self.streamChannel )
            relFile = os.path.join( recorderPath,  filename )
            while ( file in self.recorder.writing or  filename in self.recorder.writing or  relFile in self.recorder.writing  ):
                time.sleep(0.01)
            time.sleep(1)
            print(detector.title.encode(),"detected at timestamp",timestamp,"Will start uploading")
            title = detector.title
            title+=" "+T+" automated by ZiedYT"
            try:
                url = self.uploader.uploadFile(file,title,detector.folder)
                # self.uploader.waitForUpload(url)
                if(detector.msg!=None):
                    tosend= detector.msg +" "+url+self.msgEnding
                    lastcount=self.linesCount-10

                    for i in range(self.msgPosting):
                        start = time.time()
                        now= time.time()
                        cond = (self.linesCount-lastcount>5) or (self.linesCount < lastcount-500)

                        while ( not cond ):
                            print("sleeping")
                            time.sleep(0.5)
                            now= time.time()
                            cond = (self.linesCount-lastcount>5) or (self.linesCount < lastcount-500)
                            if( now-start>=self.msgPause):
                                break

                        print("self.linesCount",self.linesCount,"lastcount",lastcount)
                        if( cond ):
                            self.chatBot.sendMsg(tosend)
                            tosend+=self.spamChar                      
                            # if(self.msgPosting -i >1):
                            now= time.time()
                            if(  now< start+self.msgPause ):
                                time.sleep( (start+self.msgPause) -now )
                            lastcount=self.linesCount         
            except Exception as e:
                print(str(e))

        else:
            print("no file")
        time.sleep(4)
        detector.cleanAll()
        detector.uploading=False
        detector.run=True

    def run(self):
        print("launched stream:{} chat:{}".format(self.streamChannel,self.chatChannel))
        while self.running:
            self.loopOnce()
        print("closing",self.chatChannel)
        self.chatBot.soc.close()

    def summary(self):
        summary ={"stream": self.streamChannel,"chat":self.chatChannel,"status":self.recorder.online }
        summary["detectors"]=[]
        for detector in self.detectors:
            detectorData={}
            # detector:msgDetector=detector
            detectorData["name"]=detector.title
            detectorData["msg"]=detector.msg
            detectorData["uplaoding"]=detector.uploading
            detectorData["scenarios"]=[]
            ind=-1
            for scenario in detector.scenarios:
                ind+=1
                scenarioData={}
                scenarioData["index"]=ind
                scenarioData["counters"]=[]
                for counter in scenario:
                    counterData={}
                    last="-----"
                    if( len(counter["activations"])>0 ):
                        activationTimes = [counter["activations"][username] for username in counter["activations"]]
                        activationTimestamps = [temp.timestamp() for temp in activationTimes]
                        indx = activationTimestamps.index(max( activationTimestamps ))
                        last=activationTimes[indx].strftime("%Y-%m-%d %H:%M:%S")

                    thresh= str(counter["thresh"])
                    count= str(len(counter["activations"]))

                    counterData["name"]=counter["name"]
                    counterData["count"]="{}/{}".format(count,thresh)
                    counterData["last"]=last

                    scenarioData["counters"].append(counterData)
                detectorData["scenarios"].append(scenarioData)
            summary["detectors"].append(detectorData)
            

        return summary

class mainApp:
    def __init__(self):
        self.clippers=[]
        print(datetime.datetime.now() )
        self.loadCredentials()
        # if( os.path.isfile("token.json") ):
        #     self.uploader = drive()
        #     print("using google drive")
        # else:
        #     self.uploader =streamableUploader(self.cred["streamableLogin"],self.cred["streamablePass"])
        #     print("using streamable")
        # self.uploader=uploader(self.cred["streamableLogin"],self.cred["streamablePass"],self.cred["imgurClinetID"] )

        for file in glob.glob("channels/*.json"):
            channel = os.path.basename(file).replace(".json","")
            add = self.cred.get(channel,None)
            if (add==None):
                if(channel in os.environ):
                    add= self.isdefined(channel)
            if(add):
                self.loadJson(file)

        for clipper in self.clippers:
            threading.Thread(target=clipper.run, ).start()

    def loadCredentials(self):
        self.cred={}
        path="secrets.json"
        parts=["streamableLogin","streamablePass","chatToken","recorderaouth","clipperChannel","imgurClinetID"]
        unasigned=["your_streamable_email","your_streamable_password","your_chat_token","your_twitch_stream_aouth","your_twitch","your_imgur_client"]
        if( os.path.isfile(path) ):
            with open(path,"rb") as json_file:
                data = json.load(json_file) 
                self.cred=data

        for i in range(len(parts)):
            p=parts[i]
            default=unasigned[i]
            if(  self.cred.get(p,default) == default ):
                if( p in os.environ):
                    self.cred[p] = self.getVar(p)

    def getVar(self,name):
        try:
            return str(os.environ[name])
        except:
            return str(os.getenv(name))

    def summary(self):
        return [ clipper.summary() for clipper in self.clippers ]
    
    def isdefined(self,name):
        if( name in os.environ):
            return os.environ[name]=="True"
        return False

    def loadJson(self,path):
        if( os.path.isfile(path) ):
            with open(path,"rb") as json_file:
                data = json.load(json_file) 
                chatChannel = data["chatChannel"]

                streamChannel = data.get("streamChannel",chatChannel)
                timeZone = data["timeZone"]
                clippingRate = data["clippingRate"]
                clipLength = data["clipLength"]
                msgPosting = data["msgPosting"]
                detectors = data["Detectors"]
                msgEnding = data.get("msgEnding"," (automated) MrDestructoid ")
                quality = data.get("quality","720p")
                spamChar= data.get("spamChar","⠀")
                msgPause = data.get("msgPause",3.5)
                googleToken=data.get("googleToken","tokens/token")
                googleToken=googleToken.replace(".json","")

                clipper = autoClipperClass (  
                    twitchUser= self.cred["clipperChannel"], chatToken = self.cred["chatToken"],
                    chatChannel=chatChannel, streamChannel=streamChannel,googleToken=googleToken,
                    recorderaouth=self.cred["recorderaouth"],quality=quality,
                    timeZone=timeZone,clippingRate=clippingRate,
                    clipLength=clipLength,msgPosting=msgPosting,msgEnding=msgEnding,spamChar=spamChar,msgPause=msgPause
                )

                for detector in detectors:
                    title = detector["title"]
                    msg = detector["msg"]
                    # print(msg)
                    positionInClip = detector["positionInClip"]
                    scenarios = detector["scenarios"]
                    folder=detector.get("folder",chatChannel)
                    clipper.addDetector(title=title,scenarios= scenarios, msg=msg,positionInClip=positionInClip,folder=folder)

                json_file.close()
                self.clippers.append(clipper)

if __name__ == "__main__":
    app=mainApp()
    while True:
        time.sleep(0.01)

    print("quitting")
