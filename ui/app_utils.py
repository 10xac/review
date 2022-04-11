import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join("../")))
from db.atable import get_table
import model.spacy_model as spm


cookie_value = "LI_AT_COOKIE=AQEDAR4F42UEBUWKAAABfXpdp7sAAAF9nmoru1YAg43xB1TocCauDt_x_m-YCBtkZm5P2Vrd5diMXtErb7FpyzroEnKZ2IMyrAaNxdsn4x0B3t6ydZLcwDjKUWQSR0Wal0NAK0pGhg0SBdZdN6LmWeAv"


def transform_trainees_data():
    try:
        _, trainees = get_table(
            name_list=["B4-Trainees"], fields={"B4-Trainees": ["Name", "Email", "Tags"]}
        )
        # fill missing values with DataEng
        trainees["Tags"].fillna("DataEng", inplace=True)
        # convert Tags to str so it can be separated based on keywords
        trainees["Tags"] = trainees["Tags"].apply(lambda x: "".join(map(str, x)))
        trainees["TagId"] = trainees["Tags"].apply(
            lambda x: 2 if x in ["MLEngDataEng", "DataEng"] else 1
        )
        print(trainees.columns.values)

        return trainees
    except Exception as e:
        print("An Error Occured", e)


def get_jobs_linkedln():
    try:
        # this will produce a jobs.csv file
        os.system(f"python ../jdcrawl/linkedln_scraper.py")
        jobs = pd.read_csv("jobs.csv")
        return jobs
    except Exception as e:
        print("Error Occured, failed to get jobs", e)
        sys.exit()


def transform_linkedln_jobs():
    # get jobs from linkedln
    jobs = get_jobs_linkedln()
    jobs.drop_duplicates(subset=["description"], inplace=True)

    return jobs


def get_trainees_jobs_based_on_category(jobs, trainees):
    # get jobs based on tag
    # identifying MLE jobs
    mle_jobs = jobs[
        jobs["title"].str.contains(
            "Machine | Machine Learning Engineer | Software Engineer"
        )
    ]
    # Identifying DE jobs
    de_jobs = jobs[
        jobs["title"].str.contains(
            "Data Engineer | Analytics Engineer | Data Platform Engineer"
        )
    ]
    # get trainees based on tag
    mle_trainees = trainees.query("TagId == 1")
    de_trainees = trainees.query("TagId == 2")

    try:
        # merge jobs with trainees
        de_jobs_trainees = de_jobs.merge(
            de_trainees, left_on="job_title_id", right_on="TagId"
        )
        mle_jobs_trainees = mle_jobs.merge(
            mle_trainees, left_on="job_title_id", right_on="TagId"
        )
        print("DE Role shape:: ", de_jobs_trainees.shape)
        print("MLE Role shape:: ", mle_jobs_trainees.shape)
        print(de_jobs_trainees.columns.values)

        return mle_jobs, mle_jobs_trainees, de_jobs, de_jobs_trainees

    except Exception as e:
        print("An Error Occurred while Merging", e)


def get_skills_per_jobs(trainees_jobs_df, jobs):
    nlp = spm.get_skill_nlp()

    # ndays to keep cache of profile skills extracts
    pj = spm.pjmatch(nlp=nlp, pcol="profile_text", ndays=100)

    try:
        skills = pd.DataFrame()
        for job_desc in jobs["description"]:
            # extract the skills
            job_skill = pj.get_skills(job_desc)
            if len(job_skill) < 1:
                continue
            else:
                # match skills with trainees skills
                n_df = pj.job_candidates(job_skill)
                n_df = n_df.query("match_degree >= 80").reset_index(drop=True)
                n_df = n_df.loc[~n_df.index.duplicated(keep="first")]
                skills = skills.append(n_df, ignore_index=True)
        # join extracted skills with trainees_df_jobs
        skills = skills.merge(trainees_jobs_df, left_on="name", right_on="Name")
        skills = skills.sort_values(
            by=["name", "match_degree"], ascending=[False, False], ignore_index=True
        )
        return skills
    except Exception as e:
        print("An Error Occured in skills match", e)
        sys.exit()


def get_top_5_matched_jobs(skills):
    # select top 5 matched jobs MLE
    try:
        jobs_skills = skills.iloc[
            skills.groupby("Name")["match_degree"].nlargest(5).index.get_level_values(1)
        ]

        return jobs_skills

    except Exception as e:
        print("An Error Occured\n Could not get top 5 matched jobs", e)
