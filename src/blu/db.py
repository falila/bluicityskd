import csv
import requests
import xml.etree.ElementTree as ET
import collections
import sqlite3
import os
from sqlite3 import Error
from blu.exception_logger import logger
from queue import Queue
from threading import Thread
from pathlib import Path



Notification = collections.namedtuple('Notification',['Speed','Coordinates','Locat','Sensor','valuess','Timess'])

Notification.__new__.__defaults__=(None,None,None,None,None,None)

sql = "CREATE TABLE IF NOT EXISTS NOTIFICATION ( \
	Speed text NOT NULL,\
	Coordinates text,\
	Locat text,\
	Sensor text,\
	valuess text,\
	Timess text);"


def sync_notifcation():
    pass

from os import listdir
from os.path import isfile, join
#onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

class db_update_Worker(Thread):

    stop_threads = False
    table_created = False
   
    def __init__(self, number, queue, sql, stop_thread=False):
        Thread.__init__(self)
        self.queue = queue
        self.sql = sql
        self.number = number
        self.stop_threads = stop_thread
        self.conn = None
        self.table_created = False
        

    def run(self):
        if not self.table_created:
            self._create_table()
            self.table_created = True
        else :
            self._create_connection()

        while True:
            if self.stop_threads:
                logger.debug(f"stoping...{self.number}")
                break
            
            # Get the work from the queue and expand the tuple
            logger.debug(f" thread {self.number} getting task form queue")
            directory, filename = self.queue.get()
            try:
                self.filecontent_to_db(directory, filename, self.sql)
            finally:
                self.queue.task_done()
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
                notif.append(child.attrib['txt'])       
            sensors_notifications.append(Notification._make(notif))
        
        return sensors_notifications


    def savetodb(self, notifications):
        """Save notifications """  
        print("saving....") 
        for notif in notifications:
            values = tuple(notif._asdict().values())
            keys = str(notif._fields).replace("'","")
            self.insert_notification(values)
        self.conn.commit()

    def _create_connection(self, db_file):
        """create a database connection to a SQLite database"""

        #os.getenv('user_name')
        #os.getenv('db_password')
        #os.getenv('db_rul')
        try:
            if not self.conn :
                print("creating connection")
                self.conn = sqlite3.connect(db_file)
                print(sqlite3.version)
        except Error as e:
            print(e)
        return self.conn
        
    def _close_connection(self):
    
        if self.conn:
            try:
                conn.close()
            except Error as e:
                logger.debug(e)
            finally:
                self.conn = None


    def _create_table(self):
        print("attempting to creat data table structure")
        if not self.conn:
            self._create_connection("db_file.db")
        cursor = self.conn.cursor()
        cursor.execute(self.sql)
        print("table structure created")


    def insert_notification(self, data=None):
        """insert notification"""
        cursor = self.conn.cursor()
        _sql = ''' INSERT INTO NOTIFICATION(Speed, Coordinates, Locat, Sensor, valuess, Timess)
                VALUES(?,?,?,?,?,?) '''
        logger.debug("inserting...")
        cursor.execute(_sql, data)
        #cursor.close()
        logger.debug(data)
        logger.debug(cursor.lastrowid)

    def filecontent_to_db(self, directory, filename,sql):
        download_path = os.path.join(directory, filename)
        notifications = self._parseXML(Path(download_path))
        self.savetodb(notifications)
           
    
if __name__ == "__main__":
    pass