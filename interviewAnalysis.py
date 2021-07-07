import pandas as pd
import plotly.express as px
import streamlit as st
import displayInterviewee
import createDBandTables

def loadInterview() -> pd.DataFrame:
    """

    Parameters
    ----------
    filepath:str : path where data is located on the local machine


    Returns
    -------
    A dataframe

    """
    dbName = "tenxdb"
    query = "SELECT * FROM ApplicantInterviewResult"
    df = createDBandTables.db_execute_fetch(query, rdf=True, dbName=dbName)
    return df

def plot_bar(df: pd.DataFrame, col_name: str):
    colsList = col_name.split("_")
    col = " ".join(colsList)

    df.loc[df[col_name] == "Quite Sure", col_name] = "Very Sure"
    df.loc[df[col_name] == "", col_name] = "unanswered"

    data = pd.crosstab(df[col_name], df['interviewer_email'])

    fig = px.bar(data, x=data.index, y=list(data.columns), height=550, width=580, title=f'{col.title()}')
    st.plotly_chart(fig)

def first_plot_bar(df: pd.DataFrame, col_name: str):
    df.loc[df[col_name] == "Quite Sure", col_name] = "Very Sure"
    df.loc[df[col_name] == "", col_name] = "unanswered"
    values = df[col_name].unique()
    uniqueCount = []
    for value in values:
        df2 = df.loc[df[col_name] == value]
        count = df2["interviewee_email"].nunique()
        uniqueCount.append([value, count])

    colsList = col_name.split("_")
    col = " ".join(colsList)

    dfPlot = pd.DataFrame(uniqueCount, columns=["answer", "count"])
    fig = px.bar(dfPlot, x='answer', y='count', height=550, width=580, title=f'Total {col.title()}')
    st.plotly_chart(fig)

def piePlot(df: pd.DataFrame, col: str):
    dfLead = displayInterviewee.loadTrainee()
    dfSuit = df.loc[df["suitable"] == "yes"]

    df = pd.merge(dfSuit, dfLead, left_on="interviewee_email", right_on="email", how="left")
    df = df.drop_duplicates("email")

    data = df[col].value_counts().reset_index(name='Count')
    fig = px.pie(data, names='index', values='Count', height=550, width=580, title=f'{col.title()}')
    st.plotly_chart(fig)

def first_layer(df: pd.DataFrame):
    """

    Parameters
    ----------
    df:pd.DataFrame :


    Returns
    -------
    A 5 column bar chart

    """
    st.text(f"Total Trainee Interviewed:    {df['interviewee_email'].nunique()}")
    suitable, suitable2 = st.beta_columns([1, 1])
    job_readineess, grad = st.beta_columns([1, 1])
    first_interview_pass, social = st.beta_columns([1, 1])
    gender, nationality = st.beta_columns([1, 1])
    with suitable:
        first_plot_bar(df, 'suitable')
    with suitable2:
        plot_bar(df, 'suitable')
    with job_readineess:
        plot_bar(df, 'predict_job_readiness')
    with grad:
        plot_bar(df, 'predict_distinction_graduation')
    with first_interview_pass:
        plot_bar(df, 'predict_first_job_interview_pass')
    with social:
        plot_bar(df, 'predict_outstanding_social_contribution')
    with gender:
        piePlot(df, 'gender')
    with nationality:
        piePlot(df, 'nationality')

def insight_per_interviewee(df: pd.DataFrame):
    """

    Parameters
    ----------
    df:pd.DataFrame :


    Returns
    -------
    A 5 column bar chart

    """
    interviewee_email = st.selectbox("Select Email of the interviewee ", list(df['interviewee_email'].unique()))
    data = df.query(f"interviewee_email == '{interviewee_email}' ")

    with st.beta_expander(f"show {interviewee_email} interview data"):
        suitable1, job_readineess1 = st.beta_columns([1, 1])
        first_interview_pass1, grad1 = st.beta_columns([1, 1])
        social1, _ = st.beta_columns([1, 1])
        with suitable1:
            plot_bar(data, 'suitable')
        with job_readineess1:
            plot_bar(data, 'predict_job_readiness')
        with grad1:
            plot_bar(data, 'predict_distinction_graduation')
        with first_interview_pass1:
            plot_bar(data, 'predict_first_job_interview_pass')
        with social1:
            plot_bar(data, 'predict_outstanding_social_contribution')

        st.write("## Interviewer Comments")
        for comment in data["comments"]:
            if isinstance(comment, str):
                st.markdown(f"<p style='color:black;background:#F0F2F6;border-radius:5px;padding:5px;'>{comment}</p>",
                            unsafe_allow_html=True)


def main():
    st.title('Interview Result Analysis')
    st.subheader('Overall Analysis')

    df = loadInterview()

    first_layer(df)
    insight_per_interviewee(df)
