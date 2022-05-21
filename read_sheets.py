from __future__ import print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import sqlalchemy as sa
import datetime as dt
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'creds.json'

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1ZZGVwnOgCkglTk5WHS6yXQkLNjsolbMmXilCbWsrGuo'
SAMPLE_RANGE_NAME = 'test!A2:D'

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

    id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column('number', sa.Integer)
    cost_dol = sa.Column('Cost in dollars', sa.Integer)
    deliver = sa.Column('Delivery date', sa.Date, default=sa.func.now())
    cost_rub = sa.Column('Cost in rubles', sa.Integer)

    def __repr__(self):
        return f'{self.number}'


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=SAMPLE_RANGE_NAME).execute()

        values = result.get('values', [])

        if not values:
            print('No data found.')
            return
        
    except HttpError as err:
        print(err)

    engine = sa.create_engine(
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

    for value in values:
        query = sa.select(
            Purchase.id,
            Purchase.number,
            Purchase.cost_dol,
            Purchase.deliver,
            Purchase.cost_rub
        ).where(Purchase.id==value[0])
        exec = session.execute(query).first()
        if exec is None:
            date = dt.date(*map(int, value[3].split('.')[::-1]))
            session.add(
                Purchase(
                    id = value[0],
                    number = value[1],
                    cost_dol = value[2],
                    deliver = date,
                    cost_rub = value[2]
                )
            )
            session.commit()
        else:
            value = [*map(int, value[:-1])]\
                + [dt.date(*map(int, value[3].split('.')[::-1]))]
            if list(exec[:-1]) != value:
                pass

            





if __name__ == '__main__':
    main()