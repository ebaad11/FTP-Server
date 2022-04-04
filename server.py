# from builtins import print
import socket
import os
import sys

# from typing_extensions import ParamSpec
from logger import logger


class server:

    validCommnads = [
        "USER",
        "PASS",
        "CWD",
        "CDUP",
        "QUIT",
        "PASV",
        "EPSV",
        "PORT",
        "EPRT",
        "RETR",
        "STOR",
        "PWD",
        "LIST",
    ]

    # responses associated with each code
    RESPONSES = {
        110: "Restart marker reply.",
        120: "Service not yet ready.",
        125: "Data connection already open; transfer starting.",
        150: "File status okay; about to open data connection.",
        200: "Command okay.",
        202: "Command not implemented, superfluous at this site.",
        211: "System status, or system help reply.",
        212: "Directory status.",
        213: "File status.",
        214: "Help message.",
        215: "NAME system type.",
        220: "Welocme to the HW3 FTPserver.",
        221: "GOOD BYE",
        225: "Data connection open; no transfer in progress.",
        226: "Closing data connection. Requested file action successful.",
        227: "Entering Passive Mode.",
        230: "Login successful.",
        250: "change of directory completed",
        257: "is the current directory",
        331: "Please specify the password.",
        332: "Need account for login.",
        350: "Requested file action pending further information.",
        421: "Service not available, closing control connection.",
        425: "Can’t open data connection.",
        426: "Connection closed; transfer aborted.",
        450: "Requested file action not taken.",
        451: "Requested action aborted: local error in processing.",
        452: "Requested action not taken.",
        500: "Syntax error, command unrecognized.",
        501: "Syntax error in parameters or arguments.",
        502: "Command not implemented.",
        503: "Bad sequence of commands.",
        504: "Command not implemented for that parameter.",
        530: "Not logged in.",
        532: "Need account for storing files.",
        550: "Failed to change directory.",
        551: "Requested action aborted: page type unknown.",
        552: "Requested file action aborted.",
    }

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.psd = None

        self.command = None
        self.respone = None
        # hard coded values for testing
        self.userNames = ["user1", "user2", "user3"]
        self.passwords = ["pass1", "pass2", "pass3"]

        self.workingDirectory = os.getcwd()

        # logger

        self.loggerInst = logger()

        # command and data sockets to send data back and forth
        self.conncetionSocket = None
        self.dataSocket = None

        # modes
        self.passivemode = False
        # socket for recieving in commands
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))

        while True:

            # listening for connection from clients
            self.socket.listen(1)
            print("listenting")
            print("opening a server on port: ", port)

            # .accept() returns client socket object(conncetionSocket) and the address
            # of the connection(connectionAddress)
            self.conncetionSocket, connectionAddress = self.socket.accept()

            # self.conncetionSocket.bind((self.host, connectionAddress[1]))
            if self.conncetionSocket:

                self.sendResponse(220)

            while self.conncetionSocket:

                self.runCommand()

    # processes the command sent by client
    # sends error code back to the user upon faulty command

    # recieves a command and returns an array object where each elemnet
    # is an arrgumnet of the command sent split by spaces
    def recieveCommand(self):

        try:
            self.command = self.conncetionSocket.recv(1024).decode("ascii")
            print(self.command[:-2].split(" "))
            return self.command[:-2].split(" ")

        except Exception as ex:
            self.loggerInst.error(ex)
            # implemnet logger error handeling

    # TO DO :Implement the 501 :Syntax error in parameters or arguments."
    # send a message back to the client

    def sendResponse(self, responseCode, custom=None):

        if custom:
            response = custom
            response += "\r\n"

        else:
            response = f"{str(responseCode)} {self.RESPONSES[responseCode]}\r\n"
            self.loggerInst.info(response)

        try:
            self.conncetionSocket.send((response).encode("ascii"))
        except Exception as ex:
            self.loggerInst.error(ex)

    # SIGNIN

    # implements the user authentication
    def user(self, command, authenticated):

        if authenticated:
            # if user in system
            try:
                # asking for password code
                self.sendResponse(331)

            except Exception as ex:
                # log.error(str(error), self.client)
                self.loggerInst.error(ex)
        # not authenticated
        else:
            try:
                self.sendResponse(501)

            except Exception as ex:
                self.loggerInst.error(ex)

        # TO DO:
        #  query an SQL data base to see if the user exists
        # or
        # array solution

    # implements the password authentication
    def password(self, command, authenticated):

        # if the user exists query the SQL data base to authenticate password
        if authenticated:
            try:
                self.sendResponse(230)
            except Exception as ex:
                self.loggerInst.error(ex)
        # password not authenticated
        else:
            try:
                self.sendResponse(501)
            except Exception as ex:
                self.loggerInst.error(ex)

        # TO DO:
        #  query an SQL data base to see if the passowrd exists

    # SIMPLE COMMNADS

    # implements the PWD command

    # RETURN MESSAGE TO CLIENT IE :257 "/home/cs472" is the current directory
    def pwd(self):

        if self.workingDirectory:
            try:
                # send the working directory back to the user

                self.sendResponse(257, str(self.workingDirectory))

            except Exception as ex:
                self.loggerInst.error(ex)

        # get the current working directory and send it back to the user

    # Request: CWD /home
    # Implements the CWD command
    def cwd(self, command):
        # check if the command lenght is 2
        if len(command) == 2:
            # if the directory exists
            # change the working directory

            if os.path.exists(command[1]):
                # only changes as an attribute that could later be used to change directories
                self.workingDirectory = command[1]
                self.sendResponse(250)

            else:
                # return the error message
                self.sendResponse(550)
        else:
            # return the error message
            self.sendResponse(421)

    # Implements the CDUP command
    # changes the working directory to parent directory

    def cdup(self):
        # check if the command lenght is 2
        try:
            pathParent = os.path.dirname(self.workingDirectory)
            if pathParent:
                self.workingDirectory = pathParent
                self.sendResponse(250)
            else:
                # return the error message
                self.sendResponse(550)
        except Exception as ex:

            self.loggerInst.error(ex)

    # the list command is two commnads on the client side
    # First opens a port
    # Command : PORT 10,250,76,53,222,80
    # then
    # Commnad : LIST

    # implements the list command
    def list(self):

        try:
            # get the list of items in the working directory
            arraylist = os.listdir(self.workingDirectory)
            print(arraylist)

            self.sendResponse(150)

            #  sending data through ls over the port connection.
            for value in arraylist:
                self.dataSocket.send((str(value) + "\r\n").encode("ascii"))

            command = "226 Directory send OK."

            self.dataSocket.close()

            self.sendResponse(226, command)

        except Exception as ex:
            self.loggerInst.error(ex)

    # implements the quit command
    def quit(self):

        # sending request before the socket closes
        self.sendResponse(221)
        # close the connection socket
        self.conncetionSocket.close()
        # if there is a data socket
        if self.dataSocket:
            # close the data socket
            self.dataSocket.close()
        # return all the class attributes to NONE
        self.command = None
        self.respone = None
        self.conncetionSocket = None

    # CONNECTION COMMANDS

    # command :PORT 10,250,76,53,223,130
    # implements the port command
    def _port(self, command):

        # if an exisiting port(data) is open close it
        if self.dataSocket:
            self.dataSocket.close()

        fullAdd = command[1].split(",")
        print(fullAdd)

        # create a new data channel
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # TRY

        try:

            # get the last two pieces of numbmers from the port command(223,130)

            # set the port and host for the server side socket connection

            port = int(fullAdd[4]) * 256 + int(fullAdd[5])
            host = ".".join(fullAdd[:4])
            # CONNECT
            self.dataSocket.connect((host, port))
            command = "200 PORT command successful. Consider using PASV."
            self.sendResponse(200, command)

        # EXCEPT
        except Exception as ex:
            self.sendResponse(500)

    # EPRT |1|10.250.76.53|57022| command sample
    def eport(self, command):

        print("this function is not impleneted")

        # check if command has three arrguments

        # if close the exisitng data channel

        # TRY

        # parse the porrt out of the command

        # connect the socket

        # EXCPET

        # send and log error

        pass

    # implements the PASV command

    def passive(self):
        # if there is a data socket open close it
        if self.dataSocket:
            self.dataSocket.close()

        # open a new data socket
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.passivemode = True

        try:
            port = 0
            host = "127.0.0.1"
            self.dataSocket.bind((host, port))

            DP = self.dataSocket.getsockname()[1]
            RP = DP % 256

            p0 = self.dataSocket.getsockname()[0].replace(".", ",")
            p1 = str(int((DP - RP) / 256))
            p2 = str(RP)

            command = "227 Entering Passive Mode (%s,%s,%s)." % (p0, p1, p2)

            print(command, "this is the command")

            self.sendResponse(227, command)

        # EXCEPT
        except Exception as ex:
            self.loggerInst.error(ex)

        # send the error message and log the result

    # implements the epassive command
    def epassive(self):
        # if an existing data socket is open close it
        if self.dataSocket:
            self.dataSocket.close()

        # create a new  data socket
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.passivemode = True

        # TRY
        try:
            # set port and host
            port = 0
            host = "127.0.0.1"
            self.dataSocket.bind((host, port))
            # geting the data port
            DP = self.dataSocket.getsockname()[1]

            command = "229 Entering Passive Mode (|||%s)." % (DP)
            print(command, "this is the command")

            self.sendResponse(229, command)

        # bind the socket with the host

        # EXCEPT
        except Exception as ex:
            self.loggerInst.error(ex)

    # Implements the RETR command
    def retr(self, command):

        self.sendResponse(150)
        self.sendResponse(226)

        print("this funciton is not implemented")

    # Implements the STOR command
    def stor(self, command):

        # commands recieved by the client to know data transfer was succesfful
        # 150 Ok to send data.
        # 226 Transfer complete

        self.sendResponse(150)
        self.sendResponse(226)
        print("this function is not implemneted")

    # implements the running of each command

    def runCommand(self):
        command = self.recieveCommand()
        if (
            not command
            or len(command) < 1
            or command[0].upper() not in self.validCommnads
        ):
            self.sendResponse(501)
        else:
            command[0] = command[0].upper()
            if command[0] == "USER":
                self.user(command, True)
            elif command[0] == "PASS":
                self.password(command, True)
            elif command[0] == "CWD":
                self.cwd(command)
            elif command[0] == "CDUP":
                self.cdup()
            elif command[0] == "PWD":
                self.pwd()
            elif command[0] == "LIST":
                self.list()
            elif command[0] == "PORT":
                self._port(command)
            elif command[0] == "PASV":
                self.passive()
            elif command[0] == "EPRT":
                self.eport(command)
            elif command[0] == "EPSV":
                self.epassive(command)
            elif command[0] == "LOAD":
                self.retr(command)
            elif command[0] == "STOR":
                self.stor(command)
            else:
                self.sendResponse(502)


if __name__ == "__main__":

    if len(sys.argv) == 2:

        port = sys.argv[1]
        # always local host for this program
        # takes in the file name but genterates its own based on time and data
        SS = server("127.0.0.1", int(port))
        print("listenting")
        print("opening a server on port: ", port)

    else:
        print("Valid command serve.py <port>")
        exit(0)
