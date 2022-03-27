import socket
import errno
import sys
import threading
HEADER_LENGTH = 4096

IP_ADD = "<IP ADDRESS HERE>"
PORT_NUM = 1234

accountPermission = "nurse"

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
            print("What would you like to do today?\n1. View your details\n2. Insert a new log")
            chosenOption = input()
            if int(chosenOption) == 1:
                message1 = "nurseDetail;1"
                message2 = message1.encode('utf-8')
                message_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(message_header + message2)
            elif int(chosenOption) == 2:
                print("Please input the patient's ID\n")
                patientId = input()
                print("Please write the log that you wish to input\n")
                logInput = input()
                logInput = logInput.replace(" ", "_")
                message1 = f"insertLog;{patientId},{logInput}"
                message2 = message1.encode('utf-8')
                message_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(message_header + message2)

#So that the user can terminate the group gracefully.
    except KeyboardInterrupt:

        sys.exit(0)


