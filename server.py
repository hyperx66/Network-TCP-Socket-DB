import socket
import select
import sys
import errno
import datetime
import mysql.connector
from mysql.connector import Error

HEADER_LENGTH = 4096
connection = mysql.connector.connect(
    host='194.59.164.158', database='u645071659_makerspace', user='u645071659_hyperx66', password='s9740499b')
IP_ADD = "192.168.0.196"
PORT_NUM = 1234
check = 0
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP_ADD, PORT_NUM))
server_socket.listen()
server_socket.setblocking(False)
sockets_list = [server_socket]
clients = {}
print(f'Awaiting connection from {IP_ADD}:{PORT_NUM}...')


def initialiseDatabaseConnect(commandType, patientId):
    try:
        if commandType == "select":
            sql_select_Query = "SELECT * FROM patient WHERE patientId = " + patientId
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            for row in records:
                return row
            cursor.close()
        elif commandType == "checkDetails":
            sql_select_Query = "SELECT * FROM patient WHERE patientId = " + patientId
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            for row in records:
                return row
            cursor.close()
        elif commandType == "selectLog":
            sql_select_Query = "SELECT * FROM patientLog WHERE patientId = " + patientId + " ORDER BY logTimeStamp DESC"
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            for row in records:
                return row
            cursor.close()
        elif commandType == "selectNurse":
            sql_select_Query = "SELECT * FROM staffNetworking WHERE nuseId = " + patientId 
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            for row in records:
                return row
            cursor.close()
    except Error as e:
        print("Error reading data from MySQL table", e)

def insertIntoDatabase(commandType, patientId, logInput):
    try:
        if commandType == "insertLog":
            print("Patient ID is "+patientId)
            print("Log is "+logInput)
            now = datetime.datetime.now()
            nowFormatted = now.strftime('%Y-%m-%d %H:%M:%S')
            sql_select_Query = "INSERT INTO patientLog VALUES(0, '"+logInput+"','"+nowFormatted+"',"+patientId+")"
            print(sql_select_Query)
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            connection.commit()
            cursor.close()
    except Error as e:
        print("Error reading data from MySQL table", e)

def receive_message(client_socket):
    try:

        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False


def sendClientMsg(clientSocket, msg):
    message2 = msg.encode('utf-8')
    message_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
    clientSocket.sendall(message_header+message2)


while True:

    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)

            if user is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print('New connection from {}:{}, username: {}'.format(
                *client_address, user['data'].decode('utf-8')))
            

        else:
            message = receive_message(client_socket)

            if message is False:

                user = clients[notified_socket]

                leaveMessage = user['data'].decode('utf-8') + " has left."
                leaveMessage_header = f"{len(leaveMessage):<{HEADER_LENGTH}}".encode(
                    'utf-8')

                text = user['header'] + user['data'] + \
                    leaveMessage_header + leaveMessage.encode('utf-8')

                print('Connection closed from: {}'.format(
                    clients[notified_socket]['data'].decode('utf-8')))

                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[client_socket]
            print(
                f'Message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            if user["data"].decode("utf-8") == "patient":
                # Start of patient
                stringArr = message['data'].decode("utf-8").split(" ")
                for dataStr in stringArr:
                    individualData = dataStr.split(";")
                    if individualData[0] == "id":
                        message = "Welcome " + \
                            initialiseDatabaseConnect("select", individualData[1])[1]
                        sendClientMsg(client_socket, message)
                    if individualData[0] == "latestLog":
                        message = "This is your latest log: " + \
                            initialiseDatabaseConnect(
                                "selectLog", individualData[1])[1]
                        sendClientMsg(client_socket, message)
                    if individualData[0] == "checkDetails":
                        message = "These are your details: \n"
                        rowDetails = initialiseDatabaseConnect("checkDetails", individualData[1])
                        message += "Patient ID is "+(str)(rowDetails[0])+"\n"
                        message += "Patient Full Name is "+(str)(rowDetails[1])+"\n"
                        message += "Patient Address is "+(str)(rowDetails[2])+"\n"
                        message += "Patient Ward No is "+(str)(rowDetails[3])+"\n"
                        message += "Patient Bed No is "+(str)(rowDetails[4])+"\n"
                        sendClientMsg(client_socket, message)
            elif user["data"].decode("utf-8") == "nurse":
                # Start of nurse
                stringArr = message['data'].decode("utf-8").split(" ")
                for dataStr in stringArr:
                    individualData = dataStr.split(";")
                    if individualData[0] == "insertLog":
                        dataForInsert = individualData[1].split(",")
                        patientId = dataForInsert[0]
                        patientLog = dataForInsert[1]
                        patientLog = patientLog.replace("_"," ")
                        insertIntoDatabase("insertLog", patientId, patientLog)
                    if individualData[0] == "nurseDetail":
                        rowDetails = initialiseDatabaseConnect("selectNurse", individualData[1])
                        message = "These are your details: \n"
                        message += "Patient ID is "+(str)(rowDetails[0])+"\n"
                        message += "Patient Full Name is "+(str)(rowDetails[1])+"\n"
                        message += "Patient Address is "+(str)(rowDetails[2])+"\n"
                        message += "Patient Ward No is "+(str)(rowDetails[3])+"\n"
                        message += "Patient Bed No is "+(str)(rowDetails[4])+"\n"
        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]

if (connection.is_connected()):
    connection.close()
    print("MySQL connection is closed")
