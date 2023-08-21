import streamlit as st
import pymongo
import yaml
import time
from yaml.loader import SafeLoader
from streamlit_authenticator import Authenticate

st.set_page_config(page_title= "VedsuTechnology", page_icon="📧")
st.title("Welcome to User Registration")
#Database connections
@st.cache_resource
def init_connection():
   
    try:
        db_username = st.secrets.db_username
        db_password = st.secrets.db_password

        mongo_uri_template = "mongodb+srv://{username}:{password}@emailreader.elzbauk.mongodb.net/"
        mongo_uri = mongo_uri_template.format(username=db_username, password=db_password)

        client = pymongo.MongoClient(mongo_uri)
        return client
    except:
        st.write("Connection Could not be Established with database")
#  Database
client = init_connection()
db= client['EmailDatabase']
collection_usersdetail = db['Users']

def user():
    with st.sidebar.expander("Enter user details"): 
        st.write("----------------------------------")
        username = st.text_input("Enter Handler name")
        emailid = st.text_input("Enter Email id")
        passwordid = st.text_input("Enter Password")
        imapserver = st.text_input("Enter imap server")
        status = st.radio("Choose Status", ["Active", "Inactive"])
        if st.button("Submit"):
            user_data = {
                "username": username,
                "emailid": emailid,
                "password": passwordid,
                "status": status,
                "imapserver":imapserver,
                "inbox":"",
                "spam":"",
                "lastupdated":""
            }
            # Perform the insert operation
            try:
               collection_usersdetail.insert_one(user_data)
               st.success("User details submitted successfully!")
            except:
               st.warning("Submission unsuccessfully!")
            time.sleep(1)  # Pause for 1 second
            st.experimental_rerun()  # Trigger a rerun


        

    

def display():
    if not hasattr(st.session_state, "button_states"):
        st.session_state.button_states = {}

    with st.expander("Check existing users"):
        query = {}
        projection = {"emailid": 1, "username": 1, "status": 1,"password": 1,"imapserver":1 , "lastupdated":1, "inbox":1, "spam":1 ,"_id": 1}
        results = collection_usersdetail.find(query, projection)

        for result in results:
            status_color = "green" if result['status'] == "Active" else "red"

            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

            with col1:
                st.markdown(
                    f"Handler: <span style='color: orange;'>{result['username']}</span>",
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"Email ID: <span style='color: blue;'>{result['emailid']}</span>",
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(
                    f"Status: <span style='color: {status_color};'>{result['status']}</span>",
                    unsafe_allow_html=True
                )
            with col4:
                st.markdown(
                    f"Last updated: <span style='color: black;'>{result['lastupdated']}</span>",
                    unsafe_allow_html=True
                )

            with col5:
                st.markdown(
                    f"Inbox: <span style='color: orange;'>{result['inbox']}</span>",
                    unsafe_allow_html=True
                )
            
            with col6:
                st.markdown(
                    f"Spam: <span style='color: orange;'>{result['spam']}</span>",
                    unsafe_allow_html=True
                )
            
            with col7:
                updated_status = st.radio("Update status:", ["Active", "Inactive"], index=0 if result['status'] == "Active" else 1,key=f"update_status_{result['_id']}" )
                update_action_button = st.button("Update", key=f"update_action_button_{result['_id']}")
                if update_action_button:
                    try:
                            collection_usersdetail.update_one(
                             {"_id": result['_id']},
                             {"$set": { "status": updated_status}})
                            st.write("Status updated successfully!")
                            st.experimental_rerun()        
                    except:
                            st.write("Status updation unsucessful")
                            st.experimental_rerun()

            with col8:
                delete_button_key = f"delete_button_{result['_id']}"
                delete_button = st.button("Delete record", key=delete_button_key)
                if delete_button:
                    # Perform the delete action here
                    try:
                        collection_usersdetail.delete_one({"_id": result['_id']})
                        st.write("Deleted successfully!")
                    except:
                        st.write("Deletion unsuccessful")
                    st.experimental_rerun()

            st.write("------------------------------------------------------------")





def main():

    config_file_path = "./config.yaml"
    try:
        with open(config_file_path) as file:
            config = yaml.load(file, Loader=SafeLoader)
    except Exception as e:
        st.error(f"Error loading configuration file: {e}")
        st.stop()

    # Initialize the authenticator

    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    col1, col2 = st.columns(2)
    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        with st.container():
            user()
            with col1:
                st.markdown(f'Welcome- <span style="color: blue;"> *{name}*</span>',unsafe_allow_html=True)
            with col2:
                authenticator.logout('Logout', 'main')
            display()
    elif authentication_status==False:
        st.error("Username/password is incorrect")
    elif authentication_status == None:
        st.warning("Please enter your username and password")


if __name__=="__main__":
    main()
