import streamlit as st

def check_login():
    st.sidebar.title("🔒 Login Required")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        valid_username = st.secrets["login"]["username"]
        valid_password = st.secrets["login"]["password"]

        if username == valid_username and password == valid_password:
            st.sidebar.success("✅ Login successful")
            st.session_state.logged_in = True
        else:
            if username or password:
                st.sidebar.error("❌ Invalid credentials")
            return False

    return st.session_state.logged_in

