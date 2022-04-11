import json
import sqlite3
import pandas as pd

from utils.displaycard import Job, display_jobs

class SkillSetMatch:
    def __init__(self, connection_to_company_db,
                     dfjob=None,dfmatch=None,
                     path_to_jobs_csv=None,
                     path_to_matched_json=None,
                     ) -> None:
        if dfjob is None and path_to_jobs_csv is not None:
           dfjob = pd.read_csv(path_to_jobs_csv)
        if dfmatch is None and path_to_jobs_csv is not None:        
            dfmatch = pd.read_json(path_to_matched_json)

        jobs_slice = dfjob[['title', 'company', 'industry', 'description', 'apply_link']]
        matched = dfmatch
        skills_series= pd.DataFrame({'skills': matched[matched.columns[0]]['matched_skills']})
        jobs_slice['skills'] = skills_series
        querry ='''
        SELECT company,
        headquarters AS location
        FROM companies
        '''
        company_slice = pd.read_sql(querry, con=connection_to_company_db)

        self.company_jobs_df = jobs_slice.merge(right=company_slice, on='company', how='left')

    def get_match_summary(self, skill_list):
        df = self.company_jobs_df.copy()
        matched_idx = []
        for skill in skill_list:
            for idx in df['skills'].index:
                if skill.lower() in df['skills'][idx].lower():
                    matched_idx.append(idx)
        matched_idx.sort()
        matched_idx = list(set(matched_idx))
        matched_df = df.iloc[matched_idx]

        num_matched_jobs = len(matched_df)
        num_companies = len(matched_df['company'].unique())
        num_locations = len(matched_df['location'].unique())
        
        #print('Number of job matches: {}Number of companies looking the skill set: {}\nNumber of locations: {}'.format(num_matched_jobs, num_companies, num_locations))

        self.matched_df = matched_df

        return "<p style='box-shadow: 0 1px 5px rgba(0, 0, 0, 0.4);padding:30px;text-align:center;font-size:26px;border-radius:10px;'>Number of job matches: <b>{}</b></br>Number of companies looking for the skill set: <b>{}</b></br>Number of locations: <b>{}</b></p>"\
            .format(num_matched_jobs, num_companies, num_locations)

        

    def display_match_details(self):
        display_jobs(self.matched_df.head())
