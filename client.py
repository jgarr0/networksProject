# Client script
# TO-DO: Generate JSON in client script, parse JSON in server script, add client/server logic to output as string or reconstruct file, restructure socket code be its own function?

import socket
import pickle

HEADERSIZE = 10

# Testing data values
serverIP = "10.10.10.131"
serverPort = 8080
dataFormat = "text"
dataText = "This is my test message! YAY!"

def dataSend():
    # Connect to peer via socket
    print("Establishing socket")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4/TCP socket
    client.connect((serverIP, serverPort))
    print(type(client))

    # ~~ ENCRYPT DATA HERE ~~

    # Serialize/convert data input to bytes
    pickledMsg = pickle.dumps(dataText) 

    # Create a string with the message's length. Our protocol says it will alway be of length "HEADERSIZE"
    msgSize = f"{len(pickledMsg):<{HEADERSIZE}}" 
    print(f"Message size to send: {msgSize}")

    # Create string of bytes with the message length appended to the beginning of the encrypted string (our header)
    fullMsg = bytes(msgSize, "utf-8") + pickledMsg 
    print(f"Message to send: {fullMsg}")

    # Send data stream and close socket
    client.send(fullMsg) 
    client.close()

    return

dataSend()