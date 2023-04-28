import psutil
import threading
import time

class MemLogger:
    '''A simple memory logger to record and retrieve
    the memory usage of a program over time.'''
    
    def __init__(self, interval):
        '''Initializes a new MemLogger. The 'interval'
        property allows for setting how often the
        memory usage is recorded.'''
        self.interval = interval
        self.log = []
        
    def __log(self):
        self.keep_logging = True
        while self.keep_logging:
            amt = psutil.Process().memory_info().rss
            self.log.append((time.time(), amt))
            time.sleep(self.interval)
        
    def start(self):
        '''Start logging memory usage.'''
        t = threading.Thread(target=self.__log)
        t.start()
    
    def stop(self):
        '''Stop logging memory usage.'''
        self.keep_logging = False
        
    def get_log(self):
        '''Retrieve the memory log.'''
        return self.log
        