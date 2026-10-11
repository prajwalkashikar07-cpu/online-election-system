import streamlit as st
import sqlite3
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Online Election System", page_icon="🗳️", layout="wide")

# Custom CSS: Transform Radio Buttons into Large Professional Nav Cards
st.markdown("""
    <style>
    /* Light Background for Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        padding-top: 1rem;
    }
    
    /* Hide Default Radio Circles entirely */
    [data-testid="stSidebar"] div[role="radiogroup"] label div:first-child {
        display: none !important;
    }

    /* Style the Radio Option Container into Bold Cards */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin-bottom: 12px !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }

    /* Hover Effect */
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        border-color: #2563eb !important;
        background-color: #eff6ff !important;
        transform: translateY(-1px);
    }

    /* Label Text Styling: Large, Bold, Clean Spacing */
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin: 0 !important;
        letter-spacing: 0.3px !important;
    }

    /* Active Selected Card Styling */
    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] {
        background-color: #2563eb !important;
        border-color: #1d4ed8 !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] p {
        color: #ffffff !important;
    }

    /* Quick Status Card */
    .status-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 14px;
        border: 1px solid #e2e8f0;
        margin-top: 25px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .status-title {
        font-size: 11px;
        font-weight: bold;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .status-value {
        font-size: 13px;
        color: #10b981;
        font-weight: 700;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("online_election.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS voters (
                    voter_name TEXT PRIMARY KEY, 
                    has_voted INTEGER DEFAULT 0
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY, 
                    name TEXT
                )''')
    
    c.execute("SELECT COUNT(*) FROM candidates")
    count = c.fetchone()[0]
    
    candidates_list = [
        (1, "Prof. Ankush Ajankar (Head of Department - Computer Science)"),
        (2, "Prof. Saurabh Darokar (Assistant Professor - Software Engineering)"),
        (3, "Prof. Rishikesh Sayande (Assistant Professor - Data Structures & Algorithms)"),
        (4, "Prof. Snehal Deshmukh (Assistant Professor - Web Technologies & UI/UX)"),
        (5, "Prof. Sakshi Gayki (Assistant Professor - Database Management Systems)")
    ]
    
    if count == 0:
        c.executemany("INSERT INTO candidates (id, name) VALUES (?, ?)", candidates_list)
    else:
        for c_id, c_name in candidates_list:
            c.execute("INSERT OR REPLACE INTO candidates (id, name) VALUES (?, ?)", (c_id, c_name))

    c.execute('''CREATE TABLE IF NOT EXISTS votes (
                    candidate_id INTEGER PRIMARY KEY, 
                    count INTEGER
                )''')
    for c_id, _ in candidates_list:
        c.execute("INSERT OR IGNORE INTO votes (candidate_id, count) VALUES (?, 0)", (c_id,))

    conn.commit()
    conn.close()

init_db()

def get_voters():
    conn = sqlite3.connect("online_election.db")
    df = pd.read_sql("SELECT * FROM voters", conn)
    conn.close()
    return df

def get_candidates():
    conn = sqlite3.connect("online_election.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM candidates")
    data = c.fetchall()
    conn.close()
    return {row[0]: row[1] for row in data}

def get_votes():
    conn = sqlite3.connect("online_election.db")
    c = conn.cursor()
    c.execute("SELECT candidate_id, count FROM votes")
    data = c.fetchall()
    conn.close()
    return {row[0]: row[1] for row in data}

# --- SIDEBAR DESIGN ---
with st.sidebar:
    st.markdown("## 🗳️ Navigation Menu")
    st.markdown("---")
    
    menu = st.radio(
        "NAVIGATION",
        ["📝  Voter Registration", "🗳️  Cast Vote", "📊  Live Analytics", "🔒  Admin Portal"],
        label_visibility="collapsed"
    )
    
    df_voters = get_voters()
    votes_dict = get_votes()
    total_cast = sum(votes_dict.values())
    total_reg = len(df_voters)
    
    st.markdown(f"""
        <div class="status-card">
            <div class="status-title">System Status</div>
            <div class="status-value">🟢 Engine: Active & Encrypted</div>
            <hr style="margin: 8px 0; border-color: #f1f5f9;">
            <div style="font-size: 13px; color: #334155;">
                <b>Registered Voters:</b> {total_reg}<br>
                <b>Total Cast Votes:</b> {total_cast}
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN APP LAYOUT ---
st.title("🌟Online Election & Analytics System")
st.markdown("A professional web-based electronic voting system with real-time database persistence.")

# 1. VOTER REGISTRATION
if "Voter Registration" in menu:
    st.header("📝 Voter Registration Portal")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        voter_name = st.text_input("Enter Student Full Name for Registration:").strip().title()
        if st.button("Register Voter", type="primary"):
            if not voter_name:
                st.warning("Voter name cannot be empty.")
            else:
                conn = sqlite3.connect("online_election.db")
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO voters (voter_name, has_voted) VALUES (?, 0)", (voter_name,))
                    conn.commit()
                    st.success(f"Success! Voter '{voter_name}' registered successfully.")
                except sqlite3.IntegrityError:
                    st.error("Error: This voter is already registered in the system.")
                finally:
                    conn.close()
                    
    with col2:
        st.info(f"**Total Registered Voters:** {total_reg}")

# 2. CAST VOTE
elif "Cast Vote" in menu:
    st.header("🗳️ Electronic Voting Section")
    voter_name = st.text_input("Enter Your Registered Student Name:").strip().title()
    
    if voter_name:
        conn = sqlite3.connect("online_election.db")
        c = conn.cursor()
        c.execute("SELECT has_voted FROM voters WHERE voter_name = ?", (voter_name,))
        result = c.fetchone()
        conn.close()
        
        if result is None:
            st.error("Voter name not found! Please register first.")
        elif result[0] == 1:
            st.warning(f"Access Denied, {voter_name}: You have already cast your vote.")
        else:
            st.success(f"Verification Successful! Welcome, {voter_name}. Select your faculty candidate below:")
            candidates = get_candidates()
            choice = st.radio(
                "Select Faculty Candidate",
                options=list(candidates.keys()),
                format_func=lambda x: candidates[x]
            )
            
            if st.button("Submit Vote Securely", type="primary"):
                conn = sqlite3.connect("online_election.db")
                c = conn.cursor()
                c.execute("UPDATE votes SET count = count + 1 WHERE candidate_id = ?", (choice,))
                c.execute("UPDATE voters SET has_voted = 1 WHERE voter_name = ?", (voter_name,))
                conn.commit()
                conn.close()
                st.balloons()
                st.success(f"Vote successfully recorded for {candidates[choice]}!")

# 3. LIVE ANALYTICS
elif "Live Analytics" in menu:
    st.header("📊 Live Election Analytics & Results")
    candidates = get_candidates()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Votes Cast", total_cast)
    col2.metric("Registered Voters", total_reg)
    turnout = (total_cast / total_reg * 100) if total_reg > 0 else 0
    col3.metric("Voter Turnout", f"{turnout:.1f}%")
    
    st.markdown("---")
    
    if total_cast == 0:
        st.info("No votes recorded yet. Real-time graphs will render after voting begins.")
    else:
        col_left, col_right = st.columns(2)
        
        chart_data = {}
        with col_left:
            st.subheader("Candidate Vote Share Breakdown")
            for num, name in candidates.items():
                v_count = votes_dict.get(num, 0)
                pct = (v_count / total_cast) * 100 if total_cast > 0 else 0
                chart_data[name] = v_count
                st.write(f"**{name}**: {v_count} votes ({pct:.2f}%)")
                st.progress(pct / 100)
                
        with col_right:
            st.subheader("Visual Distribution Graph")
            df_chart = pd.DataFrame(list(chart_data.items()), columns=["Candidate", "Votes"])
            st.bar_chart(df_chart.set_index("Candidate"))
            
        max_votes = max(votes_dict.values())
        winners = [candidates[num] for num in candidates if votes_dict.get(num, 0) == max_votes]
        
        st.markdown("---")
        if len(winners) == 1:
            st.success(f"🏆 **Current Leading Winner: {winners[0]}**")
        else:
            st.warning(f"⚠️ **Result Status: Tie between:** " + ", ".join(winners))

# 4. ADMIN PORTAL
elif "Admin Portal" in menu:
    st.header("🔒 Restricted Admin Control Panel")
    
    password = st.text_input("Enter Administrator Password:", type="password")
    if password == "admin123":
        st.success("Admin Authorization Granted!")
        
        tab1, tab2 = st.tabs(["Voter Directory Logs", "Database Management"])
        
        with tab1:
            st.subheader("Registered Voters Directory")
            df = get_voters()
            if not df.empty:
                df['Status'] = df['has_voted'].apply(lambda x: 'Voted' if x == 1 else 'Not Voted')
                st.dataframe(df[['voter_name', 'Status']], use_container_width=True)
            else:
                st.info("No voter records found in database.")
                
        with tab2:
            st.subheader("System Reset Actions")
            if st.button("⚠️ Reset Entire Election Database", type="primary"):
                conn = sqlite3.connect("online_election.db")
                c = conn.cursor()
                c.execute("DELETE FROM voters")
                c.execute("UPDATE votes SET count = 0")
                conn.commit()
                conn.close()
                st.success("Election data reset successfully!")
    elif password:
        st.error("Incorrect Admin Password! (Hint: admin123)")