from __future__ import print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
# from . import db_creds
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'creds.json'

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1ZZGVwnOgCkglTk5WHS6yXQkLNjsolbMmXilCbWsrGuo'
SAMPLE_RANGE_NAME = 'test!A1:D1'

DATABASE = {
    'drivername': 'postgresql',
    'host': 'localhost',
    'port': '5432',
    'username': 'postgres',
    'password': '1234',
    'database': 'postgres'
    }


DeclarativeBase = declarative_base()

class Purchase(DeclarativeBase):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True)
    number = Column('number', Integer)
    cost_dol = Column('Cost in dollars', Integer)
    # deliver = Column('Delivery date', DateTime)
    # cost_rub = Column('Cost in rubles', Integer)

    def __repr__(self):
        return f'{self.number}'


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    # creds = None
    # creds = service_account.Credentials.from_service_account_file(
    #     SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # try:
    #     service = build('sheets', 'v4', credentials=creds)

    #     # Call the Sheets API
    #     sheet = service.spreadsheets()
    #     result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #         range=SAMPLE_RANGE_NAME).execute()

    #     print(result)
    #     values = result.get('values', [])

    #     if not values:
    #         print('No data found.')
    #         return

    #     print(values)
        
    # except HttpError as err:
    #     print(err)

    engine = create_engine(
        'postgresql+psycopg2://{user}:{password}@{host}/{base}'.format(
            user='postgres',
            password='1234',
            host='localhost',
            base='postgres'
        )
    )
    DeclarativeBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    new_purchase = Purchase(number=1, cost_dol=2)
    session.add(new_purchase)
    session.commit()
    for prch in session.query(Purchase):
        print(prch)



if __name__ == '__main__':
    main()