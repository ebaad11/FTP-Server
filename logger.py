# class for logging requests/response from the client and server
from datetime import datetime
from os import path, mkdir


class logger:
    def __init__(self):

        now = datetime.now()
        today = datetime.today()

        # create a file with the days log
        self.file = "log-" + today.strftime("%m-%d-%Y") + ".txt"
        # error handeling not added because of time constraints
        self.outStremam = open(self.file, "a+")

        self.time = now.strftime("%d/%m/%Y %H:%M:%S")

    def info(self, msg):
        self.outStremam.write(f"{self.time} - {msg}\n")

    def warning(self, msg):
        self.outStremam.write(f"{self.time} WARNING - {msg}\n")

    def error(self, msg):
        print(f"Existed program look at <{self.file}> for more information")
        self.outStremam.write(f"{self.time} ERROR - {msg}\n")

    def close(self):
        self.outStremam.close()


if __name__ == "__main__":
    loggerFile = logger()
    loggerFile.info("hello")
    loggerFile.warning("hello")
    loggerFile.error("hello")
    loggerFile.close()
