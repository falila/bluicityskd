import requests
import xml.etree.ElementTree as ET
import collections
import os , traceback,sys
from datetime import datetime
from blu.exception_logger import logger
from queue import Queue
from threading import Thread
from pathlib import Path
from blu.db_wrapper import Wrapper ,Tracker


Notification = collections.namedtuple('Notification',['local_time','coordinates','locat','sensor','data'])

Notification.__new__.__defaults__=(None,None,None,None,None)

from os import listdir
from os.path import isfile, join

class Worker(Thread):

    stop_threads = False
    table_created = False
   
    def __init__(self, number, queue, stop_thread=False, db_string=None):
        Thread.__init__(self)
        self.queue = queue
        self.number = number
        self.stop_threads = stop_thread
        self.db_wrapper = Wrapper(db_string)
        
    def run(self):

        while True:
            if self.stop_threads:
                logger.debug(f"stoping...{self.number}")
                break
            
            # Get the work from the queue and expand the tuple
            logger.debug(f" thread {self.number} getting task form queue")
            directory, filename = self.queue.get()
            try:
                logger.debug(f'thread {self.number} trying to persiste data')
                self.save_to_db(directory, filename)
            finally:
                self.queue.task_done()
                logger.debug(f'thread {self.number} has done')
                #self._close_connection()

            
    def _parseXML(self, xmlfile):
        # create element tree object
        tree = ET.parse(xmlfile)
        # get root element
        root = tree.getroot()
        sensors_notifications = []
        for item in root.findall('./tables/table/row'):
            notif = []
            for child in item:
                if child.attrib['val'] and len(child.attrib['val']) == 10:
                    try:
                        timestamp = datetime.fromtimestamp(int(child.attrib['val']))
                        notif.append(timestamp)
                    except Exception as e:
                        logger.debug(f"attempted to convert timestamp value but failed")
                        logger.debug(e)
                        exc_type, exc_value, exc_tb = sys.exc_info()
                        traceback.print_exception(exc_type, exc_value, exc_tb)
                else :
                    notif.append(child.attrib['txt']) 
            sensors_notifications.append(Notification._make(notif))
        
        return sensors_notifications

    def find_linked_row(self,cp_notification=None, o_notifications=None):
        dual_row = []
        for notif in cp_notification:

            if len(dual_row) == 0 :
                dual_row.append(notif)
                continue
                
            elif len(dual_row) == 1 and dual_row[0].local_time == notif.local_time :
                dual_row.append(notif)
                o_notifications.remove(dual_row[0])
                o_notifications.remove(dual_row[1])
                return dual_row

    def save_to_db(self, directory, filename):
        download_path = os.path.join(directory, filename)
        notifications = self._parseXML(Path(download_path))
        records_to_save = []
        #extract unit nam from filename
        unit_name = filename.split('_')[0]

        nb_notifications = len(notifications)
        print(f"notif {nb_notifications}")

        for i in range(1,nb_notifications//2):
            dual_row = self.find_linked_row(cp_notification=notifications[:], o_notifications=notifications)
            if not dual_row:
                continue
            print(f"in loop {i}")
            print(f"dual: {dual_row}")
            if "CT" in  dual_row[0].data:
                beacon_serial = dual_row[0].data
                beacon_temp =  dual_row[1].data
            else:
                beacon_serial = dual_row[1].data
                beacon_temp =  dual_row[0].data

            records_to_save.append((Tracker(unit_name=unit_name,
                                        coordinates=dual_row[0].coordinates,
                                        locat=dual_row[0].locat ,sensor_serial= beacon_serial, sensor_temp= beacon_temp, local_time=dual_row[0].local_time)))
            
        
        self.db_wrapper.add_records(records_to_save)
        logger.debug(f"{len(records_to_save)} records saved")
    


if __name__ == "__main__":
    pass
