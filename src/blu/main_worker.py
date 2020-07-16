import email
import imaplib
import os
import shutil
from time import time
import time as sleeper
from pathlib import Path
from blu.exception_logger import logger
from blu.worker import Worker
from queue import Queue

tracker_file_dirname = 'trakerfiles'
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
root_dir = Path(base_dir, '.')
trackerfile_dir_path = str(Path(root_dir,tracker_file_dirname).resolve())
file_list = []
stop_threads = False

def download_attachment(directory, file_name, payload):
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

def fetch_emails(tracker_file_dir=None, email=None, password=None):
    from imap_tools import MailBox
    logger.info(f'fetching emails')
    logger.debug(f' tracker file repo {trackerfile_dir_path}')

    # get list of email subjects from INBOX folder
    with MailBox('imap.gmail.com').login(email, password) as mailbox:
            #subjects = [msg.subject for msg in mailbox.fetch('(SEEN)')]
            _result_iterator = mailbox.fetch('(UNSEEN)')
            for msg in _result_iterator:

                for att in msg.attachments:  # list: [Attachment]
                    ext = os.path.splitext(att.filename)[-1].lower()
                    if ext == ".xml":
                        download_attachment(trackerfile_dir_path, att.filename, att.payload)
                        file_list.append(att.filename)
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
    logger.debug('Starting main worker...')
    global file_list , stop_threads
    file_list = []
    logger.debug('getting env variable')
    db_connexion_url = os.getenv('B_DB_URL')
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_PASSWORD')

    if not db_connexion_url:
        logger.debug(f"Couldn't find db configuration environment variable {db_connexion_url}")
        raise Exception("Couldn't find db configuration environment variable!")
    
    if not gmail_user or gmail_password:
        logger.debug(f"Couldn't find gmail_password or gmail_user configuration environment variable {db_connexion_url}")
        raise Exception("Couldn't find gmail_password or gmail_user configuration environment variable!")
  

    # Create a queue to communicate with the worker threads
    queue = Queue()
        # Create 8 worker threads
    worker_list = []
    for x in range(4):
        worker = Worker(x,queue,db_string=db_connexion_url)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
        worker_list.append(worker)
        # Put the tasks into the queue as a tuple

    while True :
        ts = time()
        tracker_file_dir = setup_download_dir()
        
        try:
            clear_download_dir()
            fetch_emails(tracker_file_dir,email=gmail_user, password=gmail_password)
        except Exception as e :
            logger.debug(e)

        if len(file_list) > 0 :
            # Put the tasks into the queue as a tuple
            for _file in file_list:
                logger.debug('Queueing {}'.format(_file))
                queue.put((trackerfile_dir_path, _file))
            
            file_list = []
        
            logger.info('Took %s seconds', time() - ts)
        sleeper.sleep(60)
        logger.info('Re-starting')

if __name__ == "__main__":
    main()
