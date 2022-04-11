from botocore.exceptions import ClientError
import streamlit as st
import db_functions
import sessionState
import interviewForm
import interviewAnalysis

st. set_page_config(layout="wide", page_title="Review and Interview")
# @st.cache(suppress_st_warning=True)
def getReviewerAppli(reviewerId, reviewerGroup, dbName):

    query = "SELECT * from applicant_information WHERE batch = \"batch-5\" "
    df = db_functions.db_execute_fetch(query, rdf=True, dbName=dbName)
    print("______________________data for ",len(df))
    df.drop(['time_stamp','firstname','email','city','nationality','date_of_birth','gender','2nd_reviewer_id', '2nd_reviewer_accepted', '3rd_reviewer_id', '3rd_reviewer_accepted'], inplace=True,
            axis=1)
    print ("reviewwer_id",reviewerId )
    if reviewerGroup == 2:
        query = f"SELECT * from applicant_information where 2nd_reviewer_id = {reviewerId} AND batch = \"batch-5\""
        df = db_functions.db_execute_fetch(query, rdf=True, dbName=dbName)
        print(df)
        df.drop(['time_stamp','firstname','email','city','nationality','date_of_birth','gender','batch','3rd_reviewer_id', 'accepted', '3rd_reviewer_accepted'], inplace=True, axis=1)
        print(len(df))
    elif reviewerGroup == 3:
        query = f"SELECT * from applicant_information where 3rd_reviewer_id = {reviewerId}"
        df = db_functions.db_execute_fetch(query, rdf=True, dbName=dbName)
        df.drop(['time_stamp','firstname','email','city','nationality','date_of_birth','gender','batch','2nd_reviewer_id', 'accepted', '2nd_reviewer_accepted'], inplace=True, axis=1)
        print(len(df))
    return df

def getNotDoneReviews(reviewerId, reviewerGroup, dbName):

    # query = "SELECT * from applicant_information"
    
    # Comment above and uncomment below during actual review time
    query = "SELECT * from applicant_information where accepted IS NULL"
    if reviewerGroup == 2:
        query = "SELECT * from applicant_information where 2nd_reviewer_accepted IS NULL and 2nd_reviewer_id =" \
                f" {reviewerId}"
    elif reviewerGroup == 3:
        query = "SELECT * from applicant_information where 3rd_reviewer_accepted IS NULL and 3rd_reviewer_id =" \
                f"{reviewerId}"

    df = db_functions.db_execute_fetch(query, rdf=True, dbName=dbName)

    return len(df)

def displayQuestionAndAnswer(reviewerId, reviewerGroup, email, dbName):

    conn = db_functions.db_connect(dbName)
    cur = conn.cursor()
    applicant_info = getReviewerAppli(reviewerId, reviewerGroup, dbName)
    #
    notDone = getNotDoneReviews(reviewerId, reviewerGroup, dbName)
    remaining = len(applicant_info) - notDone
    percentage = remaining / len(applicant_info) * 100
    N = 1

    if remaining >= 1:
        session_state = sessionState.get(email=email, page_number=remaining)
    else:
        session_state = sessionState.get(email=email, page_number=0)

    last_page = len(applicant_info) // N
    
    # st.write(str(session_state.page_number))

    prevCol, _, nextCol = st.columns([1, 10, 1])
    
    if nextCol.button('Next'):
        if session_state.page_number + 1 > last_page:
            session_state.page_number = last_page
        else:
            session_state.page_number += 1

    if prevCol.button("Previous"):
        if session_state.page_number - 1 < 0:
            session_state.page_number = 0
        else:
            session_state.page_number -= 1

    # Get start and end indices of the next page of the dataframe
    start_idx = session_state.page_number * N
    end_idx = (1 + session_state.page_number) * N
    
    row = applicant_info.iloc[start_idx:end_idx]
    
    applicant_index = row["applicant_id"].values[0]
    print("_____________",applicant_index)
   
    with st.form(key='review-form'):
        st.write(f"You have reviewed {remaining} / {len(applicant_info)} so far; {percentage:.2f}% done ")
         
        for question in row.columns:
            if question == "3rd_reviewer_id" or question == "2nd_reviewer_id":
                continue

            if question == "2nd_reviewer_accepted" or question == "3rd_reviewer_accepted":
                st.write("## Accepted")
            else:
                st.write(f"## {question.capitalize()}")

            answer = str(row[question].values[0])
            
           

            if answer == 'None' or answer == '':
                if question == 'accepted' or question == "2nd_reviewer_accepted" or question == "3rd_reviewer_accepted":
                    appQue = "Is this applicant accepted to week 0?"
                    st.markdown(f"<p style='padding:10px;color:#ed1f33;font-size:20px;border-radius:10px;'>{appQue}"
                                "</p>", unsafe_allow_html=True)
                    acceptedValue = st.radio("", ("Yes", "No", "Maybe"))
                    continue

                noAns = "Applicant did not answer this question"
                st.markdown("<p style='padding:10px; background-color:#F0F2F6;color:#ed1f33;font-size:16px;"
                            f"border-radius:10px;'>{noAns}</p>", unsafe_allow_html=True)

            else:
                if question == 'accepted' or question == "2nd_reviewer_accepted" or question == "3rd_reviewer_accepted":
                    st.markdown("<p style='padding:10px; background-color:#F0F2F6;color:black;font-size:18px;"
                                f"border-radius:10px;'>{answer}</p>", unsafe_allow_html=True)
                    chanQue = "Change this applicant's status to"
                    st.markdown(f"<p style='font-size:22px;border-radius:10px;'>{chanQue}</p>", unsafe_allow_html=True)
                    acceptedValue = st.radio("", ("Yes", "No", "Maybe"))
                    
                    continue

                answer = '\r\n'.join([x for x in answer.splitlines() if x.strip()])
               
                st.markdown("<p style='padding:10px; background-color:#F0F2F6;color:black;font-size:18px;"
                            f"border-radius:10px;'>{answer}</p>", unsafe_allow_html=True)

        colB1, colB2 = st.columns([1, .1])

        with colB1:
            pass
        with colB2:
            submitButton = st.form_submit_button(label="Submit")

        if submitButton:
            st.write("This Applicant has been reviewed")
            # print (acceptedValue)
            query = """UPDATE applicant_information
                    SET accepted = (%s)
                    WHERE applicant_id = (%s)"""
            if reviewerGroup == 2:
                query = """UPDATE applicant_information
                    SET 2nd_reviewer_accepted = (%s)
                    WHERE applicant_id = (%s)"""
            elif reviewerGroup == 3:
                query = """UPDATE applicant_information
                    SET 3rd_reviewer_accepted = (%s)
                    WHERE applicant_id = (%s)"""

            cur.execute(query, (acceptedValue, int(applicant_index)))

            conn.commit()
            cur.close()


def verifyEmail(dbName):
    st.title("2022 Applicants Review")
    email = st.text_input("Enter Your 10academy Email below")

    if email:
        try:
            query = f"SELECT * fROM reviewer WHERE reviewer_email = '{email}'"
            res = db_functions.db_execute_fetch(query, rdf=False, dbName=dbName)
            
            if len(res) == 0:
                st.write("You're not a reviewer, Enter a valid email")

            try:
                with st.expander("Show Review Form"):
                    
                    displayQuestionAndAnswer(res[0][0], res[0][4], email, dbName)
            except IndexError as e:
                st.write("You have not been assigned any applicants to review")
                raise e

        except ClientError as e:
            st.write("You're not a reviewer, Enter a valid email")
            raise e

reviewType = st.sidebar.selectbox("Review Stage", ["Application review", "Interview"])

if reviewType == "Application review":
    verifyEmail('tenxdb')
elif reviewType == "Interview":
    interviewForm.start()
# elif reviewType == "Interview Analysis":
#     interviewAnalysis.main()
