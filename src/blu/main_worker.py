import email
import imaplib
import os , traceback ,sys
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

    logger.info(f"gmail login")
    # get list of email subjects from INBOX folder
    with MailBox('imap.gmail.com').login(email, password) as mailbox:
            #subjects = [msg.subject for msg in mailbox.fetch('(SEEN)')]
            _result_iterator = mailbox.fetch('(UNSEEN)')
            for msg in _result_iterator:

                for att in msg.attachments:  # list: [Attachment]
                    ext = os.path.splitext(att.filename)[-1].lower()
                    if ext == ".xml":
                        logger.info(f"file found {att.filename}")
                        download_attachment(trackerfile_dir_path, att.filename, att.payload)
                        file_list.append(att.filename)
                    else:
                        # logger.info(f'DO NOT PROCESS -- {att.filename}')
                        pass
            #marked unseen email as seen
            logger.info(f"marked unseen email as seen")
            mailbox.seen(_result_iterator, True)
            logger.info("emails treatment is done !")
    #mailbox.logout()

def clear_download_dir():
    logger.debug("attempt to clean downloaded folder")
    import glob, os, os.path

    filelist = glob.glob(os.path.join(trackerfile_dir_path, "*.xml"))
    logger.debug(f"download folder {filelist} ")
    try:
        for f in filelist:
            logger.debug(f"deleting {f} ")
            os.remove(f)
    except Exception as e:
        logger.debug(e)
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)


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
    
    if not gmail_user or not gmail_password:
        logger.debug(f"Couldn't find gmail_password or gmail_user configuration environment variable {db_connexion_url}")
        raise Exception("Couldn't find gmail_password or gmail_user configuration environment variable!")
  

    # Create a queue to communicate with the worker threads
    queue = Queue()
        # Create 8 worker threads
    worker_list = []
    for x in range(2):
        worker = Worker(x,queue,db_string=db_connexion_url)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
        worker_list.append(worker)
        # Put the tasks into the queue as a tuple

    tracker_file_dir = setup_download_dir()

    while True :
        ts = time()
        
        try:
            clear_download_dir()
            fetch_emails(tracker_file_dir,email=gmail_user, password=gmail_password)
        except Exception as e :
            logger.debug(e)
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)

        if len(file_list) > 0 :
            # Put the tasks into the queue as a tuple
            for _file in file_list:
                logger.debug('Queueing {}'.format(_file))
                queue.put((trackerfile_dir_path, _file))
            
            file_list = []
        
            logger.info('Took %s seconds', time() - ts)
        else:
            logger.info('No files have been found')
        sleeper.sleep(240) # 4 min
        logger.info('Re-starting')

if __name__ == "__main__":
    main()
