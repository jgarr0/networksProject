# Client script
# TO-DO: Generate JSON in client script, parse JSON in server script, add client/server logic to output as string or reconstruct file, restructure socket code be its own function?

import socket
import pickle
import json
import sys

HEADERSIZE = 10

def dataSend(dataDict):
    serverIP = dataDict.get("destinationIP", "NULL")
    if serverIP == "NULL":
        print("Could not find destination IP")
        sys.exit()
    elif serverIP == "":
        print("Destination IP is empty")
        sys.exit()
    
    serverPort = dataDict.get("destinationPort", "NULL")
    if serverIP == "NULL":
        print("Could not find destination port")
        sys.exit()
    elif serverIP == "":
        print("server port is empty")
        sys.exit()

    # Connect to peer via socket
    #print("Establishing socket")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4/TCP socket
    client.connect((serverIP, int(serverPort)))

    # Create a JSON with all of the data to send to the server
    dataJSON = json.dumps(dataDict)

    # Serialize/convert JSON to bytes
    pickledJSON = pickle.dumps(dataJSON)

    # Create a string with the message's length. Our protocol says it will alway be of length "HEADERSIZE"
    msgSize = f"{len(pickledJSON):<{HEADERSIZE}}" 
    #print(f"Message size to send: {msgSize}")

    # Create string of bytes with the message length appended to the beginning of the encrypted string (our header)
    fullMsg = bytes(msgSize, "utf-8") + pickledJSON 
    #print(f"Message to send: {fullMsg}")

    # Send data stream and close socket
    #print("Message sent")
    client.send(fullMsg) 
    client.close()

    return