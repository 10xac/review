import streamlit as st
#from PIL import Image
import utils.hashManagement as hash
import db.databaseManagement as db
import ui.userManagement as userManagement
import page

def signin():
    """A form validator which is used to get email and password

    Args:
        -

    Returns:
        -
    """ 
    with st.sidebar.form(key = 'my_form'):
        email_text_input = st.text_input(label = 'Email')
        password_text_input = st.text_input(label = 'Password', type = 'password')
        m = st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: rgb(255, 77, 77);
            color:#ffffff;
            font-size:30px;
            width:100%;
        }
        div.stButton > button:hover {
            background-color: #ffffff;
            color:rgb(255, 77, 77);
            font-size:30px;

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
                st.sidebar.error("Invalid Credentials")
                st.sidebar.error("No User")
         
def landingScreen():
    """Main screen of the site
    Args:
        -

    Returns:
        -
    """
    #image = Image.open('data/images/logo.png')
    #st.image(image, use_column_width=True)
    st.title("")
    st.header("Welcome to 10Academy Application Review Engine")


def changeselectorStatus(status, value, *arg):
    """change the status of selector to selected\n should be updated
    
    Args:
        status and value
        
    Returns:
        -
    """
    st.session_state['selector'] = "selected"

def sidebarselection(selector):
    """display sidebar according to selector value\n selector is to check user has pressed login or not

    Args:
        selector either "selected" or "notselected"

    Returns:
        -
    """


    if(st.session_state["selector"] == "notselected"):
        m = st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: rgb(255, 77, 77);
            color:#ffffff;
            font-size:30px;
            width:100%;
        }
        div.stButton > button:hover {
            background-color: #ffffff;
            color:rgb(255, 77, 77);
            font-size:30px;
            }
        </style>""", unsafe_allow_html=True)
        st.sidebar.button("Login", 
                          key = 'signin', 
                          on_click = changeselectorStatus(
                              st.session_state['selector'],"selected")
                         )       
    else:
        signin()
        
def session_start():
    """initial get to the page

    Args:
        -

    Returns:
        -
    """ 
    db.create_usertable()

    if "login" not in st.session_state or st.session_state["login"] == "unsuccess":
        print("lp.login.status=unsuccess")
        
        st.session_state["login"] = "unsuccess"
        
        if "selector" not in st.session_state:
            st.session_state["selector"] = "notselected"
            
        landingScreen()
        sidebarselection(st.session_state["selector"])
        st.session_state["hasLoggedIn"] = False
        
    elif st.session_state["login"] == "success":
        
        if st.session_state["access"] == "student":
            # studentPage.main()
            st.sidebar.header("Student Page")
            st.sidebar.subheader("Under construction")
            st.session_state["hasLoggedIn"] = True 

        elif st.session_state["access"] == "staff":
            st.success("You are successfully logged in")
            st.session_state["hasLoggedIn"] = True
            page.main()
            
        elif st.session_state["access"] == "superAdmin":
            st.success("You are successfully logged in")
            st.session_state["hasLoggedIn"] = True
            userManagement.main()

session_start()
