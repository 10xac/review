import os, sys
import re 
from functools import reduce

path='./'
print(path in sys.path)
if not path in sys.path:
    sys.path.append(path)
from gcdb import *


sid_w0 = '1a_SYUzxeAePL_bRKAqck7_lvlbHDF5su0fxz0td8ScY'
sid_lb_w1_12 = '1-stg9I0r58ZA4kapXqEmIVDdUKEcW1hruYMudCp7t7c'
sid_score_w1_12 = '1a_anQkWZyq09qMYTNETGz4kxH-79LxspOq6kG5JexQ8'
sid_emap = '1GpNqueyGZeV07FuVpPPMoC6e-5SEfldibcHrdzTETSc'
sid_badge = '1zAA_SZEc0j-55pzM9dzz_k7bfnq0HMpk0S-YapRgQN4'


def get_columns_like(df,pattern):
    '''find column names with pattern'''
    if not isinstance(pattern, (list, tuple) ):
        pattern = [pattern]
    cols = []
    for p in pattern:
        cols.extend([x for x in df.columns if p in x])
        
    return cols

def drop_columns_like(df,pattern):
    '''find column names with pattern, and drop them'''
    cols = get_columns_like(df,pattern)  
    return df.drop(columns=cols)

def sum_prev_score(dfin, **kwargs):
    df = dfin.copy()
    dfout = pd.DataFrame()
    
    if 'userId' in df.columns:
        dfout['userId'] = df['userId']
    else:
        print('Warning: userId not found in dfin ... returning empty dataframe')
        return dfout
        
    oldscorecol = kwargs.get('oldscorecol','past_weeks_score_norm')
    scorecol = kwargs.get('scorecol','final_score_norm')
    
    dfout[oldscorecol] = 0
    if  oldscorecol in df.columns:
        dfout[oldscorecol] += df[oldscorecol].astype({oldscorecol:float}) 
        
    if  scorecol in df.columns:
        dfout[oldscorecol] += df[scorecol].astype({scorecol:float}) 
        
    return dfout

def get_week_name_map():
    return {1:'1',2:'2',3:'3',4:'4-5',
            6:'6',7:'7',8:'8',9:'9-10',
            11:'11'}

def get_weekly_scores(week, **kwargs):
    
    oldscorecol = kwargs.get('oldscorecol','past_weeks_score_norm')
    scorecol = kwargs.get('scorecol','final_score_norm') 
    verbose = kwargs.get('verbose',0)
    
    #
    index_col = 'userId'
    name_col = 'fullName'
    email_col = 'email'
    
    gst = gdr.gsheet(sheetid=sid_score_w1_12,fauth='admin-10ac-service.json')
    
    loop = 0
    for w,n in get_week_name_map().items():
        if w > week:
            break
        
        #
        scol_week = f"{scorecol}_{w}"
        use_cols = [index_col,name_col,email_col]
        use_cols.append(scol_week)
        
        #            
        df = gst.get_sheet_df(f'Week{w}').T.rename(columns={scorecol:scol_week})
        if verbose>=0:
            print(f'Got score from week={w}; shape={df.shape}.')        
        
        #
        if loop==0:
            df_merged = df[use_cols]
        else:
            df_merged = pd.merge(df_merged,df[[index_col,scol_week]],on=index_col, how='right')
            
        loop += 1
        
    return  df_merged.set_index(index_col, drop=True)

def get_topn_score_sum(df=None, n=8, **kwargs):
    
    oldscorecol = kwargs.get('oldscorecol','past_weeks_score_norm')
    scorecol = kwargs.get('scorecol','final_score_norm')
    verbose = kwargs.get('verbose',-1)
    
    if df is None:
        df = get_week_score_table()
        
    cols = get_columns_like(df, scorecol)
    topn_sum = {}
    loop=0
    for ix, row in df.iterrows():
        S = row[cols].astype(float)
        Sn = S.nlargest(n, keep='all').mean() #keep duplicates        
        topn_sum[ix] = Sn
        #
        if verbose>0:
            if loop==0:
                print('all: ',S)
                print(f'top {n}: ',S.nlargest(n, keep='all'))
                print(f'sum top {n}: ',Sn)
            loop += 1
        
    dftopn = pd.DataFrame.from_dict(topn_sum,orient='index',columns=['final_score_norm'])
    dftopn.index.name='userId'
    dftopn = df[['email','fullName']].join(dftopn).reset_index()
    return dftopn
        
    
        
def get_last_week_score(week,plot=False, **kwargs):
    if week>1:
        gst = gdr.gsheet(sheetid=sid_score_w1_12,fauth='admin-10ac-service.json')
        if week in [6,11]:
            past_week = f'Week{week-2}'
        else:
            past_week = f'Week{week-1}'

        #
        print(f'Getting score from week={past_week}...')
        dfall_old = gst.get_sheet_df(past_week).T    

        #
        dfscore_old = sum_prev_score(dfall_old,**kwargs)
        
        if plot:
            plot_score(dfscore_old, x=oldscorecol,xcut=10)

    else:
        dfscore_old = None    
        
    return dfscore_old
   
def get_badge_score(week, **kwargs):
    try:
        gst = gdr.gsheet(sheetid=sid_badge,fauth='admin-10ac-service.json')
        if week==4:        
            dfbadge = gst.get_sheet_df(f'Week4-5').T
        else:
            dfbadge = gst.get_sheet_df(f'Week{week}').T

        dfbadge = dfbadge.astype({'shift':float,'multiplier':float}).fillna({'shift':0,'multiplier':1})   

        print('dfbadge', dfbadge.shape, dfbadge.columns)
    except:
        dfbadge = None
        
    return dfbadge

def get_email_mapper():
    #get email mapper
    gst = gdr.gsheet(sheetid=sid_emap,fauth='admin-10ac-service.json') 
    dfemap = gst.get_sheet_df(f'Week1to12').T
    #
    emap = dfemap.set_index('rc_email',drop=True).to_dict()['gclass_email']
    
    return emap