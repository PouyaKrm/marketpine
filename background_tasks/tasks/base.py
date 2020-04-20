import abc
import multiprocessing
import os
import sys
import threading
from os.path import dirname, abspath

sys.path.append(dirname(dirname(abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'CRM.settings'
import django

django.setup()


class BaseBackgroundTask:

    def __init__(self, name: str = None):
        self.name = name
        self.__event = None
        self.__process = None
        self.pid = -1
        self.thread = None
        self.kill_thread = False

    def start(self):
        # self.__event = multiprocessing.Event()
        # self.__process = multiprocessing.Process(target=self.run_task, kwargs={'event': self.__event})
        # self.__process.start()
        # self.pid = self.__process.pid
        self.thread = threading.Thread(target=self.run_task).start()
        return True

    def set_event_and_join(self):
        # if self.__process is None or not self.__process.is_alive():
        #     return
        # self.__event.set()
        # self.__process.join()
        self.kill_thread = True
        self.thread.join()

    @abc.abstractmethod
    def run_task(self):
        pass

