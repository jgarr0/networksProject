from asyncio.windows_events import NULL
from cgi import test
from operator import length_hint, truediv   # get length of lists
import sys 
from urllib.request import DataHandler
from requests import get                    # get current IP
from os.path import exists                  # check that files exist

# other impots
import json                                 # json file support + associated functions                               
import shlex                                # command parsing to preserve substrings
import time                                 # get time that message was created for indexing

#######################################################################################################################################################

# supported instructions:
#   h                                                           = explanation + show commands
#   m [ip:optional port] [message type] ['message'] ['key']     = send message
#   l [type]                                                    = list messages
#   v [index] [destination] [name] [decryption key]             = decrypt a message'

#######################################################################################################################################################

# recognized commands
VALIDCMDS = ['m', 'msg', 'v', 'view', 'h', 'help', '?', 'q', 'quit', 'e', 'exit', 'l', 'list']

# type of content that can be sent
# -f = file; specify a file path in the next parameter
# -m = text; specify plain text in the next parameter
VALFMT = ['-f', '-t']

# default port used by listening socket
DFTPORT = 11083

#######################################################################################################################################################

# header
print('################################\nPeer to Peer Encrypted Messanger\n################################\n')

# code from https://www.ipify.org/
def getPublicIP():
    return get('https://api.ipify.org').text

# assign the default port
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
# declare a name, desired port, default encryption key
# declare desired location to store decrypted data?
def firstTimeSetup():
    #begin setup
    nick = input('Please enter your nickname: ')
    newPortNumber = DFTPORT 

    # get response
    portResponse = input('Would you like to recieve messages on the default port (11083)? ')
    if(portResponse != 'y' and portResponse != 'yes'):
        newPortNumber = newPort()

    defaultKey = NULL
    while(defaultKey == NULL):
        testInput = input('What would you like your default key for encrypting data to be? ')
        if(testInput != NULL):
            defaultKey = testInput
        else:
            print('The default key can not be empty')

    # json struct for user info
    userInfo = {
        "name" : nick,
        "defaultPort" : newPortNumber,
        "defaultKey" : defaultKey
    }

    # write port and name to settings
    with open('settings.json', 'w') as f:
        json.dump(userInfo, f)

    # display commands
    print('################################')
    printHelp()
    
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
    # invalid if not purely numeric
    if(not str(portnumber).isnumeric()):
        return False
    # invalid if out of bounds
    if(int(portnumber) > 65535 or int(portnumber) < 1024):
        return False
    return True

# get file extension from file path
def getExt(filePath):
    # split along '.'
    splitPath = filePath.split('.')
    numPathArgs = length_hint(splitPath)
    if(numPathArgs == 0):
        return NULL
    else:
        return splitPath[numPathArgs-1]

# print all supported commands
def printHelp():
    print('Supported Instructions:\n')

    # m cmd
    print('send a message- m, msg')
    print('\n\tm [ip:optional port] [message type] ["message"] ["key"] \t= send a message')
    print('\n\t\tip \t\t= destination IP address (xxx.xxx.xxx.xxx)\n\t\tport \t\t= optional destination port (if none provided, the default port is used)')
    print('\t\tmessage type \t= -t for plain text, -f for file\n\t\tmessage \t= plaintext for text, a path to the file for -f')
    print('\t\tkey \t\t= optional encryption key. T client\'s default encryption key is used if none provided.')

    # l cmd
    print('\nlist all messages- l, list')
    print('\tl \t\t\t\t\t\t\t\t= list all received messages')

    # v cmd
    print('\nview message- v, view')
    print('\tv [index] [destination] [name] [decryption key] \t\t= decrypt a message')
    print('\n\t\tindex \t\t= number assigned to message\n\t\tdestination \t= optional location to write result (if none provided, the default location is used)')
    print('\t\tname \t\t= name for file\n\t\tdecryption key \t= key to decrypt message')

    # s cmd
    print('\nsettings- s, settings')
    print('\ts [arg] [variable] [new value] = change or view settings')
    print('\t\targ \t\t= -v to view, -cc to change\n\t\tvariable \t= name, port, key, or path\n\t\tnew value \t= new value for parameter')

    # q cmd
    print('\nquit- q, quit, e, exit')
    print('\tq \t\t\t\t\t\t\t\t = quit program\n')

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
DFTKEY = userInfo["defaultKey"]

# lists to store message information
# list for sent messages
sentMessages = []

# list for recieved messages
receivedMessages = []

# list for sent acks
sentACK = []

# list for receievd acks
receivedACK = []

# display current public IP and defined port
print('##########################################')
print('welcome ' + name + '!')
print('\tYour Public IP is:', getPublicIP())
print('\tCurrently receiving on port:', currentPort)
print('##########################################\n')

# create listening socket on its own thread here
# want to place incoming messages into a list in memory- thoughts?


# begin main program loop
runFlag = True
while(runFlag):
    # check to see if listening socket has anything 
    inputstring = str(input(name + "> "))


    if(inputstring != NULL and inputstring.isspace() == False):
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

            # assign destination IP
            destIP = destInfo[0]
            destPort = DFTPORT

            # if valid, see if there is a port and check if it is valid
            if(ipArgs == 2):
                if(not portCheck(str(destInfo[1]))):
                    print(destInfo[1] + ' is not a valid port number')
                    continue;

                # if this passes, destPort = destInfo[1]
                destPort = str(destInfo[1])

            # check type of message
            msgFmt = commandParts[2].lower()
            if(msgFmt not in VALFMT):
                print(commandParts[2] + "is not a valid argument for the type of content to send")
                continue;

            # handle -t = text
            fileExt = NULL
            dataToSend = NULL
            if(msgFmt == '-t'):
                print('text input')
                # update contents
                dataToSend = commandParts[3]

            if(msgFmt == '-f'):
                print('fileInput')
                # check that file exists
                if(exists(commandParts[3]) == False):
                    print('Specified file does not exist!')
                    continue;
                # if the file exists
                else:
                    fileExt = getExt(commandParts[3])
                    if(fileExt == NULL):
                        print("Can not determine file extension from the provided path")
                        continue;
                    fileInput = open(commandParts[3], 'rb')
                    dataToSend = fileInput.read()

            # key check
            currentKey = NULL

            # if no key provided, use default key
            if(numArg == 4):
                currentKey = str(DFTKEY)

            # if a key is provided, ensure that it is correct
            if(numArg == 5):
                # check that provided key is not whitespace
                if(str(commandParts[4]).isspace()):
                    print("Provided key can not be only whitespace")
                    continue;

                # check that provided key field is not empty
                if(str(commandParts[4]) == ""):
                    print("Provided key can not be empty")
                    continue;

                # if valid, use entered key
                currentKey = str(commandParts[4])

            #print("current port: " + str(currentPort) +  "\ndestination IP: " + str(destIP) + "\ndestination port: " + str(destPort) + "\ndata to send: " + str(dataToSend) + "\nfile ext (if applicable): " + str(fileExt))
            sendTime = int(time.time())

            # if we are here, can open a socket and send the message
            # all required info is here

            # encrypt data here

            # encrypt key here

            # create dict here
            encrPacket = {
                "timeSent" : sendTime,
                "responseIP" : "NULL",
                "responsePort" : currentPort,
                "destinationIP" : destIP,
                "destinationPort" : destPort,
                "encryptedMessage": dataToSend,                 # TODO replace with encrypted data
                "encryptedKey" : currentKey,                    # TODO replace with encrypted key
                "dataType": fileExt
            }

            # store time sent, dest IP, despPort, and encryptedKey
            sentMessages.append({encrPacket['timeSent'], encrPacket['destinationIP'], encrPacket['destinationPort'], encrPacket['encryptedKey']})
            #print(sentMessages)
            
            # send with socket here

        # list [l, list]
        if((commandParts[0].lower() == VALIDCMDS[11]) or (commandParts[0].lower() == VALIDCMDS[12])):
            print('list all messages')
            # display indexed list of all IPs that a message was sent to or received from (maybe date/time and name too)?

        # view [v, view]
        if((commandParts[0].lower() == VALIDCMDS[2]) or (commandParts[0].lower() == VALIDCMDS[3])):
            print('view a specific message')
            # decrypt a message by its index
            # remove dict with matching time index - https://www.geeksforgeeks.org/python-removing-dictionary-from-list-of-dictionaries/
            #sentMessages = [i for i in sentMessages if not (i['timeSent'] == sendTime)]
            print(sentMessages)

        # settings [settings, s]
        #if((commandParts[0].lower() == VALIDCMDS[4]) or (commandParts[0].lower() == VALIDCMDS[5])):
        #    print('change settings')

        # help [h, help, q]
        if((commandParts[0].lower() == VALIDCMDS[4]) or (commandParts[0].lower() == VALIDCMDS[5]) or (commandParts[0].lower() == VALIDCMDS[6])):
            printHelp()

        # quit [q, quit, e, exit]
        if((commandParts[0].lower() == VALIDCMDS[7]) or (commandParts[0].lower() == VALIDCMDS[8]) or (commandParts[0].lower() == VALIDCMDS[8]) or (commandParts[0].lower() == VALIDCMDS[10])):
            # kill the program
            runFlag = False

# kill all sockets/threads after this point