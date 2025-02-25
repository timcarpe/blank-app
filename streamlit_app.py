import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Create a connection object to your Google Sheet.
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper functions to read and write data.
def read_data():
    df = conn.read()
    if df is None or df.empty:
        # Create an empty dataframe with the appropriate columns if no data exists.
        df = pd.DataFrame(columns=["Name", "Points Deducted", "Base Multiplier", "Time (Seconds)", "Total Score"])
    return df

def write_data(df):
    conn.write(df)

def get_leaderboard():
    df = read_data()
    if not df.empty:
        leaderboard = df.groupby("Name", as_index=False)["Total Score"].max()
        leaderboard = leaderboard.sort_values("Total Score", ascending=False)
    else:
        leaderboard = pd.DataFrame(columns=["Name", "Total Score"])
    return leaderboard

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

def get_person_history(name):
    df = read_data()
    person_df = df[df["Name"] == name]
    return person_df

def delete_person(name):
    df = read_data()
    df = df[df["Name"] != name]
    write_data(df)

def delete_record(index):
    df = read_data()
    df = df.drop(index=index)
    write_data(df)

def calculate_score(points_deducted, base_multiplier, time_seconds):
    base_score = max(100 - points_deducted, 0)
    time_multiplier = max(0.5, min(1.5, 1.5 - 0.1 * max(0, time_seconds - 6)))
    total_score = base_score * base_multiplier * time_multiplier
    return total_score

def main():
    st.title("Score Leaderboard using Google Sheets")
    
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
    leaderboard = get_leaderboard()
    if not leaderboard.empty:
        st.dataframe(leaderboard)
    
    # Delete a person.
    if not leaderboard.empty:
        person_to_delete = st.selectbox("Select a person to delete", leaderboard["Name"].tolist())
        if st.button("Delete Selected Person"):
            delete_person(person_to_delete)
            st.success(f"Deleted {person_to_delete}")
            st.experimental_rerun()
    
    # View individual records.
    if not leaderboard.empty:
        selected_person = st.selectbox("View records for", leaderboard["Name"].tolist())
        if selected_person:
            st.header(f"{selected_person}'s Scores")
            history = get_person_history(selected_person)
            if not history.empty:
                st.dataframe(history)
                # Here the dataframe index is used for record identification.
                record_to_delete = st.selectbox("Select a record index to delete", history.index.tolist())
                if st.button("Delete Selected Record"):
                    delete_record(record_to_delete)
                    st.success("Record deleted")
                    st.experimental_rerun()

if __name__ == "__main__":
    main()
