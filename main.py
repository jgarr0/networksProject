from asyncio.windows_events import NULL
from cgi import test
from http import server
from operator import length_hint, truediv   # get length of lists
import sys
from urllib.request import DataHandler
from requests import get                    # get current IP
from os.path import exists                  # check that files exist

# other impots
import threading
import json                                 # json file support + associated functions
import shlex                                # command parsing to preserve substrings
import time                                 # get time that message was created for indexing
import client
import server
from datetime import datetime, timezone

# crypto imports
import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

backend = default_backend()

# number of iterations to run crypto algorithm
iterations = 100_000

#######################################################################################################################################################

# supported instructions:
#   h                                                           = explanation + show commands
#   m [ip:optional port] [message type] ['message'] ['key']     = send message
#   l [type]                                                    = list messages
#   v [index] [destination] [name] [decryption key]             = decrypt a message'

#######################################################################################################################################################

# recognized commands
VALIDCMDS = ['m', 'msg', 'd', 'decrypt', 'h', 'help', '?', 'q', 'quit', 'e', 'exit', 'l', 'list']

# type of content that can be sent
# -f = file; specify a file path in the next parameter
# -m = text; specify plain text in the next parameter
VALFMT = ['-f', '-t']

# type of content to be viewed
# -s = view sent messages
# -r = view received messages
VALVIEW = ['-s', '-r']

# default port used by listening socket
DFTPORT = 8080

#######################################################################################################################################################

# code from https://www.ipify.org/ -> unneeded
#def getPublicIP():
#    return get('https://api.ipify.org').text

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
    portResponse = input('Would you like to recieve messages on the default port (8080)? ')
    if(portResponse != 'y' and portResponse != 'yes'):
        newPortNumber = newPort()

    defaultKey = NULL
    while(defaultKey == NULL):
        testInput = input('What would you like your default key for encrypting data to be? ')
        if(testInput != NULL):
            defaultKey = testInput
        else:
            print('The default key can not be empty')

    defaultAttempts = NULL
    while(defaultAttempts == NULL):
        testInput = input('What would you like the default number of attempts to decrypt messages that you send to be? ')
        # valid input conditions
        if(int(testInput) > 0 and int(testInput) < 101) and testInput.isnumeric() == True:
            defaultAttempts = testInput
        else:
            print('The default number of attempts to decrypt messages must be between 1 and 100')

    # json struct for user info
    userInfo = {
        "name" : nick,
        "defaultPort" : newPortNumber,
        "defaultKey" : defaultKey,
        "defaultAttempts" : defaultAttempts
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

# Derive a secret key from a given password and salt
def _derive_key(password: bytes, salt: bytes, iterations: int = iterations) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=iterations, backend=backend)
    return b64e(kdf.derive(password))

# encrypt message with key
def password_encrypt(message: bytes, password: str, iterations: int = iterations) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    return b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message)),
        )
    )

# decrypt message from key
def password_decrypt(token: bytes, password: str) -> bytes:
    print(type(token))
    print(token)
    print(password)
    decoded = b64d(token)
    salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, 'big')
    key = _derive_key(password.encode(), salt, iterations)
    return Fernet(key).decrypt(token)

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

# header- cool ascii art?
print('################################\nPeer to Peer Encrypted Messanger\n################################\n')

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
DFTATTEMPTS = userInfo["defaultAttempts"]

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
print('\nwelcome ' + name + '!\n')
#print('\tYour Public IP is:', getPublicIP()) --> unneeded
#print('\tCurrently receiving on port:', currentPort) --> unneeded
print('##########################################\n')

# create listening socket on its own thread here
# pass thread the list for recieved messages
listenThread = threading.Thread(target=server.dataReceive, args=(receivedMessages, receivedACK), daemon=True)
listenThread.start()

# begin main program loop
runFlag = True
while(runFlag):

    # check to see if listening socket has anything
    inputstring = str(input(name + "> "))

    # do not accept empty input or pure white space input
    if(inputstring != NULL and inputstring.isspace() == False and inputstring != ''):
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
            if(numArg > 6 or numArg < 4):
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
                    dataToSend = str(fileInput.read())

            # key check
            currentKey = NULL

            # check optional paramaeters

            # if 4 parameters, use default key and default number of attempts
            if(numArg == 4):
                currentKey = str(DFTKEY)
                numAttempts = str(DFTATTEMPTS)

            # if 1 optional argument, could be the key or the number of attempts
            if(numArg == 5):
                # determine if key or nuymber of tries
                argLength = commandParts[4].len()

                # if enclosed with parenthesis, argument is the key
                if((commandParts[4][0] == '"' and commandParts[4][argLength-1] == '"') or (commandParts[4][0] == '\'' and commandParts[4][argLength-1] == '\'')):
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
                    numAttempts = str(DFTATTEMPTS)  

                # otherwise, argument is the number of attempts
                else:
                    if(str(commandParts[4]).isnumeric() == True and () > 0 and (int(commandParts[4]) < 101 and int(commandParts[4]) > 1)):
                        numAttempts = str(commandParts[4])  
                        currentKey = str(DFTKEY)

                    # stop if bad argument
                    else:
                        continue;

            # if both optional arguments, ensure that they are in the correct order and that they are valid
            if(numArg == 6):
                # make sure first argument is the key
                if((commandParts[4][0] == '"' and commandParts[4][argLength-1] == '"') or (commandParts[4][0] == '\'' and commandParts[4][argLength-1] == '\'')):
                    # check that provided key is not whitespace
                    if(str(commandParts[4]).isspace()):
                        print("Provided key can not be only whitespace")
                        continue;

                    # check that provided key field is not empty
                    if(str(commandParts[4]) == ""):
                        print("Provided key can not be empty")
                        continue;

                    # if here, provided key is acceptable
                    currentKey = str(commandParts[4])

                # make sure that the number of tries is valid
                if(str(commandParts[5]).isnumeric() == True and () > 0 and (int(commandParts[5]) < 101 and int(commandParts[5]) > 1)):
                    numAttempts = str(commandParts[5])  

                # stop if bad argument
                else:
                    continue;
                # make sure second argument is the number of attempts
                    
            # get time that the message was sent
            sendTime = int(time.time())

            # if we are here, can open a socket and send the message
            # all required info is here

            # encrypts data and key here
            # just double check these are the correct variables for message and key.
            encrpyted_message = str(password_encrypt(dataToSend.encode(), currentKey))
            encrypted_key = str(password_encrypt(currentKey.encode(), str(sendTime)))

            # create dict here
            encrPacket= {
                "timeSent" : sendTime,
                "maxAttempts" : numAttempts,
                "responseIP" : "NULL",
                "responsePort" : currentPort,
                "destinationIP" : destIP,
                "destinationPort" : destPort,
                "encryptedMessage": encrpyted_message,
                "encryptedKey" : encrypted_key,
                "dataType": fileExt
            }

            # store time sent, dest IP, despPort, and encryptedKey
            sentMessages.append({"timeSent":encrPacket['timeSent'], "maxAttempts":encrPacket['maxAttempts'],'destinationIP':encrPacket['destinationIP'], 'destinationPort':encrPacket['destinationPort'], 'encryptedKey':encrPacket['encryptedKey'], 'dataType':encrPacket['dataType']})

            # send with socket here
            client.dataSend(encrPacket)

        # list [l, list]
        if((commandParts[0].lower() == VALIDCMDS[11]) or (commandParts[0].lower() == VALIDCMDS[12])):
            # msg needs 2; stop processing if not met
            numArg = length_hint(commandParts)
            if(numArg != 2):
                print("Please specify if you want to view sent or received messages")
                continue;

            # view sent messages
            if(commandParts[1].lower() == VALVIEW[0]):
                numSentMsg = length_hint(sentMessages)
                if(numSentMsg == 0):
                    print("No sent messages!")
                    continue;

                # index for messages
                sendIndex = 0

                # display relevant information
                print(str(numSentMsg) + " sent messages:")
                while sendIndex < numSentMsg:
                    print("\t" + str(sendIndex) + " || " + str(datetime.fromtimestamp(int(sentMessages[sendIndex]["timeSent"]), timezone.utc)) + " || " + sentMessages[sendIndex]["destinationIP"])
                    sendIndex = sendIndex + 1

            # view recieved messages
            elif(commandParts[1].lower() == VALVIEW[1]):
                # index received messages
                numRecMsg = length_hint(receivedMessages)
                if(numRecMsg == 0):
                    print("No received messages!")
                    continue;

                # index for messages
                receiveIndex = 0

                # display relevant information
                print(str(numRecMsg) + " recieved messages:")
                while receiveIndex < numRecMsg:
                    print("\t" + str(int(receiveIndex) + 1) + " || " + str(datetime.fromtimestamp(int(receivedMessages[receiveIndex]["timeSent"]), timezone.utc)) + " || " + receivedMessages[receiveIndex]["responseIP"])
                    receiveIndex = receiveIndex + 1

            # error for no type of messages specified
            else:
                print("Please specify if you want to view sent or recieved messages")
                continue;

        # decrypt [d, decrypt]
        if((commandParts[0].lower() == VALIDCMDS[2]) or (commandParts[0].lower() == VALIDCMDS[3])):
            print('decrypt a specific message')
            # decrypt a message by its index
            
            # remove dict with matching time index - https://www.geeksforgeeks.org/python-removing-dictionary-from-list-of-dictionaries/
            #sentMessages = [i for i in sentMessages if not (i['timeSent'] == sendTime)]

            # load in flags from command
            selectedIndex = int(commandParts[1])
            key = str(commandParts[2])
            dataType = receivedMessages[selectedIndex]['dataType']

            encryptedMsg = str(receivedMessages[selectedIndex]['encryptedMessage'])
            encryptedMsgSubstr = encryptedMsg[2:126]

            # send ACK to receiver here
            # generate encrypted form of input key
            encrypted_key = str(password_encrypt(key.encode(), str(receivedMessages[selectedIndex]['timeSent'])))

            # get time of attempted decryption
            decryptTime = int(time.time())

            # create dict here
            decrPacket= {
                "decryptTime" : decryptTime,
                "destinationIP" : str(receivedMessages[selectedIndex]['responseIP']),
                "destinationPort" : str(receivedMessages[selectedIndex]['responsePort']),
                "encryptedKey" : encrypted_key,
                "dataType": "attemptedDecryptionKeyNotARealFileExtension"                       # hardcoded joke file extension to indicate ACK packets
            }

            # store time sent, dest IP, despPort, and encryptedKey
            sentACK.append({"decryptTime" : decrPacket['decryptTime'], "destinationIP" : decrPacket['destinationIP'], "destinationPort" : decrPacket['destinationPort'], "encryptedKey" : decrPacket['encryptedKey'], "dataType": decrPacket['dataType']})

            # send with socket here
            client.dataSend(decrPacket)

            # attempt to decrypt the message\
            try:
                decrypted_message = str(password_decrypt(encryptedMsgSubstr.encode(), key))

                # If text, display in console. Else, assume file and ask for file name to write
                if dataType == NULL:
                    print(f"Message from {receivedMessages[selectedIndex]['responseIP']}: {decrypted_message}")
                else:
                    print(f"File received from {receivedMessages[selectedIndex]['responseIP']}.")
                    fileSaveName = input("Enter a file name to save: ")

                    if not fileSaveName.contains("."):
                        fileSaveName = fileSaveName + "." + dataType
                    
                    file = open(fileSaveName, "wb") # write file as binary
                    file.write(decrypted_message)
                    file.close()

                    print(f"File saved to: .\{fileSaveName}")
            
            # catch InvalidSignature error
            except Exception as inst:
                continue;
    
            # Delete dictionary entry since message has been decrypted/viewed
            del receivedMessages[selectedIndex]

        # help [h, help, q]
        if((commandParts[0].lower() == VALIDCMDS[4]) or (commandParts[0].lower() == VALIDCMDS[5]) or (commandParts[0].lower() == VALIDCMDS[6])):
            printHelp()

        # quit [q, quit, e, exit]
        if((commandParts[0].lower() == VALIDCMDS[7]) or (commandParts[0].lower() == VALIDCMDS[8]) or (commandParts[0].lower() == VALIDCMDS[8]) or (commandParts[0].lower() == VALIDCMDS[10])):
            # kill the program
            runFlag = False

# kill all sockets/threads after this point
# |------> thread is set as a daemon- dies on program termination
