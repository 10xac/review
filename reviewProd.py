from botocore.exceptions import ClientError
import streamlit as st
import pandas as pd
import createDBandTables
import sessionState

st. set_page_config(layout="wide")


def getReviewerAppli():
    query = "SELECT * from applicant_information"
    df = createDBandTables.db_execute_fetch(query, rdf=True, dbName='review')

    return df

def displayQuestionAndAnswer():
    applicant_info = getReviewerAppli()
    conn, cur = createDBandTables.DBConnect('review')
    shortQue = {}
    N = 1
    session_state = sessionState.get(page_number=0)

    last_page = len(applicant_info) // N
    # st.write(str(session_state.page_number))

    prevCol, _, nextCol = st.beta_columns([1, 10, 1])

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

    with st.form(key='review-form'):
        st.title("2021 Applicant review")
        for question in row.columns:
            st.write(f"## {question.capitalize()}")
            answer = str(row[question].values[0])

            if answer == 'None' or answer == '':
                if question == 'accepted':
                    appQue = "Is this applicant accepted to week 0?"
                    st.markdown(f"<p style='padding:10px;color:#ed1f33;font-size:20px;border-radius:10px;'>{appQue}</p>", unsafe_allow_html=True)
                    acceptedValue = st.radio("", ("Yes", "No", "Maybe"))
                    continue

                noAns = "Applicant did not answer this question"
                st.markdown(f"<p style='padding:10px; background-color:#F0F2F6;color:#ed1f33;font-size:16px;border-radius:10px;'>{noAns}</p>", unsafe_allow_html=True)

            else:
                if question == 'accepted':
                    st.markdown(f"<p style='padding:10px; background-color:#F0F2F6;color:black;font-size:18px;border-radius:10px;'>{answer}</p>", unsafe_allow_html=True)
                    chanQue = "Change this applicant's status to"
                    st.markdown(f"<p style='font-size:22px;border-radius:10px;'>{chanQue}</p>", unsafe_allow_html=True)
                    acceptedValue = st.radio("", ("Yes", "No", "Maybe"))
                    continue

                st.markdown(f"<p style='padding:10px; background-color:#F0F2F6;color:black;font-size:18px;border-radius:10px;'>{answer}</p>", unsafe_allow_html=True)

        colB1, colB2 = st.beta_columns([1, .1])

        with colB1:
            pass
        with colB2:
            submitButton = st.form_submit_button(label="Submit")

        if submitButton:
            st.write("This Applicant has been reviewed")
            query = """UPDATE applicant_information
                    SET accepted = (%s)
                    WHERE applicant_id = (%s)"""

            cur.execute(query, (acceptedValue, int(applicant_index)))

            conn.commit()
            cur.close()


def verifyEmail():
    email = st.text_input("Enter Your 10academy Email below")

    try:
        query = "SELECT * fROM reviewer WHERE reviewer_email={email}"
        createDBandTables.db_execute_fetch(query, rdf=False, dbname='review')
        return True, email

    except ClientError as e:
        st.write("You're not a reviewer, Enter a valid email")
        raise e

verifyEmail()
