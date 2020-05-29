import csv
import requests
import xml.etree.ElementTree as ET
import collections
import sqlite3
from sqlite3 import Error

Notification = collections.namedtuple('Notification',['Speed','Coordinates','Locat','Sensor','valuess','Timess'])

Notification.__new__.__defaults__=(None,None,None,None,None,None)

conn = None

sql = "CREATE TABLE IF NOT EXISTS NOTIFICATION ( \
	Speed text NOT NULL,\
	Coordinates text,\
	Locat text,\
	Sensor text,\
	valuess text,\
	Timess text);"

def load_notification_from_email():
    pass
        
def parseXML(xmlfile):
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


def savetodb(notifications):
    """Save notifications """  
    print("saving....") 
    for notif in notifications:
        values = tuple(notif._asdict().values())
        keys = str(notif._fields).replace("'","")
        insert_notification(conn, values)
    conn.commit()

def create_connection(db_file):
    """create a database connection to a SQLite database"""
    global conn
    conn = None
    try:
        print("creating connection")
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn
    
def close_connection():
    global conn
    if conn:
        try:
            conn.close()
        except Error as e:
            print(e)
        finally:
            conn = None


def create_table(conn=None, sql=None):
    if not conn:
        create_connection("db_file.db")
    cursor = conn.cursor()
    cursor.execute(sql)



def insert_notification(conn=None, data=None):
    """insert notification"""
    cursor = conn.cursor()
    _sql = ''' INSERT INTO NOTIFICATION(Speed, Coordinates, Locat, Sensor, valuess, Timess)
              VALUES(?,?,?,?,?,?) '''
    #print("inserting...")
    cursor.execute(_sql, data)
    #print(cursor.lastrowid)

def sync_notifcation():
     main()

def main():
    global sql
    notifications = parseXML('VT53001.xml')
    conn = create_connection("db_file.db")
    #print(notifications)
    create_table(conn, sql)
    savetodb(notifications)       
    
if __name__ == "__main__":
    main()