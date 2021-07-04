from numpy.lib.npyio import load
from pandas.io.parsers import read_csv
import streamlit as st
import pandas as pd
import createDBandTables

def loadTrainee() -> pd.DataFrame:
    dbName = "tenxdb"
    query = "SELECT * FROM ApplicantInterview"
    df = createDBandTables.db_execute_fetch(query, rdf=True, dbName=dbName)
    return df

def loadInterviwer() -> pd.DataFrame:
    dbName = "tenxdb"
    query = "SELECT * FROM ApplicantInterviewer"
    df = createDBandTables.db_execute_fetch(query, rdf=True, dbName=dbName)
    return df

def displayTraineeInfo(df: pd.DataFrame) -> None:
    colsToDisplay = ["community_summary", "github_activity", "github_link_score", "writing_score",
                     "number_of_submissions", "gender", "nationality", "final_score", "applicant_rank", "thought_chain"]

    st.title(f"{df['fullname']}'s Week 0 Stats")

    stat1, stat2, stat3, stat4, stat5 = st.beta_columns([1, 1, 1, 1, 1])
    with stat1:
        displayStat(colsToDisplay[0], df[colsToDisplay[0]].values[0])
    with stat2:
        displayStat(colsToDisplay[1], df[colsToDisplay[1]].values[0])
    with stat3:
        displayStat(colsToDisplay[2], df[colsToDisplay[2]].values[0])
    with stat4:
        displayStat(colsToDisplay[3], df[colsToDisplay[3]].values[0])
    with stat5:
        displayStat(colsToDisplay[4], df[colsToDisplay[4]].values[0])

    stat6, stat7, stat8, stat9, stat10 = st.beta_columns([1, 1, 1, 1, 1])
    with stat6:
        displayStat(colsToDisplay[5], df[colsToDisplay[5]].values[0])
    with stat7:
        displayStat(colsToDisplay[6], df[colsToDisplay[6]].values[0])
    with stat8:
        displayStat(colsToDisplay[7], df[colsToDisplay[7]].values[0])
    with stat9:
        displayStat(colsToDisplay[8], df[colsToDisplay[8]].values[0])
    with stat10:
        displayStat(colsToDisplay[9], df[colsToDisplay[9]].values[0])

def displayStat(col: str, value):
    colsList = col.split("_")
    col = " ".join(colsList)
    st.markdown("<p style='border:solid #d3d3d3; box-shadow: .5px 1.5px #d3d3d3; border-radius:10px; padding:10px;'>"
                f"{col.title()}: {value}</p>", unsafe_allow_html=True)
