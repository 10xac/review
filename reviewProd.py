import streamlit as st
import psycopg2
import createDBandTables

st. set_page_config(layout="wide")


def getReviewerAppli():
    _, cur = createDBandTables.DBConnect()
    cur.execute('SELECT * FROM applicant_information WHERE review_id =2')

    answers = cur.fetchall()

    return answers

def getQuestionIds():
    _, cur = createDBandTables.DBConnect()
    cur.execute("SELECT * FROM question WHERE application_form_id = 12")
    questions = cur.fetchall()

    questionIds = []
    for question in questions:
        questionIds.append(question[0])

    return questionIds

def getQuestions():
    _, cur = createDBandTables.DBConnect()
    ids = getQuestionIds()
    Questions = []

    for id in ids:
        cur.execute(f"SELECT * FROM question_translation where question_id = {id}")
        Question = cur.fetchall()
        Questions.extend(Question)

    return Questions

def displayQuestionAndAnswer():
    conn, cur = createDBandTables.DBConnect()
    questions = getQuestions()
    answers = getReviewerAppli()

    answersId = []
    questionsToExclude = [299, 300, 301, 308, 309, 311, 314, 318, 329]
    for answer in answers:
        answersId.append(answer[2])

    with st.form(key='review-form'):
        st.title(f"Applicant {answers[0][1]}'s review")

        for question in questions:
            if question[1] in questionsToExclude:
                continue

            st.write(f"## {question[4].capitalize()}")
            for answer in answers:
                if answer[2] == question[1]:
                    if question[1] == 332:
                        st.markdown(f"<p style='padding-left:20px; background-color:#F0F2F6;color:black;font-size:16px;border-radius:10px;'>{answer[3]}</p>", unsafe_allow_html=True)

                        chanQue = "Enter value below to Change this applicant's status"
                        st.markdown(f"<p style='font-size:22px;border-radius:10px;'>{chanQue}</p>", unsafe_allow_html=True)
                        acceptedValue = st.radio("",
                                                 ("Yes", "No", "Maybe"))
                        continue

                    st.markdown(f"<p style='padding:10px; background-color:#F0F2F6;color:black;font-size:16px;border-radius:10px;'>{answer[3]}</p>", unsafe_allow_html=True)

            if question[1] not in answersId:
                if question[1] == 332:
                    appQue = "Is this applicant accepted to week 0?"
                    st.markdown(f"<p style='padding:10px; background-color:#F0F2F6;color:#ed1f33;font-size:20px;border-radius:10px;'>{appQue}</p>", unsafe_allow_html=True)
                    acceptedValue = st.radio(""
                                             ("Yes", "No", "Maybe"))
                else:
                    noAns = "applicant did not answer this question"
                    st.markdown(f"<p style='padding:10px; background-color:#F0F2F6;color:#ed1f33;font-size:16px;border-radius:10px;'>{noAns}</p>", unsafe_allow_html=True)

        colB1, colB2 = st.beta_columns([1, .1])

        with colB1:
            pass
        with colB2:
            submitButton = st.form_submit_button(label="Submit")

        if submitButton:
            st.write(f"Applicant {answers[0][1]} has been reviewed")
            if 332 in answersId:
                query = """UPDATE answer
                        SET value = (%s)
                        WHERE response_id = (%s)
                        AND question_id = (%s)"""

                cur.execute(query, (acceptedValue, answers[0][1], 332))
            else:
                query = """INSERT INTO answer(response_id, question_id, value)
                        VALUES (%s, %s, %s)"""

                cur.execute(query, (answers[0][1], 332, acceptedValue))

            conn.commit()
            cur.close()

    col = st.beta_columns(16)
    with col[-2]:
        st.button('Back')
    with col[-1]:
        st.button('Next')

displayQuestionAndAnswer()
