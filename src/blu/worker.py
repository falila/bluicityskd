import email
import imaplib
import os
import shutil
from time import time
import time as sleeper
from pathlib import Path
from blu.exception_logger import logger
from blu.db import db_update_Worker, sql
from queue import Queue


types = {'xml'}
tracker_file_dirname = 'trakerfiles'
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
root_dir = Path(base_dir, '.')
trackerfile_dir_path = str(Path(root_dir,tracker_file_dirname).resolve())
file_list = []
stop_threads = False

def download_attachment(directory, file_name, payload):
    #download_path = directory / os.path.basename(file_name)
    download_path = os.path.join(directory, file_name)
    logger.info(f' file dir path {download_path}')
    if not os.path.isfile(download_path):
        with open(download_path , 'wb+') as f:
            f.write(payload)
        logger.info('Downloaded %s', file_name)
    else:
        logger.info(f'this file already exist')


def setup_download_dir():
    download_dir = Path('trakerfiles')
    if not download_dir.exists():
        download_dir.mkdir()
    return download_dir

def fetch_emails(tracker_file_dir=None):
    from imap_tools import MailBox
    logger.info(f'fetching emails')
    logger.debug(f' tracker file repo {trackerfile_dir_path}')

    # get list of email subjects from INBOX folder
    with MailBox('imap.gmail.com').login('bluicity.test@gmail.com', 'Bluicitytest') as mailbox:
            #subjects = [msg.subject for msg in mailbox.fetch('(SEEN)')]
            _result_iterator = mailbox.fetch('(UNSEEN)')
            for msg in _result_iterator:

                for att in msg.attachments:  # list: [Attachment]
                    ext = os.path.splitext(att.filename)[-1].lower()
                    if ext == ".xml":
                        download_attachment(trackerfile_dir_path, att.filename, att.payload)
                        file_list.append(att.filename)
                        pass
                    else:
                        # logger.info(f'DO NOT PROCESS -- {att.filename}')
                        pass
            #marked unseen email as seen
            mailbox.seen(_result_iterator, True)
            logger.info("logout...")
    mailbox.logout()

def clear_download_dir():
    logger.debug("attempt to clean downloaded folder")
    import glob, os, os.path

    filelist = glob.glob(os.path.join(trackerfile_dir_path, "*.xml"))
    for f in filelist:
        os.remove(f)


def main():
    global file_list , stop_threads
    file_list = []

    # Create a queue to communicate with the worker threads
    queue = Queue()
        # Create 8 worker threads
    worker_list = []
    for x in range(4):
        worker = db_update_Worker(x,queue,sql)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
        worker_list.append(worker)
        # Put the tasks into the queue as a tuple

    ts = time()
    client_id = os.getenv('db_password')
    if not client_id:
        #raise Exception("Couldn't find IMGUR_CLIENT_ID environment variable!")
        print("env variable not set")

    while True :
        tracker_file_dir = setup_download_dir()
        
        try:
            clear_download_dir()
            fetch_emails(tracker_file_dir)
        except Exception as e :
            logger.debug(e)

        if len(file_list) > 0 :
            # Put the tasks into the queue as a tuple
            for _file in file_list:
                logger.debug('Queueing {}'.format(_file))
                queue.put((trackerfile_dir_path, _file))
            # Causes the main thread to wait for the queue to finish processing all the tasks
            file_list = []
        
            logger.info('Took %s seconds', time() - ts)
        sleeper.sleep(60)
        logger.info('Re starting')

if __name__ == "__main__":
    main()
