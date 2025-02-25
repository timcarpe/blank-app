import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Create a connection object to your Google Sheet.
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper function to read data.
def read_data():
    df = conn.read(worksheet="Sheet1", ttl="10m")
    if df is None or df.empty:
        df = pd.DataFrame(columns=["Name", "Points Deducted", "Base Multiplier", "Time (Seconds)", "Total Score"])
    return df

# Helper function to write data.
def write_data(df):
    conn.write(df, worksheet="Sheet1")

# Function to add a record.
def add_record(name, points_deducted, base_multiplier, time_seconds, total_score):
    df = read_data()
    new_row = pd.DataFrame({
        "Name": [name],
        "Points Deducted": [points_deducted],
        "Base Multiplier": [base_multiplier],
        "Time (Seconds)": [time_seconds],
        "Total Score": [total_score]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    write_data(df)

# Function to calculate score.
def calculate_score(points_deducted, base_multiplier, time_seconds):
    base_score = max(100 - points_deducted, 0)
    time_multiplier = max(0.5, min(1.5, 1.5 - 0.1 * max(0, time_seconds - 6)))
    return base_score * base_multiplier * time_multiplier

# Main application.
def main():
    st.title("Google Sheets Leaderboard")
    
    # Form for data entry.
    with st.form("score_form"):
        name = st.text_input("Enter Name")
        points_deducted = st.number_input("Points Deducted (0-100)", min_value=0, max_value=100, value=0)
        base_multiplier = st.selectbox("Base Multiplier", [0, 1, 2])
        time_seconds = st.selectbox("Time (seconds)", list(range(1, 13)))
        submitted = st.form_submit_button("Submit")
        
        if submitted and name:
            total_score = calculate_score(points_deducted, base_multiplier, time_seconds)
            add_record(name, points_deducted, base_multiplier, time_seconds, total_score)
            st.success(f"Recorded score {total_score:.2f} for {name}")
            st.experimental_rerun()
    
    # Display the leaderboard.
    st.header("Leaderboard")
    df = read_data()
    if not df.empty:
        st.dataframe(df)

if __name__ == "__main__":
    main()
