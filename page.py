import os
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
#
import streamlit as st
import streamlit_tags

#
import utils.extra as exa
import utils.s3_utils as s3data

#
import landingPage as lp
import b5_test_review as b5

#
# configure landing page
#st.set_page_config(page_title="Job Model", page_icon='👩‍💻')

st.markdown(
    f"""
<style>
    .reportview-container .main .block-container{{
        max-width: 80%;
        padding-top: 0rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
    }}
    .stButton>button{{
    height: 3em;
    width: 8em;
    border-radius: 12px;
    transition-duration: 0.4s;
    }}
    #tags {{    
                    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: .15rem .40rem;
    position: relative;
    text-decoration: none;
    font-size: 95%;
    border-radius: 5px;
    margin-right: .5rem;
    margin-top: .4rem;
    margin-bottom: .5rem;
    color: rgb(88, 88, 88);
    border-width: 0px;
    background-color: rgb(240, 242, 246);
    }}
    #tags:hover {{
        color: black;
        box-shadow: 0px 5px 10px 0px rgba(0,0,0,0.2);
    }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""",
    unsafe_allow_html=True,
)

st.session_state.mylist = []

if 'button_pressed' not in st.session_state:
    st.session_state['button_pressed'] = ''



def get_selected_name(name_list):
    name_list.sort()
    names_list_default = ['All']
    names_list_default.extend(name_list)
    st.subheader("Select your name:")
    selected_name = st.selectbox(
        label='Select your name from the drop-down', options=names_list_default)
    return selected_name


def render_table(df):
    fig = go.Figure(data=[go.Table(
        # columnwidth = [90, 80, 400, 200],
        # columnorder = [1,2,3,4],
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.name, df.match_degree,
                           df.required_skills, df.matched_skills],
                   fill_color='lavender',
                   align='left', height=40))
    ])
    # fig.update_layout(width=1000)
    return fig



@st.cache(suppress_st_warning=True)
def get_stat_data():
    Bucket = 'jobmodel'
    allscrapeddata_csv = 'linkedlnScrapedJobs/AllLinkedlnJobs.csv'
    metadata_json = 'linkedlnScrapedJobs/data_file.json'

    if exa.is_aws_instance():
        print("In Aws Instance: fetch data from s3")
        # try:
        #     data = s3data.get_s3_csv_dataframe(Bucket, allscrapeddata_csv)
        #     json_data = s3data.get_s3_json_dataframe(Bucket, metadata_json)
        # except:
        #     data = pd.read_csv(f'data/{allscrapeddata_csv}')
        #     json_data = pd.read_json(f'data/{metadata_json}')  
    else:
        print("In local machine: fetch data from data/ folder")        
        # try:
        #     data = pd.read_csv(f'data/{allscrapeddata_csv}')
        #     json_data = pd.read_json(f'data/{metadata_json}')              
        # except:            
        #     data = s3data.get_s3_csv_dataframe(Bucket, allscrapeddata_csv)
        #     json_data = s3data.get_s3_json_dataframe(Bucket, metadata_json)



def form_callback():
    st.write(st.session_state.button_pressed)


def makebutton(colname, buttonname):
    st.session_state.button_pressed = buttonname
    if colname.button(buttonname, key=buttonname, on_click=form_callback):
        st.session_state.mylist.append(buttonname)


def makebutton1(colname, buttonname):
    st.session_state.button_pressed = buttonname
    if colname.button(buttonname, key=buttonname, on_click=form_callback):
        st.session_state.mylist.append(buttonname)


def main(email):
    st.sidebar.title("10 Academy")
    app_mode = st.sidebar.selectbox("Select Review Stage Page", ["Application review", "Interview"])
    
    if app_mode == "Application review":
        b5.verifyEmail('tenxdb')
    elif app_mode == "Interview":
        b5.interviewForm.start()
    # elif app_mode == "Interview Analysis":
    #     b5.interviewAnalysis.main()
        

if __name__ == "__main__":

    if "hasLoggedIn" in st.session_state:
        if st.session_state["hasLoggedIn"]:
            print('hasLoggedIn key got set. Checking access condition ..')
            if "access" in st.session_state and st.session_state["access"] == "staff":
                print('Calling main strealit app .. ')
                main(st.session_state['email'])
            else:
                st.warning("You are not logged in as a staff member")
        else:
            print('calling lp.main()')
            lp.session_start()
    else:
        print('calling lp.main()')
        lp.session_start()
