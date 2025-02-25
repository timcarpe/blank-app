import streamlit as st
import json
import pandas as pd

DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_score(points_deducted, base_multiplier, time_seconds):
    base_score = max(100 - points_deducted, 0)
    time_multiplier = max(0.5, min(1.5, 1.5 - 0.1 * max(0, time_seconds - 6)))
    total_score = base_score * base_multiplier * time_multiplier
    return total_score, time_multiplier

def get_leaderboard(data):
    leaderboard = []
    for name, records in data.items():
        if records:
            highest_score = max(record["score"] for record in records)
            leaderboard.append({
                "Name": name,
                "Highest Score": highest_score
            })
    return sorted(leaderboard, key=lambda x: x["Highest Score"], reverse=True)

def main():
    st.title("Score Leaderboard")
    data = load_data()

    # Form for data entry
    with st.form("score_form"):
        names = list(data.keys())
        selected_name = st.selectbox("Select a person or enter a new name", ["New person"] + names)
        if selected_name == "New person":
            selected_name = st.text_input("Enter new name")
        
        points_deducted = st.number_input("Build Points(0-100)", min_value=0, max_value=100, value=0)
        base_multiplier = st.selectbox("Base Multiplier", [0, 1, 2])
        time_seconds = st.selectbox("Time (seconds)", list(range(1, 13)))
        submitted = st.form_submit_button("Submit")

        if submitted and selected_name:
            total_score, time_multiplier = calculate_score(points_deducted, base_multiplier, time_seconds)
            data.setdefault(selected_name, []).append({
                "Points Deducted": points_deducted,
                "Base Multiplier": base_multiplier,
                "Time (seconds)": time_seconds,
                "Time Multiplier": time_multiplier,
                "Score": total_score
            })
            save_data(data)
            st.success(f"Recorded score {total_score:.2f} for {selected_name}")
            st.rerun()

    # Leaderboard in table format
    st.header("Leaderboard")
    leaderboard = get_leaderboard(data)
    df_leaderboard = pd.DataFrame(leaderboard)
    if not df_leaderboard.empty:
        df_leaderboard["Name"] = df_leaderboard["Name"].apply(lambda name: f"[**{name}**](#{name.replace(' ', '-')})")
        st.markdown(df_leaderboard.to_markdown(index=False), unsafe_allow_html=True)
    
    # Delete a person
    if st.button("Delete a Person"):
        person_to_delete = st.selectbox("Select a person to delete", names)
        if st.button(f"Confirm Delete {person_to_delete}"):
            del data[person_to_delete]
            save_data(data)
            st.success(f"Deleted {person_to_delete}")
            st.rerun()

    # Detailed view when clicking on a name
    for name in data.keys():
        if f"#{name.replace(' ', '-')}" in st.query_params:
            st.header(f"{name}'s Scores")
            records = data[name]
            df_records = pd.DataFrame(records)
            if not df_records.empty:
                st.dataframe(df_records)
            
            # Delete record functionality
            record_to_delete = st.selectbox("Select a record to delete", df_records.index.tolist())
            if st.button("Delete Selected Record"):
                data[name].pop(record_to_delete)
                save_data(data)
                st.success("Record deleted")
                st.rerun()
            break

if __name__ == "__main__":
    main()
