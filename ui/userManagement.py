import os, sys

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
import streamlit as st
from db.databaseManagement import create_usertable, view_all_tables, view_all_users, delete_user,add_userdata
from utils.hashManagement import make_hashes
import pandas as pd
import numpy as np


def addUser():
    email = st.text_input("Email")
    password = st.text_input("Password", type = 'password')
    status = st.selectbox("Select Status", ["student", "staff", "superAdmin"])
    button  = st.button("addUser")
    if button:
        create_usertable()
        add_userdata(email, make_hashes(password), status)

def checkUser():
    button  = st.button("checkUser")
    if button:
        create_usertable()
        print(view_all_tables())
        print(view_all_users())

def main():
    st.title("User management")
    menu = ["Display tables","Display users","Create users","Delete users"]
    selector = st.selectbox("Menu", menu)

    if selector == "Display users":
        st.write("Users")
        st.subheader("User Profiles")
        user_result = view_all_users()
        clean_ = pd.DataFrame(user_result,columns=["Username","Password","status"], index=None, )
        clean_.index = np.arange(1, len(clean_) + 1)
        st.dataframe(clean_)
    elif selector == "Display tables":
        st.write("Tables")
        st.subheader("Tables")
        table_result = view_all_tables()
        clean_ = pd.DataFrame(table_result,columns=["Table"])
        clean_.index = np.arange(1, len(clean_) + 1)
        st.dataframe(clean_)
    elif selector == "Create users":
        st.write("Create")
        st.subheader("Create")
        email = st.text_input("Email")
        password = st.text_input("Password", type = 'password')
        status = st.selectbox("Select Status", ["student", "staff", "superAdmin"])
        button  = st.button("addUser")
        if button:
            create_usertable()
            try:
                add_userdata(email, make_hashes(password), status)
                st.success("User added")
            except:
                st.warning("Error removing")
                print("Error")
    elif selector == "Delete users":
        st.write("Delete")
        st.subheader("Delete")
        email = st.text_input("Email")
        button  = st.button("Delete user")
        if button:
            create_usertable()
            try:
                delete_user(email)
                st.success("User deleted")
            except:
                st.warning("Error removing")
                print("User not found")

def injectData():
    create_usertable()
    add_userdata("admin",make_hashes("admin"),"superAdmin")
# injectData()