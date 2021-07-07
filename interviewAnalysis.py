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
    """

    Parameters
    ----------
    df:pd.DataFrame : The data that has the required colum to plot

    col_name:str : the column to aggregate with


    Returns
    -------
    A bar chart

    """
    df.loc[df[col_name] == "Quite Sure", col_name] = "Very Sure"

    colsList = col_name.split("_")
    col = " ".join(colsList)

    data = df[col_name].value_counts().reset_index(name='Count')
    fig = px.bar(data, x='index', y='Count', height=500, width=400, title=f'{col.title()}')
    st.plotly_chart(fig)

def first_plot_bar(df: pd.DataFrame, col_name: str):
    df.loc[df[col_name] == "Quite Sure", col_name] = "Very Sure"
    values = df[col_name].unique()
    uniqueCount = []
    for value in values:
        df2 = df.loc[df[col_name] == value]
        count = df2["interviewee_email"].nunique()
        uniqueCount.append([value, count])

    colsList = col_name.split("_")
    col = " ".join(colsList)

    dfPlot = pd.DataFrame(uniqueCount, columns=["answer", "count"])
    fig = px.bar(dfPlot, x='answer', y='count', height=500, width=400, title=f'{col.title()}')
    st.plotly_chart(fig)

def piePlot(df: pd.DataFrame, col: str):
    dfLead = displayInterviewee.loadTrainee()
    dfSuit = df.loc[df["suitable"] == "yes"]

    df = pd.merge(dfSuit, dfLead, left_on="interviewee_email", right_on="email", how="left")
    df = df.drop_duplicates("email")

    data = df[col].value_counts().reset_index(name='Count')
    fig = px.pie(data, names='index', values='Count', height=500, width=400, title=f'{col.title()}')
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
    suitable, job_readineess, grad = st.beta_columns([1, 1, 1])
    first_interview_pass, social, _ = st.beta_columns([1, 1, 1])
    gender, nationality = st.beta_columns([1, 1])
    with suitable:
        first_plot_bar(df, 'suitable')
    with job_readineess:
        first_plot_bar(df, 'predict_job_readiness')
    with grad:
        first_plot_bar(df, 'predict_distinction_graduation')
    with first_interview_pass:
        first_plot_bar(df, 'predict_first_job_interview_pass')
    with social:
        first_plot_bar(df, 'predict_outstanding_social_contribution')
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
        suitable1, job_readineess1, grad1 = st.beta_columns([1, 1, 1])
        first_interview_pass1, social1, _ = st.beta_columns([1, 1, 1])
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


def main():
    st.title('Interview Result Analysis')
    st.subheader('Overall Analysis')

    df = loadInterview()

    first_layer(df)
    insight_per_interviewee(df)
