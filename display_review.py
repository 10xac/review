import math
import streamlit as st
import pandas as pd
import createDBandTables
import db_functions

def loadTrainee() -> pd.DataFrame:
    dbName = "tenxdb"
    # query = "SELECT * FROM ApplicantInterview"
    df = db_functions.fromTenx()
    # df = db_functions.db_execute_fetch(query, rdf=True, dbName=dbName)
    return df

def loadInterviwer() -> pd.DataFrame:
    dbName = "tenxdb"
    # query = "SELECT * FROM ApplicantInterviewer"
    query = "SELECT * FROM reviewer"
    df = db_functions.db_execute_fetch(query, rdf=True, dbName=dbName)
    return df

def displayTraineeInfo(df: pd.DataFrame) -> None:
    colsToDisplay = [ "email","gender", "github_profile", "self_funding", "linkedIn_profile",
                     "previously_applied_batch","stage_to_pevious_application", "work_experience_month", "occupation", "3rd_reviewer_accepted", "3rd_reviewer_accepted",
                     "batch"]

    st.title(f"{df['firstname'].values[0]}'s review information")

    stat1, stat2, stat3, stat4 = st.columns([1, 1, 1, 1])
    with stat1:
        displayStat(colsToDisplay[0], df[colsToDisplay[0]].values[0], df[colsToDisplay[0] + "_rank"].values[0],
                    df[colsToDisplay[0] + "_max"].values[0])
    with stat2:
        displayStat(colsToDisplay[1], df[colsToDisplay[1]].values[0], df[colsToDisplay[1] + "_rank"].values[0],
                    df[colsToDisplay[1] + "_max"].values[0])
    with stat3:
        displayStat(colsToDisplay[2], df[colsToDisplay[2]].values[0], df[colsToDisplay[2] + "_rank"].values[0],
                    df[colsToDisplay[2] + "_max"].values[0])
    with stat4:
        displayStat(colsToDisplay[3], df[colsToDisplay[3]].values[0], df[colsToDisplay[3] + "_rank"].values[0],
                    df[colsToDisplay[3] + "_max"].values[0])

    stat5, stat6, stat7, stat8 = st.columns([1, 1, 1, 1])
    with stat5:
        displayStat(colsToDisplay[4], df[colsToDisplay[4]].values[0], df[colsToDisplay[4] + "_rank"].values[0],
                    df[colsToDisplay[4] + "_max"].values[0])
    with stat6:
        displayStat(colsToDisplay[5], df[colsToDisplay[5]].values[0], df[colsToDisplay[5] + "_rank"].values[0],
                    df[colsToDisplay[5] + "_max"].values[0])
    with stat7:
        displayStat(colsToDisplay[6], df[colsToDisplay[6]].values[0], df[colsToDisplay[6] + "_rank"].values[0],
                    df[colsToDisplay[6] + "_max"].values[0])
    with stat8:
        displayStat(colsToDisplay[7], df[colsToDisplay[7]].values[0], df[colsToDisplay[7] + "_rank"].values[0],
                    df[colsToDisplay[7] + "_max"].values[0])

    stat9, stat10, stat11, _ = st.columns([1, 1, 1, 1])
    with stat9:
        displayStat(colsToDisplay[8], df[colsToDisplay[8]].values[0], df[colsToDisplay[8] + "_rank"].values[0],
                    df[colsToDisplay[8] + "_max"].values[0])
    with stat10:
        displayStat(colsToDisplay[9], df[colsToDisplay[9]].values[0], df[colsToDisplay[9] + "_rank"].values[0],
                    df[colsToDisplay[9] + "_max"].values[0])
    with stat11:
        displayStat(colsToDisplay[10], df[colsToDisplay[10]].values[0], df[colsToDisplay[10] + "_rank"].values[0],
                    df[colsToDisplay[10] + "_max"].values[0])

def displayStat(col: str, value: float, rank: float, max: float):
    colsList = col.split("_")
    col = " ".join(colsList)
    if not math.isnan(rank):
        st.markdown("<p style='border:solid #d3d3d3;box-shadow: .5px 1.5px #d3d3d3; border-radius:10px; padding:10px;'>"
                    f"{col.title()}: {value:.2f} <br></br> Rank: {int(rank)}/{int(max)}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='border:solid #d3d3d3;box-shadow: .5px 1.5px #d3d3d3; border-radius:10px; padding:10px;'>"
                    f"{col.title()}: {value}</p>", unsafe_allow_html=True)
