from typing_extensions import SupportsIndex
import streamlit as st
import sessionState
import createDBandTables
import displayInterviewee

def interviewForm(intervieweeEmail: str, interviewerEmail: str, dbName: str):
    conn, cur = createDBandTables.DBConnect(dbName)

    with st.form(key="interview-form"):
        st.title("Interview Form")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>2. Was the trainee on time for"
                    " this interview?</p>", unsafe_allow_html=True)
        onTime = st.radio("", ("Yes", "No"), key="on time")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>3. How good is this trainees'"
                    " communication?</p>", unsafe_allow_html=True)
        communincation = st.radio("", ("Exceeds Expectation", "Meets Expectation", "Does Not Meet Expectation",
                                  "Not Applicable"), key="communication")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>4. Interviewer asks: What did you think when"
                    " you saw the week 0 challenges?. </p>",
                    unsafe_allow_html=True)
        QA1 = st.radio("", ("Exceeds Expectation", "Meets Expectation", "Does Not Meet Expectation",
                       "Not Applicable"), key="QA1")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>5. Interviewer asks: What's something interesting "
                    "you shared with someone during 10 Academy week 0?</p>", unsafe_allow_html=True)
        QA2 = st.radio("", ("Exceeds Expectation", "Meets Expectation", "Does Not Meet Expectation",
                       "Not Applicable"), key="QA2")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>6. Interviewer asks: What's your biggest why for "
                    "becoming an  ML Engineer?</p>", unsafe_allow_html=True)
        QA3 = st.radio("", ("Exceeds Expectation", "Meets Expectation", "Does Not Meet Expectation",
                       "Not Applicable"), key="QA3")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>7. Interviewer asks: Is the Trainee ready to pay"
                    " forward?</p>", unsafe_allow_html=True)
        payForward = st.radio("", ("Yes", "No"), key="payForward")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>8. Interviewer asks: Is the Trainee ready to commit"
                    " to the program full time?</p>", unsafe_allow_html=True)
        fullTime = st.radio("", ("Yes", "No"), key="fullTime")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>9. Interviewer asks: Is the Trainee ready to self "
                    " fund?</p>", unsafe_allow_html=True)
        selfFund = st.radio("", ("Yes", "No"), key="selfFund")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>10. Interviewer asks: Does the Trainee have a "
                    "concrete understanding of ML Flow Design??</p>", unsafe_allow_html=True)
        mlFlow = st.radio("", ("Exceeds Expectation", "Meets Expectation", "Does Not Meet Expectation",
                          "Not Applicable"), key="mlFlow")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>11. Interviewer asks: Does the trainee have "
                    "concrete Code understanding?</p>", unsafe_allow_html=True)
        codeUnderstanding = st.radio("", ("Exceeds Expectation", "Meets Expectation", "Does Not Meet Expectation",
                                     "Not Applicable"), key="codeUnderstanding")

        st.write("## Interviewer Section (These questions are for you, the interviewer to answer)")
        st.markdown("<p style='font-size:22px; margin-bottom:-50px; border-radius:10px;'>i. Do you have any additional"
                    " comments with regards to this Trainee?</p>", unsafe_allow_html=True)
        comments = st.text_area("")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>ii. Is this Trainee suitable "
                    "for 10academy training program?</p>", unsafe_allow_html=True)
        suitable = st.radio("", ("yes", "no"), key="suitable")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>iii. What's your prediction? If accepted, will this"
                    "Trainee be job ready at the end of the training?</p>", unsafe_allow_html=True)
        predictJobReadiness = st.radio("", ("Absolutely", "Quite Sure", "Sure", "Not Sure"), key="predictJobReadiness")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>iv. What's your prediction? If accepted, will this "
                    " Trainee graduate with distinction?</p>", unsafe_allow_html=True)
        predictDistinctionGraduation = st.radio("", ("Absolutely", "Quite Sure", "Sure", "Not Sure"), key="distinction")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>v. What's your prediction? If accepted, will this "
                    "Trainee pass their first interview?</p>", unsafe_allow_html=True)
        predictFirstJobInterviewPass = st.radio("", ("Absolutely", "Quite Sure", "Sure", "Not Sure"), key="1Interview")

        st.markdown("<p style='font-size:22px; border-radius:10px;'>vi. What's your prediction? If accepted, will this "
                    "trainee have outstanding social contribution?</p>", unsafe_allow_html=True)
        predictOutStandingSocialContribution = st.radio("", ("Absolutely", "Quite Sure", "Sure", "Not Sure"),
                                                        key="social contribution")

        colB1, colB2 = st.beta_columns([1, .1])

        with colB1:
            pass
        with colB2:
            submitButton = st.form_submit_button(label="Submit")

        if submitButton:
            st.write("Submitted")
            query = f"""INSERT INTO ApplicantInterviewResult (interviewer_email,interviewee_email,on_time,communication_skill,q1,q2,q3,
                        payforward_confirmation,fulltime_confirmation,selffund_confirmation,mlflow_design_understanding,
                        code_understanding, comments, suitable, predict_job_readiness, predict_distinction_graduation,
                        predict_first_job_interview_pass, predict_outstanding_social_contribution)
                        VALUES('{interviewerEmail}', '{intervieweeEmail}',{onTime},'{communincation}','{QA1}','{QA2}',
                        '{QA3}',{payForward},{fullTime},{selfFund},'{mlFlow}','{codeUnderstanding}','{comments}',
                        {suitable},'{predictJobReadiness}', '{predictDistinctionGraduation}',
                        '{predictFirstJobInterviewPass}','{predictOutStandingSocialContribution}')"""

            cur.execute(query)

            conn.commit()
            cur.close()

def start():

    state = sessionState.get(key=0)
    st.markdown("<p style='font-size:22px; margin-bottom:-50px; border-radius:10px;'>Enter trainee's email"
                " below</p>", unsafe_allow_html=True)
    traineeMail = st.empty()
    traineeInfo = st.empty()

    st.markdown("<p style='font-size:22px; margin-bottom:-50px; border-radius:10px;'>Enter your 10academy email"
                " below</p>", unsafe_allow_html=True)
    interviewerMail = st.empty()
    interviewQuestions = st.empty()

    colB1, colB2 = st.beta_columns([1, .1])

    with colB1:
        pass
    with colB2:
        if st.button("Reset"):
            state.key += 1

    intervieweeEmail = traineeMail.text_input("", key=str(state.key))

    if intervieweeEmail:
        df = displayInterviewee.loadTrainee()
        df = df.loc[df["email"] == intervieweeEmail]
        if len(df) == 0:
            traineeInfo.markdown("<p style='color:#F63366;font-size:22px;'>This email is not registered with the 2021"
                                 " batch</p>", unsafe_allow_html=True)
        else:
            with traineeInfo.beta_expander("Show Trainee Info"):
                displayInterviewee.displayTraineeInfo(df)

    interviewerEmail = interviewerMail.text_input("", key="int" + str(state.key))

    if interviewerEmail:
        df = displayInterviewee.loadInterviwer()
        df = df.loc[df["email"] == interviewerEmail]
        if len(df) == 0:
            interviewQuestions.markdown("<p style='color:#F63366;font-size:22px;'>This is not a registered 10academy"
                                        " email</p>", unsafe_allow_html=True)
        else:
            with interviewQuestions.beta_expander("Show Trainee The Interview Form"):
                interviewForm(intervieweeEmail, interviewerEmail, "tenxdb")
