from sqlalchemy import create_engine  
import sqlalchemy as sa
from sqlalchemy import Column, String ,Integer , DateTime
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
Base = declarative_base()

class Tracker(Base):  
        __tablename__ = 'Tracker'

        ids =  Column(Integer,primary_key=True)
        speed = Column(String)
        coordinates = Column(String)
        locat = Column(String)
        sensor = Column(String)
        data = Column(String)
        local_time = Column(DateTime)
        time_created = Column(DateTime, server_default=sa.sql.func.now())

        def __repr__(self):
            return "<Tracker(sensor='{}', speed='{}', locat={} , value={}, times={})>"\
                .format(self.sensor, self.speed, self.locat ,self.data, self.local_time)

class Wrapper():
    global Base

    def __init__(self,db_string):
        self.db = create_engine(db_string)  
        self.Base = Base
        #Session = sessionmaker(self.db)  
        #self.session = Session()
        self.Base.metadata.create_all(self.db)
    
    

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around add records."""
        Session = sessionmaker(self.db) 
        session = Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add_records(self, trackers_list=None):

        with self.session_scope() as session:
            for tr in trackers_list:
                session.add(tr)  

if __name__ == "__main__":
    # for testing
    pass