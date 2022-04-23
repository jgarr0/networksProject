from operator import truediv
import sys 
from urllib.request import DataHandler
from requests import get
from os.path import exists
import json

#######################################################################################################################################################

# supported instructions:
#   h                                       = explanation + show commands
#   m [ip:optional port] ["message"]        = send message
#   v                                       = 

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

name = userInfo['name']
currentPort = userInfo['defaultPort']

# create listening socket on its own thread here


# display current public IP and defined port
print('welcome ' + name + '!')
print('\tYour Public IP is:', getPublicIP())
print('\tCurrently receiving on port:', currentPort)
print('##########################################\n')

# begin main program
runFlag = True
while(runFlag):
    # check to see if listening socket has anything 
    inputstring = str(input(name + "> "))

    # split input at spaces to get command + arguments
    commandParts = inputstring.split()

    # if valid command proceed
    if(commandParts[0] not in VALIDCMDS):
        print(commandParts[0], "is not a recognized command")

    # if valid command, execute command
    # msg [m, msg]
    if((inputstring == VALIDCMDS[0]) or (inputstring == VALIDCMDS[1])):
        print(' send message')

    # view [v, view]
    if((inputstring == VALIDCMDS[2]) or (inputstring == VALIDCMDS[3])):
        print('view messages')

    # settings [settings, s]
    if((inputstring == VALIDCMDS[4]) or (inputstring == VALIDCMDS[5])):
        print('change settings')

    # help [h, help, q]
    if((inputstring == VALIDCMDS[6]) or (inputstring == VALIDCMDS[7]) or (inputstring == VALIDCMDS[8])):
        print('change settings')

    # quit [q, quit, e, exit]
    if((inputstring == VALIDCMDS[9]) or (inputstring == VALIDCMDS[10]) or (inputstring == VALIDCMDS[11]) or (inputstring == VALIDCMDS[12])):
        runFlag = False

# kill all sockets/threads