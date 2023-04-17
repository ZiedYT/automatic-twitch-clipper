
import socket
import time
import re
import datetime
import select


class twitchChat:
    server = 'irc.chat.twitch.tv'
    port = 6667
    
    def __init__(self,name,token,channel) -> None:
        self.nickname=name
        self.token=token
        self.channel=channel
    
        while True:
            try:
                self.connect()
                break
            except:
                print("reconnecting")
                time.sleep(1)

        print("chat bot started",channel )
        self.lastPing = time.time()
        self.reping = 180
    def close(self):
        self.soc.close()
    def connect(self):
        self.soc = socket.socket()
        self.soc.connect((self.server, self.port))
        # self.port+=1
        self.soc.send(f"PASS {self.token}\n".encode('utf-8'))
        self.soc.send(f"NICK {self.nickname}\n".encode('utf-8'))
        self.soc.send(f"JOIN {self.channel}\n".encode('utf-8'))
        self.pong()
        # rev= self.soc.recv(2048)
        # response = rev.decode("utf-8")
        # print(response)

    def pong(self):
        self.soc.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        self.lastPing = time.time() 

    def sendMsg(self,msg):
        try:
            print("sending msg",self.channel,msg)
        except:
            print("sending msg",self.channel)
        self.soc.send("PRIVMSG {} :{}\r\n".format(self.channel, msg ).encode("utf-8"))

    def recv_timeout(self, sock, bytes_to_read, timeout_seconds):
        sock.setblocking(0)
        ready = select.select([sock], [], [], timeout_seconds)
        if ready[0]:
            return sock.recv(bytes_to_read)
        # raise socket.timeout()

    def flush(self):
        try:
            # rev= self.soc.recv(2048)
            rev = self.recv_timeout(self.soc, 2048, 10)
            if(rev==None):
                return None
            print(type(rev))
            if b"PING :tmi.twitch.tv\r\n" in rev:
                self.pong()
        except Exception as e:
            try:
                print(self.channel,str(e) )
                if("that is not a socket" in str(e)):
                    self.soc = socket.socket()
                else:
                    self.soc.close()
                self.connect()
            except:
                pass

    def spinOnce(self):
        try:
            if(  time.time()-self.lastPing >self.reping):
                self.pong()
            # rev= self.soc.recv(2048)
            rev = self.recv_timeout(self.soc, 2048, 10)
            if(rev==None):
                return None
            # response = rev.decode("utf-8")
            if b"PING :tmi.twitch.tv\r\n" in rev:
                self.pong()
            else:
                responses=rev.split(b"\n")
                return responses
            
        except Exception as e:
            try:
                print(self.channel,str(e) )
                if("that is not a socket" in str(e)):
                    self.soc = None
                    self.soc = socket.socket()
                elif(self.soc==None):
                    self.soc = None
                    self.soc = socket.socket()
                else:
                    self.soc.close()
                    self.soc = None
                    self.soc = socket.socket()

                self.connect()
            except:
                pass
            #print("reconnecting")
            #self.connect()
        return ""
    

# msgDetector gets active if one scenario is active
# a scenario gets active if ALL OF its counters are active (count == thresh)
# counter gets +1 count if one combination is valid
# a combination is valid if all includes are within a msg 
class msgDetector:
    def __init__(self,title,scenarios,channel,msg=None,positionInClip=0.5) -> None:
        self.channel=channel
        self.instances=[]
        self.title= title
        self.run=True
        self.msg=msg
        self.positionInClip=positionInClip
        self.uploading=False

        self.scenarios=scenarios
        for scenario in self.scenarios:
            for counter in scenario:
                counter["activations"]={}
        # print(title)

    def spinOnce(self,lines):    
        if(not self.run):
            return False
        for resbytes in lines:
            try:
                res=resbytes.decode("utf-8")
                # print(res)
                username = re.search(r"\w+", res).group(0).lower()
                CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
                message = CHAT_MSG.sub("", res).rstrip('\n')
                # message=message.rstrip(b'\r')
                messageBytes = resbytes.split("{} :".format(self.channel).encode() )[-1][:-1]
                msgSTR = messageBytes.decode("utf-8")
                msgSTRparts = msgSTR.lower().split(" ") 
                messageBytesparts  = messageBytes.split(" ".encode() ) 
                t= datetime.datetime.now()
                for scenario in self.scenarios:
                    for counter in scenario:
                        combinations = counter["combinations"]
                        users = counter.get("users",None)
                        if(users!=None):
                            if(not username in users):
                                continue

                        for combination in combinations:
                            words= combination["include"]
                            lock = combination["caseSensitive"]
                            exclude = None
                            exclude = combination.get("exclude",[])

                            add= True 
                            for word in exclude:
                                if( not lock):
                                    if( word.lower() in msgSTRparts  ):
                                        add=False
                                        break
                                else:
                                    if( word.encode() in messageBytesparts  ):
                                        add=False
                                        break
                            if(add):                
                                for word in words:
                                    if( not lock):
                                        if( not word.lower() in msgSTRparts  ):
                                            add=False
                                            break
                                    else:
                                        if(not  word.encode() in messageBytesparts  ):
                                            add=False
                                            break
                            if(add):
                                counter["activations"][username]=t
                                # counter["activations"].append(t)
                                print(self.channel,t,self.title.encode(),counter["name"].encode(),"new instance, {} total".format(len(counter["activations"])) )
            except:
                pass

    def isActive(self):
        self.cleanOld()
        if(not self.run):
            return False
        self.instances=[]
        valids=[]
        for scenario in self.scenarios:
            # print("-----------")
            valid=True
            for counter in scenario:
                activations = counter["activations"]
                thresh =  counter["thresh"]

                if(thresh> len(activations) ):
                    valid =False
                    break

            valids.append(valid)
            # print(valid)

        times=[]
        timestamps=[]
        positions=[]
        for valid, scenario in zip(valids,self.scenarios):
            if(not valid):
                continue
            
            ts =[]
            stamps=[]
            position=self.positionInClip
            for counter in scenario:
                position = counter.get("positionInClip",position)
                activationTimes = [counter["activations"][username] for username in counter["activations"]]
                activationTimestamps = [temp.timestamp() for temp in activationTimes]
                indx = activationTimestamps.index(min(activationTimestamps))
                ts.append( activationTimes[indx] )
                stamps.append( activationTimestamps[indx] )

            indx = ts.index(max(ts)) #use the counter that was activated the last
            times.append(ts[indx] )
            timestamps.append( stamps[indx])
            positions.append(position)

        if(True in valids): 
            index = timestamps.index( min(timestamps) ) # use the first active scenario
            # self.instances=[  ]
            return True, times[index], positions[index]
        
        return False,0,0


    def cleanAll(self):
        for scenario in self.scenarios:
            for counter in scenario:
                counter["activations"]={}

    def cleanOld(self):
        now = datetime.datetime.now()
        for scenario in self.scenarios:
            for counter in scenario:
                windowSize =  counter["windowSize"]
                cleaned =False
                while not cleaned:
                    cleaned=True
                    for username in counter["activations"]:
                        t = counter["activations"][username]
                        if (now-t).total_seconds()>windowSize:
                            cleaned=False
                            counter["activations"].pop(username)
                            break