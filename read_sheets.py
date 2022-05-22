from __future__ import print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import sqlalchemy as sa
import datetime as dt
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
import xml.etree.ElementTree as ET
import time


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'creds.json'

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1ZZGVwnOgCkglTk5WHS6yXQkLNjsolbMmXilCbWsrGuo'
SAMPLE_RANGE_NAME = 'test!A2:D'

DeclarativeBase = declarative_base()

class Purchase(DeclarativeBase):
    __tablename__ = 'purchases'

    id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column('number', sa.Integer)
    cost_dol = sa.Column('Cost in dollars', sa.Float)
    deliver = sa.Column('Delivery date', sa.Date, default=sa.func.now())
    cost_rub = sa.Column('Cost in rubles', sa.Float)

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
        r = requests.get("https://www.cbr.ru/scripts/XML_daily.asp").text
    except (requests.ConnectionError,
    requests.HTTPError,
    requests.Timeout):
        print('Не удалось подключиться в ЦБ.')
        return
    tree = ET.fromstring(r)
    course = tree.find('./Valute[@ID="R01235"]/Value').text.replace(',', '.')
    course = float(course)

    engine = sa.create_engine(
        'postgresql+psycopg2://{user}:{password}@{host}/{base}'.format(
            user='postgres',
            password='1234',
            host='database',
            base='postgres'
        )
    )
    DeclarativeBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    while(True):

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
        del_list = [id[0] for id in session.query(Purchase.id).all()]

        for value in values:
            if '' in value:
                continue
            try:
                del_list.remove(int(value[0]))
            except ValueError:
                pass
            except IndexError:
                continue
            try:
                date = dt.date(*map(int, value[3].split('.')[::-1]))
                int(value[0])
                int(value[1])
                float(value[2])
            except ValueError as e:
                print(f'Invalid data in № {value[0]}, {e}')
                continue
            query = sa.select(
                Purchase.id,
                Purchase.number,
                Purchase.cost_dol,
                Purchase.deliver,
                Purchase.cost_rub
            ).where(Purchase.id==value[0])
            exec = session.execute(query).first()

            if exec is None:
                session.add(
                    Purchase(
                        id = value[0],
                        number = value[1],
                        cost_dol = value[2],
                        deliver = date,
                        cost_rub = round(float(value[2]) * course, 2)
                    )
                )
                session.commit()
            else:
                value = [*map(int, value[:-2])]\
                    + [float(value[-2])]\
                    + [date]
                if list(exec[:-1]) != value:
                    print(f'Changed id {value[0]}')
                    pr = session.get(Purchase, value[0])
                    pr.number = value[1]
                    pr.cost_dol = value[2]
                    pr.deliver = date
                    pr.cost_rub = round(float(value[2]) * course, 2)
                    session.commit()

        for id in del_list:
            session.delete(session.get(Purchase, id))
        session.commit()
        print(f'Updated {dt.datetime.now().strftime("%H:%M:%S")}')
        time.sleep(15)

            





if __name__ == '__main__':
    main() 
