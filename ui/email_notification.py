import yagmail
import pandas as pd

jobs_path = "s3://jobmodel/linkedlnScrapedJobs/LinkedlnJobs.csv"
trainees_info_path = "s3://jobmodel/TraineesProfile/TraineesEmail.csv"

LinkedInJobs = pd.read_csv(jobs_path)
TraineesEmail = pd.read_csv(trainees_info_path)

class email_notification:
  def send_email(self,all_receivers,  Job_title, company, link):
    """
    Sends an email to the top matched trainees.

    Inputs: 
    all_receivers - a Python list of recipients' email addresses
    Job_title - Name of the Job position in string format
    company - Name of the company in string format
    link - a link that can be used to apply for the job.
    
    Returns:
    """
    To=all_receivers[0]
    all_receivers_cc=all_receivers[1:]

    sender_email = 'sisaybethel3@gmail.com'
    sender_password = input(f'Please, enter the password for {sender_email}:\n')
    Contents = [
              "Hi,\n You've been matched with a job..",
              company+" is looking for "+Job_title+".\n\n",   
                link
              ]
  
    emails_sent=[]
    for receiver in all_receivers:
      try:
        MatchedTraineesEmail=TraineesEmail.loc[TraineesEmail["Email"]==receiver]
        email_id=int(MatchedTraineesEmail["Email_id"])
        email_uid=str(LinkedInJobs["job_title_id"][4])+"_"+str(email_id)+"_"+str(LinkedInJobs["job_desc_id"][4])
        emails_sent.append(email_uid)
        #Save the unique email_uid
      except Exception as e:
        print(f"{receiver} is not found in the receivers list")
    print(emails_sent)

    try: 
      yag = yagmail.SMTP(user=sender_email, password=sender_password)
      yag.send(to=To,cc=all_receivers_cc, subject="Job Match Alert", contents=Contents)
    except Exception as e:
      print(f'Email not sent.\nSomething went wrong!\n{e}')
    
if __name__ == "__main__":
    notifications=email_notification()
    Job_title=LinkedInJobs["title"][4]
    company=LinkedInJobs["company"][4]
    link=LinkedInJobs["post_link"][4]
    all_receivers = ['sisaybethelhem@gmail.com','sisaybethelhem5@gmail.com']
    notifications.send_email(all_receivers,  Job_title, company, link)
   