import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

# prefect workflow
from prefect import task, Flow
from prefect.schedules import CronSchedule
from prefect.utilities.notifications import slack_notifier
from prefect.engine.state import Success

# Email Utils
from app_utils import (
    transform_trainees_data,
    transform_linkedln_jobs,
    get_trainees_jobs_based_on_category,
    get_skills_per_jobs,
    get_top_5_matched_jobs
)


handler = slack_notifier(only_states=[Success])


def job_alert_email(RECIPIENT: str, name: str, message: list):
    SENDER = "10 Academy Training Team <train@10academy.org>"

    AWS_REGION = "eu-west-1"

    SUBJECT = "10 Academy Batch 4 - Job Match Alert"

    BODY_HTML = f"""
        <html>
            <body>
                <p>Dear {name}</p>

                <p>You've been matched with some Open jobs</p>
                {message}

            </body>
        </html>
        """

    CHARSET = "UTF-8"

    client = boto3.client("ses", region_name=AWS_REGION)

    msg = MIMEMultipart("mixed")
    # Add subject, from and to lines.
    msg["Subject"] = SUBJECT
    msg["From"] = SENDER
    msg["To"] = RECIPIENT

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart("alternative")

    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    # textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), "html", CHARSET)

    # Add the text and HTML parts to the child container.
    # msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)

    try:
        # Provide the contents of the email.
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=[RECIPIENT],
            RawMessage={
                "Data": msg.as_string(),
            },
        )
        print(f"Sent to {name}")
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])


# def read_data(filename: str):
#     jobs_path = f"s3://jobmodel/{filename}"
#     linkedInJobs = pd.read_csv(jobs_path)
#     return linkedInJobs


def read_data(filename: str, foldername: str):
    jobs_path = f"s3://jobmodel/{foldername}/{filename}"
    linkedInJobs = pd.read_csv(jobs_path)
    return linkedInJobs


def list_files(bucket: str):
    """
    Function to list files in a given S3 bucket
    """
    s3 = boto3.client("s3")
    contents = []
    for item in s3.list_objects(Bucket=bucket)["Contents"]:
        contents.append(item)
    # print(contents)
    return contents


@task(nout=4)
def transform_data():
    trainees = transform_trainees_data()

    jobs = transform_linkedln_jobs()
    # jobs = pd.read_csv("jobs.csv")

    (
        mle_jobs,
        mle_jobs_trainees,
        de_jobs,
        de_jobs_trainees,
    ) = get_trainees_jobs_based_on_category(jobs, trainees)

    return mle_jobs, mle_jobs_trainees, de_jobs, de_jobs_trainees


@task(nout=2)
def get_skills(mle_jobs, mle_jobs_trainees, de_jobs, de_jobs_trainees):
    # get skills for mle
    mle_skills = get_skills_per_jobs(mle_jobs_trainees, mle_jobs)
    de_skills = get_skills_per_jobs(de_jobs_trainees, de_jobs)

    # get top 5
    mle_top5 = get_top_5_matched_jobs(mle_skills)
    de_top5 = get_top_5_matched_jobs(de_skills)

    return mle_top5, de_top5


@task
def get_message(df):
    # get email content
    mle_message = {}
    names = df["name"].unique().tolist()
    new_msg = []
    for name in names:
        trainees_df = df[df["Name"] == name]
        trainees_df = trainees_df.drop_duplicates()
        trainees_df.reset_index(drop=True, inplace=True)
        for i in range(len(trainees_df)):
            if name in mle_message:
                mle_message[name].append(
                    f"<p><b>{trainees_df['company'][i]}</b> is looking for a <b>{trainees_df['title'][i]}</b></p>. <p>Apply here::<br>{trainees_df['post_link'][i]}</p>"
                )
            else:
                mle_message[name] = [
                    f"<p><b>{trainees_df['company'][i]}</b> is looking for a <b>{trainees_df['title'][i]}</b></p>. <p>Apply here::<br>{trainees_df['post_link'][i]}</p>"
                ]

            if len(mle_message[name]) == 5:
                break
        for msg in mle_message[name]:
            if msg not in new_msg:
                new_msg.append(msg)

        mle_message[name] = new_msg

    return mle_message


@task(nout=2)
def get_trainees_df(de_skills, mle_skills, de_message, mle_message):
    de_df = pd.DataFrame(
        {"Name": de_skills["Name"].unique(), "Email": de_skills["Email"].unique()}
    ).sort_values("Name")
    mle_df = pd.DataFrame(
        {"Name": mle_skills["Name"].unique(), "Email": mle_skills["Email"].unique()}
    ).sort_values("Name")

    de_df_message = []
    for name in de_df["Name"]:
        de_df_message.append(de_message[name])

    mle_df_message = []
    for name in mle_df["Name"]:
        mle_df_message.append(mle_message[name])

    de_df["message"] = de_df_message
    mle_df["message"] = mle_df_message

    return de_df, mle_df


@task
def get_team_df():
    team_df = pd.DataFrame(
        {
            "Name": [
                "Abubakar",
                "Arun",
                "Yabebal",
                "Mahlet",
                "Mukuzi",
                "Binyam",
                "Bethelhem",
                "Micheal",
            ],
            "Email": [
                "alaroabubakarolayemi@gmail.com",
                "arun@10academy.org",
                "yabebal@gmail.com",
                "formahlet@gmail.com",
                "damukuzi@gmail.com",
                "binasisayet8790@gmail.com",
                "sisaybethelhem@gmail.com",
                "kaaymyke@gmail.com",
            ],
        }
    )
    return team_df


@task(name="Send Email Task")
def send_email(team_df, df):
    names = df["Name"].unique().tolist()
    for i, name in enumerate(names[: len(team_df)]):
        # job_alert_email(df[df['Name'] == name]['Email'].tolist()[0], name, "".join(map(str, df[df['Name'] == name]['message'].tolist())).replace('[' , '').replace(']' , '').replace(',' , ''))
        # job_alert_email(email, name, "".join(map(str, df[df['Name'] == name]['message'].tolist())).replace('[' , '').replace(']' , '').replace(',' , ''))
        job_alert_email(
            team_df["Email"][i],
            team_df["Name"][i],
            "".join(map(str, df[df["Name"] == name]["message"].tolist()))
            .replace("[", "")
            .replace("]", "")
            .replace(",", ""),
        )
        # break


cron_schedule = CronSchedule(cron="0 */4 * * *")
# 0 11 * * *


def prefect_flow():
    with Flow(name="EmailSender", schedule=cron_schedule) as email_sender_job:
        mle_jobs, mle_jobs_trainees, de_jobs, de_jobs_trainees = transform_data()
        mle_top5, de_top5 = get_skills(
            mle_jobs, mle_jobs_trainees, de_jobs, de_jobs_trainees
        )

        mle_messages = get_message(mle_top5)
        de_messages = get_message(de_top5)

        de_df, mle_df = get_trainees_df(de_top5, mle_top5, de_messages, mle_messages)
        team_df = get_team_df()
        send_email(team_df, de_df)
        send_email(team_df, mle_df)
    return email_sender_job


if __name__ == "__main__":
    # get_jobs()
    flow = prefect_flow()
    # flow.register(project_name = "JobModel")
    flow.run()
