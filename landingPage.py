import streamlit as st
#from PIL import Image
import utils.hashManagement as hash
import db.databaseManagement as db
import ui.userManagement as userManagement
import page

form_count = 1
def redirect_to_content():
    if st.session_state["access"] == "student":
        
        # studentPage.main()
        st.sidebar.header("Student Page")
        st.sidebar.subheader("Under construction")
        st.session_state["hasLoggedIn"] = True 
        
    elif st.session_state["access"] == "staff":
        st.success("You are successfully logged in")
        st.session_state["hasLoggedIn"] = True
        st.write("Redirecting to review page with user: {st.session_state['email']}")
        #col1 = st.columns(1)
        #with col1:
        page.main(st.session_state['email'])
        
    else: #st.session_state["access"] == "superAdmin":
        st.success("You are successfully logged in")
        st.session_state["hasLoggedIn"] = True
        #col1 = st.columns(1)
        #with col1:                
        userManagement.main()
        
def signin():
    """A form validator which is used to get email and password

    Args:
        -

    Returns:
        -
    """

    form_count = 1
    form_key = "my_form"
    while form_key in st.session_state.keys():
        form_key=f'my_form_{form_count}'
        form_count += 1                      
        
    with st.form(key = form_key):
        st.header("Welcome to 10Academy Application Review Engine")
        st.write("")
        email_text_input = st.text_input(label = 'Email')
        password_text_input = st.text_input(label = 'Password', type = 'password')
        m = st.markdown("""
        <style>        
        div.stButton > button:first-child {
            background-color: rgb(255, 77, 77);
            color:#ffffff;
            font-size:15px;
            width:100%;
        }
        div.stButton > button:hover {
            background-color: #ffffff;
            color:rgb(255, 77, 77);
            font-size:15px;

            }
        </style>""", unsafe_allow_html=True)
        submit_button = st.form_submit_button(label = 'Submit')

        if submit_button:
            user = db.login_user(email_text_input,
                                 hash.check_hashes(password_text_input,
                                                   hash.make_hashes(password_text_input)))

            if user:
                st.session_state["email"] = email_text_input
                if user[0][2] == "staff":
                    st.session_state["login"] = "success"
                    st.session_state["access"] = "staff"
                elif user[0][2] == "superAdmin":
                    st.session_state["login"] = "success"
                    st.session_state["access"] = "superAdmin"
            else:
                st.error("Invalid Credentials")
                st.error("No User")

                

def pageselection(selector):
    """display sidebar according to selector value\n selector is to check user has pressed login or not

    Args:
        selector either "selected" or "notselected"

    Returns:
        -
    """
    col1, col2, col3 = st.columns(3)    

    if(st.session_state["selector"] == "notselected"):
        st.session_state['selector'] = "selected"
        with col2:    
            signin()
        
        
def session_start():
    """initial get to the page

    Args:
        -

    Returns:
        -
    """ 
    db.create_usertable()
    db.add_userdata('yabebal@10academy.org',hash.make_hashes('amestkilo'),'superAdmin')
    db.add_userdata('yabebal@gmail.com',hash.make_hashes('amestkilo'),'staff')    

    st.session_state["login"] = "unsuccess"
    st.session_state["hasLoggedIn"] = False
    st.session_state["selector"] = "notselected"
    
    if "login" not in st.session_state or st.session_state["login"] == "unsuccess":
       
        #landingScreen()
        pageselection(st.session_state["selector"])


    if "login" in st.session_state and st.session_state["login"] == "success":
                
        redirect_to_content()
        
session_start()
