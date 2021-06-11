import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials as sac
import pandas as pd

def gsheet2df(spreadsheet_name, sheet_num):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials_path = 'appli.json'

    credentials = sac.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(credentials)

    sheet = client.open(spreadsheet_name).get_worksheet(sheet_num).get_all_records()
    df = pd.DataFrame.from_dict(sheet)
    df.to_csv('applicants_information.csv')
    return df

gsheet2df('10 Academy Batch 4 Application form (Responses)', 0)