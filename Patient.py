import socket
import errno
import sys
import threading
HEADER_LENGTH = 4096

IP_ADD = "192.168.0.196"
PORT_NUM = 1234

accountPermission = "patient"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP_ADD, PORT_NUM))


username = accountPermission.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)


def receiving():
    while True:
        try:
            while True:

                username_header = client_socket.recv(HEADER_LENGTH)

                if not len(username_header):
                    print('Server terminated.')
                    sys.exit()

                message_header = client_socket.recv(HEADER_LENGTH)
                message = message_header.decode('utf-8')
                print(f'{message}')


        except IOError as e:

            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            continue

        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()

# Use multi-threading to simulataneously check receiving.
background_thread = threading.Thread(target=receiving) # To-check function is the sending()
background_thread.daemon = True
background_thread.start()
startScreen = 0
mainMenu = 0

while True:
    try:
        while True:
            if startScreen == 0:
                message1 = "id;1"
                message2 = message1.encode('utf-8')
                message_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(message_header + message2)
                startScreen = 1
                mainMenu = 1
            if mainMenu == 1:
                print("What would you like to do today?\n1. Check your latest log\n2. View your details")
                chosenOption = input()
                if int(chosenOption) == 1:
                    message1 = "latestLog;1"
                    message2 = message1.encode('utf-8')
                    message_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                    client_socket.send(message_header + message2)
                elif int(chosenOption) == 2:
                    message1 = "checkDetails;1"
                    message2 = message1.encode('utf-8')
                    message_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                    client_socket.send(message_header + message2)

#So that the user can terminate the group gracefully.
    except KeyboardInterrupt:

        sys.exit(0)


