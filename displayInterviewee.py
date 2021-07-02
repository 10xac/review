from numpy.lib.npyio import load
from pandas.io.parsers import read_csv
import streamlit as st
import pandas as pd
import createDBandTables

def loadData() -> pd.DataFrame:
    dbName = "tenx"
    query = "SELECT * FROM ApplicantInterview"
    df = createDBandTables.db_execute_fetch(query, rdf=True, dbName=dbName)
    return df

def displayTraineeInfo(df: pd.DataFrame) -> None:
    colsToDisplay = ["community_summary", "github_activity", "github_link_score", "writing_score", "cv_score",
                     "number_of_submissions", "thought_chain", "gender", "nationality"]

    st.title("Week 0 Stats")

    stat1, stat2, stat3, stat4 = st.beta_columns([1, 1, 1, 1])
    with stat1:
        displayStat(colsToDisplay[0], df[colsToDisplay[0]].values[0])
    with stat2:
        displayStat(colsToDisplay[1], df[colsToDisplay[1]].values[0])
    with stat3:
        displayStat(colsToDisplay[2], df[colsToDisplay[2]].values[0])
    with stat4:
        displayStat(colsToDisplay[3], df[colsToDisplay[3]].values[0])

    stat5, stat6, stat7, stat8 = st.beta_columns([1, 1, 1, 1])
    with stat5:
        displayStat(colsToDisplay[5], df[colsToDisplay[5]].values[0])
    with stat6:
        displayStat(colsToDisplay[6], df[colsToDisplay[6]].values[0])
    with stat7:
        displayStat(colsToDisplay[7], df[colsToDisplay[7]].values[0])
    with stat8:
        displayStat(colsToDisplay[8], df[colsToDisplay[8]].values[0])

def displayStat(col: str, value):
    st.markdown("<p style='border:solid #d3d3d3; box-shadow: .5px 1.5px #d3d3d3; border-radius:10px; padding:10px;'>"
                f"{col}: {value}</p>", unsafe_allow_html=True)
