from s3_utils import list_files, upload_file
import pandas as pd

bucket_name = "jobmodel"
all_data = list_files(bucket_name)
print(all_data)


def get_linkedln_scraped_jobs():
    linkedln_jobs = [i['Key'] for i in all_data[2:25]]
    df = pd.DataFrame()
    for name in linkedln_jobs:
        try:
            d = pd.read_csv(f's3://jobmodel/{name}')
            df = df.append(d, ignore_index=True)
        except Exception as e:
            print("Error", e)
    print(df.columns.values)
    imp_columns = ['title', 'job_title_id', 'company', 'post_link',
                   'description', 'job_desc_id']
    df = df[imp_columns]
    df.to_csv("LinkedlnJobs.csv", index=False)

    return df


def get_trainees_emails():
    filename = all_data[0]['Key']
    try:
        trainees_emails = pd.read_csv(f's3://jobmodel/{filename}')
        print(trainees_emails.columns)
        trainees_emails.to_csv('TraineesEmail.csv', index=False)
        return trainees_emails
    except Exception as e:
        print("Error", e)


if __name__ == "__main__":
    # upload_file("AllLinkedlnJobs.csv", bucket_name,
    #         "linkedlnScrapedJobs/AllLinkedlnJobs.csv")
    # upload_file("data_file.json", bucket_name,
    #         "linkedlnScrapedJobs/data_file.json")
    get_linkedln_scraped_jobs()
    get_trainees_emails()
