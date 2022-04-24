from asyncio.windows_events import NULL
from operator import length_hint, truediv
import sys 
from urllib.request import DataHandler
from requests import get
from os.path import exists

# other impots
# json files
import json
# command parsing to preserve substrings
import shlex

#######################################################################################################################################################

# supported instructions:
#   h                                                           = explanation + show commands
#   m [ip:optional port] [message type] ['message'] ['key']     = send message
#   v                                                           = 

VALIDCMDS = ['m', 'msg', 'v', 'view', 's', 'settings', 'h', 'help', '?', 'q', 'quit', 'e', 'exit']

# type of content that can be sent
# -f = file; specify a file path in the next parameter
# -m = text; specify plain text in the next parameter
VALFMT = ['-f', '-t']

# default port used by listening socket
DFTPORT = 11083

#######################################################################################################################################################

# code from https://www.ipify.org/
def getPublicIP():
    return get('https://api.ipify.org').text

def newPort():
    print("Enter a new port to recieve messages on:")
    portFlag = True
    while(portFlag):
        newPortNum = input()
        #discard non numeric input
        alphaPort = newPortNum.isnumeric()
        if(alphaPort == False):
            print('Ports can not contian characters!')
        else:
            # invalid port range
            if(int(newPortNum) < 1024 or int(newPortNum) > 65535):
                print('Ports can be between 1023 and 65535')
            else:
                print('New port number is', newPortNum)
                portFlag = False

    # return new port number
    return newPortNum

# first time setup
def firstTimeSetup():
    #begin setup
    print('Please enter your nickname:')
    nick = input()
    print('Would you like to recieve messages on the default port (11083)?')
    newPortNumber = DFTPORT 

    # get response
    portResponse = input()
    if(portResponse != 'y' and portResponse != 'yes'):
        newPortNumber = newPort()

    # json struct for user info
    userInfo = {
        "name" : nick,
        "defaultPort" : newPortNumber
    }

    # write port and name to settings
    with open('settings.json', 'w') as f:
        json.dump(userInfo, f)

# check that IP address provided is valid
def ipCheck(ipAddress):
    subBlocks = ipAddress.split('.')
    # bad IP if not exactly 4 blocks
    if(length_hint(subBlocks) != 4):
        return False
    for block in subBlocks:
        if(not str(block).isnumeric() or int(block) > 255):
            return False
    
    # if valid return true
    return True

# check that the provided port is valid
def portCheck(portnumber):
    if(not str(portnumber).isnumeric()):
        return False
    if(int(portnumber) > 65535 or int(portnumber < 1024)):
        return False
    return True


#######################################################################################################################################################

# do not run setup if settings file exists
# https://www.pythontutorial.net/python-basics/python-check-if-file-exists/
if(exists('settings.json') == False):
    firstTimeSetup()

# get data from settings
f = open('settings.json')
userInfo = json.load(f)
f.close()

# save name and current port for display purposes
name = userInfo['name']
currentPort = userInfo['defaultPort']

# display current public IP and defined port
print('welcome ' + name + '!')
print('\tYour Public IP is:', getPublicIP())
print('\tCurrently receiving on port:', currentPort)
print('##########################################\n')

# create listening socket on its own thread here



# begin main program
runFlag = True
while(runFlag):
    # check to see if listening socket has anything 
    inputstring = str(input(name + "> "))

    # split input at spaces to get command + arguments
    commandParts = shlex.split(inputstring)
    #print(commandParts)

    # if valid command proceed
    if(commandParts[0].lower() not in VALIDCMDS):
        print(commandParts[0].lower(), " is not a recognized command")

    # if valid command, execute command
    # msg [m, msg]
    if((commandParts[0].lower() == VALIDCMDS[0]) or (commandParts[0].lower() == VALIDCMDS[1])):
        # msg needs 4 or 5 arguments; stop processing if not met
        numArg = length_hint(commandParts)
        if(numArg > 5 or numArg < 4):
            print(inputstring + ' is not a valid "m" command')
            continue;

        # break up destination information
        destInfo = str(commandParts[1]).split(':')
        ipArgs = length_hint(destInfo)

        # stop if bad input
        if(ipArgs > 2):
            print('Invalid IP:Port combination.')
            continue;

        # stop if invalid IP address
        if(not ipCheck(str(destInfo[0]))):
            print(destInfo[0] + ' is not a valid IP address')
            continue;

        # if valid, see if there is a port and check if it is valid
        if(ipArgs == 2):
            if(not portCheck(destInfo[1])):
                print(destInfo[1] + ' is not a valid port number')
                continue;

        # check type of message
        msgFmt = commandParts[2].lower()
        if(msgFmt not in VALFMT):
            print(commandParts[2] + "is not a valid argument for the type of content to send")

        # handle -t = text
        fileExt = NULL
        if(msgFmt == '-t'):
            print('text input')
        if(msgFmt == '-f'):
            print('fileInput')

    # view [v, view]
    if((commandParts[0].lower() == VALIDCMDS[2]) or (commandParts[0].lower() == VALIDCMDS[3])):
        print('view messages')

    # settings [settings, s]
    if((commandParts[0].lower() == VALIDCMDS[4]) or (commandParts[0].lower() == VALIDCMDS[5])):
        print('change settings')

    # help [h, help, q]
    if((commandParts[0].lower() == VALIDCMDS[6]) or (commandParts[0].lower() == VALIDCMDS[7]) or (commandParts[0].lower() == VALIDCMDS[8])):
        print('change settings')

    # quit [q, quit, e, exit]
    if((commandParts[0].lower() == VALIDCMDS[9]) or (commandParts[0].lower() == VALIDCMDS[10]) or (commandParts[0].lower() == VALIDCMDS[11]) or (commandParts[0].lower() == VALIDCMDS[12])):
        # kill the program
        runFlag = False

# kill all sockets/threads after this point