from operator import truediv
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
    newPortNumber = 11083 

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
    print(commandParts)
    # if valid command proceed
    if(commandParts[0].lower() not in VALIDCMDS):
        print(commandParts[0].lower(), "is not a recognized command")

    # if valid command, execute command
    # msg [m, msg]
    if((commandParts[0].lower() == VALIDCMDS[0]) or (commandParts[0].lower() == VALIDCMDS[1])):
        print('send message')

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
        runFlag = False

# kill all sockets/threads