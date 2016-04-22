class Logger:
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    def __init__(self):
        self.log_level = Logger.DEBUG
    def debug(self, msg):
        if self.log_level <= Logger.DEBUG:
            print "DEBUG:", msg
    def info(self, msg):
        if self.log_level <= Logger.INFO:
            print "INFO: ", msg
    def warn(self, msg):
        if self.log_level <= Logger.WARN:
            print "WARN: ", msg
    def error(self, msg):
        if self.log_level <= Logger.ERROR:
            print "ERROR:", msg

Log = Logger()
