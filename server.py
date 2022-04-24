# Server script
# TO-DO: Generate JSON in client script, parse JSON in server script, add client/server logic to output as string or reconstruct file, restructure socket code be its own function?

import socket
import pickle
import json

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4/TCP socket

server.bind(('0.0.0.0', 8080))
server.listen(5)

HEADERSIZE = 10

def dataReceive():
    while True:
        # Accept a new connection
        clientConn, clientAddress = server.accept() 
        responseIP = {"responseIP":clientAddress[0]} # Add client IP address to dictionary for later dictionary update

        # Create empty byte string for the received message and new message flag
        fullMsgPickled = b'' 
        newMsg = True
        
        # Loops until entire message is received
        while True:
            # Our protocol says the client will send the message size appended to beginning of string
            if newMsg:
                data = clientConn.recv(HEADERSIZE)
                msgSize = int(data)
                print(f"Message length to receive: {msgSize}")
                newMsg = False

            # Break if message size of neg or zero so it doesn't run the remaining code
            if msgSize <= 0: 
                break

            # We purposely only append the fullMsg here so we don't append the msgSize
            # If length of expected message isn't met, keep receiving more data
            if len(fullMsgPickled) < msgSize: 
                data = clientConn.recv(16)
                fullMsgPickled = fullMsgPickled + data
            # Else, the message size is met, so print the full message
            else: 
                print(f"Received message length: {len(fullMsgPickled)}")
                print("Full message received!\n")

                print ("---------- MESSAGE (Pickled): ---------")
                print(fullMsgPickled)
                print ("-----------------------------\n")

                fullMsg = pickle.loads(fullMsgPickled)
                print ("---------- MESSAGE (Unpickled): ---------")
                print(fullMsg)
                print ("-----------------------------\n")

                # Process the obtained JSON data to give us a dictionary again
                receivedDict = json.loads(fullMsg)
                print(f"The results:\n{receivedDict}")

                # Update dictionary with the IP address to use for responses
                receivedDict.update(responseIP)
                print(f"The results v2:\n{receivedDict}")

                # Detect if passed data is file. If so, deserialize. Else, assume we've received text
                if not receivedDict.get("fileType") == "NULL":
                    dataDecrypted = receivedDict.get("encryptedData") # ~~ DECRYPT DATA HERE - PASS encryptedData and encryptedKey, RETURN decrypted data ~~
                    
                    file = open(str(f"receivedFile." + receivedDict.get("fileType")), "wb") # write file as binary
                    file.write(dataDecrypted)
                    file.close()
                else:
                    dataDecrypted = receivedDict.get("encryptedData")

                # Write JSON to file
                with open('receivedData.json', 'w') as json_file:
                    json.dump(fullMsg, json_file)

                # Reset message size back to zero, will also break us out of the while loop
                msgSize = 0 

        # Close connection
        clientConn.close()
        print('Client disconnected')

    return

dataReceive()