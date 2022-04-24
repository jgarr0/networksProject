# Client script
# TO-DO: Generate JSON in client script, parse JSON in server script, add client/server logic to output as string or reconstruct file, restructure socket code be its own function?

import socket
import pickle
import json

HEADERSIZE = 10

# Testing data values
serverIP = "10.10.10.131"
serverPort = 8080
encryptedKey = "applepie"
dataOriginal = "test.txt"
dataFileType = "txt"

def dataSend():
    # Connect to peer via socket
    print("Establishing socket")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4/TCP socket
    client.connect((serverIP, serverPort))
    print(type(client))

    # Detect if passed data is file. If so, serialize/convert file to bytes. Else, assume we're sending text
    fileContents = b''
    if not dataFileType == "NULL":
        file = open(dataOriginal, "rb") # read file as read-only binary
        fileContents = str(file.read())
        print(fileContents)

        dataEncrypted = fileContents # ~~ ENCRYPT DATA HERE - PASS fileContents and encryptedKey, RETURN encrypted data ~~
    else:
        dataEncrypted = dataOriginal # ~~ ENCRYPT DATA HERE - PASS dataOriginal and encryptedKey, RETURN encrypted data ~~

    # Create a JSON with all of the data to send to the server
    dataDict = {"responseIP":'', "responsePort":serverPort, "encryptedData":dataEncrypted, "encryptedKey":encryptedKey, "fileType":dataFileType}
    dataJSON = json.dumps(dataDict)

    # Serialize/convert JSON to bytes
    pickledJSON = pickle.dumps(dataJSON)

    # Create a string with the message's length. Our protocol says it will alway be of length "HEADERSIZE"
    msgSize = f"{len(pickledJSON):<{HEADERSIZE}}" 
    print(f"Message size to send: {msgSize}")

    # Create string of bytes with the message length appended to the beginning of the encrypted string (our header)
    fullMsg = bytes(msgSize, "utf-8") + pickledJSON 
    print(f"Message to send: {fullMsg}")

    # Send data stream and close socket
    client.send(fullMsg) 
    client.close()

    return

dataSend()