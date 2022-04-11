import pandas as pd
import json
import glob
import datetime

import sys
import os

sys.path.append(os.path.abspath(os.path.join('../')))

import model.spacy_model as spm
from utils.s3_utils import upload_file


def convert_2_timestamp(column, data):
    """convert from unix time to readable timestamp
        args: column: columns that needs to be converted to timestamp
                data: data that has the specified column
    """
    if column in data.columns.values:
        timestamp_ = []
        for time_unix in data[column]:
            if time_unix == 0:
                timestamp_.append(0)
            else:
                a = datetime.datetime.fromtimestamp(float(time_unix))
                timestamp_.append(a.strftime('%Y-%m-%d %H:%M:%S'))
        return timestamp_
    else:
        print(f"{column} not in data")


def parse_data():
    # specify path to get json files
    path = "slack_export/b4jobsprocess-updates/"
    combined = []
    try:
        for json_file in glob.glob(f"{path}*.json"):
            with open(json_file, 'r') as slack_data:
                combined.append(slack_data)
        print("Total Days ", len(combined))
    except Exception as e:
        print(e)
        print('Parser stopped!!')

    data = []
    for i in combined:
        slack_data = json.load(open(i.name, 'r', encoding='utf-8'))

        for row in slack_data:
            if 'attachments' not in row.keys():
                continue
            else:
                try:
                    texts = (row['text'])
                    ts = (row['ts'])
                    author_name = (row['attachments'][0]['author_name'])
                    fields = row['attachments'][0]['fields']
                    for i in range(len(fields)):
                        if fields[i]['title'] == "Name of company":
                            src = fields[i]['value']
                        else:
                            src = 'No Src'
                        if fields[i]['title'] == "How did you find this job":
                            company = fields[i]['value']
                        else:
                            company = 'Not Specified'
                        if fields[i]['title'] == "Full job description":
                            jd = fields[i]['value']
                        else:
                            jd = 'No JD'
                except Exception as e:
                    print(e)
            data.append(
                {
                    'texts': texts,
                    'times_posted': ts,
                    'author_name': author_name,
                    'fields': fields,
                    'jd': jd,
                    'company': src,
                    'src': company
                }
            )

    # save to pandas dataframe
    df = pd.DataFrame(data)
    df['updated_time'] = convert_2_timestamp('times_posted', df)
    df.drop('times_posted', axis=1, inplace=True)
    df = df.query("author_name != 'Arun Sharma'")
    # print(f"Total Jobs found Before Cleaning:: {len(df)}")
    df = df.query("jd != 'No JD' ").reset_index(drop=True)
    # df = df.query("src != 'No Src' ")
    # print(f"Total Jobs found After Cleaning:: {len(df)}")
    print(df.tail(10))
    # df.to_csv('slack_data.csv', index=False)

    return df


if __name__ == "__main__":
    filename = 'jobs_skills.csv'
    nlp = spm.get_skill_nlp()

    # ndays to keep cache of profile skills extracts
    pj = spm.pjmatch(nlp=nlp, pcol='profile_text', ndays=2)

    # extract job skulls
    df = parse_data()
    job_skills = []
    for job_desc in df['jd']:
        job_skill = pj.get_skills(job_desc)
        job_skills.append({"job_skill": job_skill})

    print("\nJob Skills")
    print(job_skills)
    job_df = pd.DataFrame(job_skills)
    job_df['author'] = df['author_name']
    job_df.to_csv(f'{filename}', index=False)

    # upload_file(f"{filename}", "jobmodel", f'traineesFoundJobs/{filename}')
