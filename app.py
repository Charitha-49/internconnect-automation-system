import streamlit as st
import mysql.connector
import hashlib
import re
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="InternConnect", layout="wide")

# ---------------- DATABASE CONNECTION ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="#Siri4923",
    database="internship_portal"
)
cursor = conn.cursor(buffered=True)  # buffered=True helps with fetchone() issues

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_id = None

# ---------------- VALIDATION FUNCTIONS ----------------
def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

def validate_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"\d", password)
    )

def hash_password(password):
    """Returns SHA256 hashed password"""
    return hashlib.sha256(password.encode()).hexdigest()

def is_field_empty(*fields):
    """Checks if any field is empty"""
    return any(not f for f in fields)

# ---------------- HELPER FUNCTIONS ----------------
def fetch_user(email, hashed_password):
    cursor.execute("SELECT id, role FROM users WHERE email=%s AND password=%s", (email, hashed_password))
    return cursor.fetchone()

def check_subscription(user_id, internship_id):
    cursor.execute("SELECT * FROM subscriptions WHERE user_id=%s AND internship_id=%s", (user_id, internship_id))
    return cursor.fetchone()

def subscribe(user_id, internship_id):
    cursor.execute("INSERT INTO subscriptions (user_id, internship_id) VALUES (%s, %s)", (user_id, internship_id))
    conn.commit()

def unsubscribe(user_id, internship_id):
    cursor.execute("DELETE FROM subscriptions WHERE user_id=%s AND internship_id=%s", (user_id, internship_id))
    conn.commit()

def post_internship(title, description, deadline):
    cursor.execute("INSERT INTO internships (title, description, deadline) VALUES (%s, %s, %s)",
                   (title, description, deadline))
    conn.commit()

def delete_internship(internship_id):
    cursor.execute("DELETE FROM internships WHERE id=%s", (internship_id,))
    conn.commit()

# ---------------- SIDEBAR ----------------
st.sidebar.title("Menu")
if st.session_state.logged_in:
    menu = st.sidebar.radio("Go to", ["Home", "Dashboard", "Profile", "Logout"])
else:
    menu = st.sidebar.radio("Go to", ["Home", "Login", "Signup"])

st.title("🎓 InternConnect")

# =========================================================
# HOME
# =========================================================
if menu == "Home":
    st.subheader("Available Internships")
    search_query = st.text_input("🔎 Search by Title")

    query = "SELECT id, title, description, deadline FROM internships"
    params = ()
    if search_query:
        query += " WHERE title LIKE %s"
        params = (f"%{search_query}%",)
    query += " ORDER BY deadline ASC"

    cursor.execute(query, params)
    internships = cursor.fetchall()

    if internships:
        for internship in internships:
            internship_id, title, desc, deadline = internship
            st.markdown(f"### 🔹 {title}")
            st.write(desc)
            st.write(f"📅 Deadline: {deadline}")

            if st.session_state.logged_in and st.session_state.role == "user":
                subscription = check_subscription(st.session_state.user_id, internship_id)
                col1, col2 = st.columns(2)
                if subscription:
                    with col1:
                        if st.button("Unsubscribe", key=f"unsub_{internship_id}"):
                            unsubscribe(st.session_state.user_id, internship_id)
                            st.success("Unsubscribed Successfully")
                            st.rerun()
                else:
                    with col1:
                        if st.button("Subscribe", key=f"sub_{internship_id}"):
                            subscribe(st.session_state.user_id, internship_id)
                            st.success("Subscribed Successfully")
                            st.rerun()
            st.markdown("---")
    else:
        st.info("No internships found.")

# =========================================================
# LOGIN
# =========================================================
elif menu == "Login":
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Login")

    if login_submit:
        if is_field_empty(email, password):
            st.error("All fields are required.")
        elif not validate_email(email):
            st.error("Invalid email format.")
        else:
            hashed = hash_password(password)
            user = fetch_user(email, hashed)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.role = user[1]
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

# =========================================================
# SIGNUP
# =========================================================
elif menu == "Signup":
    st.subheader("Create Account")
    with st.form("signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Register As", ["User", "Admin"])
        signup_submit = st.form_submit_button("Signup")

    if signup_submit:
        if is_field_empty(name, email, password):
            st.error("All fields are required.")
        elif not validate_email(email):
            st.error("Invalid email format.")
        elif not validate_password(password):
            st.error("Password must be 8+ chars with uppercase, lowercase, and number.")
        else:
            hashed = hash_password(password)
            try:
                cursor.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                    (name, email, hashed, role.lower())
                )
                conn.commit()
                st.success("Account created successfully!")
            except mysql.connector.Error:
                st.error("Email already registered.")

# =========================================================
# DASHBOARD (ADMIN)
# =========================================================
elif menu == "Dashboard":
    if st.session_state.role != "admin":
        st.warning("Access Denied. Admin Only.")
    else:
        st.subheader("📌 Post Internship")
        with st.form("post_form"):
            title = st.text_input("Internship Title")
            description = st.text_area("Description")
            deadline = st.date_input("Deadline", min_value=date.today())
            post_submit = st.form_submit_button("Post Internship")
        if post_submit:
            if is_field_empty(title, description):
                st.error("All fields required.")
            else:
                post_internship(title, description, deadline)
                st.success("Internship Posted Successfully!")

        st.markdown("---")
        st.subheader("📋 Manage Internships")
        cursor.execute("SELECT id, title, deadline FROM internships")
        data = cursor.fetchall()
        for row in data:
            col1, col2 = st.columns([4,1])
            col1.write(f"{row[1]} - Deadline: {row[2]}")
            if col2.button("Delete", key=f"del_{row[0]}"):
                delete_internship(row[0])
                st.success("Internship Deleted")
                st.rerun()

# =========================================================
# PROFILE
# =========================================================
elif menu == "Profile":
    st.subheader("👤 My Profile")
    cursor.execute("SELECT name, email, role FROM users WHERE id=%s", (st.session_state.user_id,))
    user = cursor.fetchone()
    st.write("**Name:**", user[0])
    st.write("**Email:**", user[1])
    st.write("**Role:**", user[2].capitalize())

    st.markdown("---")
    st.subheader("📌 My Subscriptions")
    cursor.execute("""
        SELECT i.title, i.deadline
        FROM internships i
        JOIN subscriptions s ON i.id = s.internship_id
        WHERE s.user_id=%s
    """, (st.session_state.user_id,))
    subs = cursor.fetchall()
    if subs:
        for sub in subs:
            st.write(f"{sub[0]} - Deadline: {sub[1]}")
    else:
        st.info("No active subscriptions.")

    st.markdown("---")
    st.subheader("🔐 Change Password")
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        reset_submit = st.form_submit_button("Update Password")
    if reset_submit:
        if is_field_empty(current_password, new_password, confirm_password):
            st.error("All fields required.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif not validate_password(new_password):
            st.error("Password must be 8+ chars with uppercase, lowercase, and number.")
        else:
            hashed_current = hash_password(current_password)
            cursor.execute("SELECT password FROM users WHERE id=%s", (st.session_state.user_id,))
            stored_password = cursor.fetchone()[0]
            if hashed_current != stored_password:
                st.error("Current password incorrect.")
            else:
                hashed_new = hash_password(new_password)
                cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed_new, st.session_state.user_id))
                conn.commit()
                st.success("Password Updated Successfully!")

# =========================================================
# LOGOUT
# =========================================================
elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_id = None
    st.success("Logged out successfully")
    st.rerun()