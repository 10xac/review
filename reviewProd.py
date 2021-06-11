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
    # applicant_info = pd.read_csv('applicants_information.csv')
    # applicant_info.drop(["Email address", 'First Name', 'Last Name', 'Nationality', 'City of current residence',
    #                      'Gender', 'Name of Institution',
    #                      "Have you previously applied for 10 Academy intensive training", "Timestamp"], axis=1, inplace=True)

    shortQue = {}
    N = 1
    session_state = sessionState.get(page_number=0)

    last_page = len(applicant_info) // N

    prev, _, next = st.beta_columns([1, 10, 1])

    if next.button("Next"):

        if session_state.page_number + 1 > last_page:
            session_state.page_number = 0
        else:
            session_state.page_number += 1

    if prev.button("Previous"):

        if session_state.page_number - 1 < 0:
            session_state.page_number = last_page
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

            if answer == 'None' or answer=='':
                if question == 'accepted':
                    appQue = "Is this applicant accepted to week 0?"
                    st.markdown(f"<p style='padding:10px; background-color:#F0F2F6;color:#ed1f33;font-size:20px;border-radius:10px;'>{appQue}</p>", unsafe_allow_html=True)
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

    # with st.form(key='review-form'):
    #     st.title(f"Applicant {answers[0][1]}'s review")

    #     for question in questions:
    #         if question[1] in questionsToExclude:
    #             continue

    #         st.write(f"## {question[4].capitalize()}")
    #         for answer in answers:
    #             if answer[2] == question[1]:
    #                 if question[1] == 332:
    #                     st.markdown(f"<p style='padding-left:20px; background-color:#F0F2F6;color:black;font-size:16px;border-radius:10px;'>{answer[3]}</p>", unsafe_allow_html=True)

    #                     chanQue = "Enter value below to Change this applicant's status"
    #                     st.markdown(f"<p style='font-size:22px;border-radius:10px;'>{chanQue}</p>", unsafe_allow_html=True)
    #                     acceptedValue = st.radio("",
    #                                              ("Yes", "No", "Maybe"))
    #                     continue

    #                 st.markdown(f"<p style='padding:10px; background-color:#F0F2F6;color:black;font-size:16px;border-radius:10px;'>{answer[3]}</p>", unsafe_allow_html=True)

    #         if question[1] not in answersId:
    #             if question[1] == 332:
    #                 appQue = "Is this applicant accepted to week 0?"
    #                 st.markdown(f"<p style='padding:10px; background-color:#F0F2F6;color:#ed1f33;font-size:20px;border-radius:10px;'>{appQue}</p>", unsafe_allow_html=True)
    #                 acceptedValue = st.radio(""
    #                                          ("Yes", "No", "Maybe"))
    #             else:
    #                 noAns = "applicant did not answer this question"
    #                 st.markdown(f"<p style='padding:10px; background-color:#F0F2F6;color:#ed1f33;font-size:16px;border-radius:10px;'>{noAns}</p>", unsafe_allow_html=True)

    #     colB1, colB2 = st.beta_columns([1, .1])

    #     with colB1:
    #         pass
    #     with colB2:
    #         submitButton = st.form_submit_button(label="Submit")

    #     if submitButton:
    #         st.write(f"Applicant {answers[0][1]} has been reviewed")
    #         if 332 in answersId:
    #             query = """UPDATE answer
    #                     SET value = (%s)
    #                     WHERE response_id = (%s)
    #                     AND question_id = (%s)"""

    #             cur.execute(query, (acceptedValue, answers[0][1], 332))
    #         else:
    #             query = """INSERT INTO answer(response_id, question_id, value)
    #                     VALUES (%s, %s, %s)"""

    #             cur.execute(query, (answers[0][1], 332, acceptedValue))

    #         conn.commit()
    #         cur.close()

    # col = st.beta_columns(16)
    # with col[-2]:
    #     st.button('Back')
    # with col[-1]:
    #     st.button('Next')

displayQuestionAndAnswer()
