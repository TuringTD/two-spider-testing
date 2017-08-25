from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ImageBase(Base):
    __tablename__ = 'test_table'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    url = Column(String(200), nullable=False)
    img_src = Column(String(200), nullable=False)

    @classmethod
    def set_table_name(self, table_name):
        assert isinstance(table_name, str)
        if len(table_name) > 3 and len(table_name) <= 10:
            self.__tablename__ = table_name
        else:
            raise Exception('table name: %s illegal')


class DataOperateModel(object):

    def __init__(self, db_url, data_base):
        self._db_url = db_url
        self._data_base = data_base
        self.counter = 0

    def sql_setup(self):
        print(self._data_base.__tablename__)
        self._engine = create_engine(self._db_url)
        self._data_base.metadata.create_all(self._engine)
        self._session = sessionmaker(bind=self._engine)()

    def save_data(self, data):
        if data:
            for item in data:
                try:
                    assert isinstance(item, self._data_base)
                    if self._session:
                        self._session.add(item)
                        self.counter += 1
                except Exception as e:
                    print('Error:', item, e)
                    continue

            self._session.commit()
            print('<MYSQL> Insert %d message to table: %s' % (self.counter, self._data_base.__tablename__))


    def sql_teardown(self):
        self._session.close()
