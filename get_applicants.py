
from createDBandTables import DBConnect, db_execute_fetch
from gdive_util import gsheet
import datetime
import sqlalchemy as sqla
from question_mapper import column_mapper
import numpy as np
import pandas as pd


def get_applicant_data ():
    sid_radar = '1UyEdERDsWi-qwIC0lmJ7lZFh34VXwuxbnTzZDBIAgQE'
    gd = gsheet(sheetid=sid_radar,fauth='gdrive_10acad_auth.json')   
    sname = f'Form responses 1'
    
    try:
        df = gd.get_sheet_df(sname)
        
        print(df.head())
        print(f'------------{sname} df.shape={df.shape}----')
        
    except Exception as e:
        print(f'ERROR: Could not obtain sheet for {sname}',e)
        
    
    return df
def batch_function(year):
      if year == "2021":
          return "batch-4"
      else:
          return "batch-5"

def process_dataframe ():
    app_df = get_applicant_data()
    df = app_df.T 
    df['Timestamp'] = df['Timestamp'].apply(lambda x: datetime.datetime.strptime(x, "%d/%m/%Y %H:%M:%S"))

    df['Year'] = df['Timestamp'].dt.year
    df['Year'] = df['Year'].apply(lambda x: str(x))
    df['Batch'] = df['Year'].apply(batch_function)
    
    df = df.drop(columns=['Year'])
    columns= df.columns.to_list()
    for cols in columns:
        db_col = column_mapper(cols)
        df.rename(columns = {cols:db_col}, inplace = True)
    df = df.replace(r'^\s+$', np.nan, regex=True)
        # print (db_col)
        
      
    print(df.columns)
    # new_df = pd.DataFrame(columns=df.columns)
    # new_df.loc[len(new_df)] = [str("test")] * 41
    return df


def split_dataframe(df, chunk_size ): 
    chunks = list()
    num_chunks = len(df) // chunk_size + 1
    for i in range(num_chunks):
        chunks.append(df[i*chunk_size:(i+1)*chunk_size])
    return chunks



def fromSheetToReview(dbName):

    appliInfo = process_dataframe()
    
    conn, cur = DBConnect(dbName)
    appliInfo['time_stamp'] = appliInfo['time_stamp'].apply(lambda x: str(x))
    data = ()
    


def loadInterviwer():
    dbName = "tenxdb"
    query = "Describe applicant_information"
    df = db_execute_fetch(query, rdf=True, dbName=dbName)
    print(df)
    
    
  
                    
    return df

if __name__ == "__main__":
    process_dataframe ()
    # fromSheetToReview('tenxdb')
    # loadInterviwer()
    # process_dataframe ()
    # fromSheetToReview('tenxdb')
    # loadInterviwer()
