import streamlit as st
import json

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

def calculate_score(field1, field2, field3):
    base_score = max(100 - field1, 0)
    multiplier = field2
    time_multiplier = max(0.5, min(1.5, 1.5 - 0.1 * max(0, field3 - 6)))
    return base_score * multiplier * time_multiplier, time_multiplier

def get_leaderboard(data):
    return sorted(((name, max((entry["score"] for entry in scores), default=0)) for name, scores in data.items()), key=lambda x: x[1], reverse=True)

def main():
    st.title("Score Leaderboard")
    data = load_data()

    # Form for data entry
    with st.form("score_form"):
        names = list(data.keys())
        selected_name = st.selectbox("Select a person or enter a new name", ["New person"] + names)
        if selected_name == "New person":
            selected_name = st.text_input("Enter new name")
        
        field1 = st.number_input("Field 1 (0-100)", min_value=0, max_value=100, value=0)
        field2 = st.selectbox("Field 2 Multiplier", [0, 1, 2])
        field3 = st.selectbox("Field 3 Time (seconds)", list(range(1, 13)))
        submitted = st.form_submit_button("Submit")

        if submitted and selected_name:
            total_score, time_multiplier = calculate_score(field1, field2, field3)
            data.setdefault(selected_name, []).append({"field1": field1, "field2": field2, "field3": field3, "time_multiplier": time_multiplier, "score": total_score})
            save_data(data)
            st.success(f"Recorded score {total_score:.2f} for {selected_name}")
            st.rerun()

    # Leaderboard
    st.header("Leaderboard")
    leaderboard = get_leaderboard(data)
    for name, high_score in leaderboard:
        if st.button(name):
            st.session_state["selected_person"] = name
            st.rerun()
        st.write(f"{name}: {high_score:.2f}")
    
    # Delete a person
    if st.button("Delete a Person"):
        person_to_delete = st.selectbox("Select a person to delete", names)
        if st.button(f"Confirm Delete {person_to_delete}"):
            del data[person_to_delete]
            save_data(data)
            st.success(f"Deleted {person_to_delete}")
            st.rerun()

    # Detailed view
    if "selected_person" in st.session_state:
        selected_person = st.session_state["selected_person"]
        st.header(f"{selected_person}'s Scores")
        
        records = data[selected_person]
        for i, record in enumerate(records):
            st.write(f"Field1: {record['field1']}, Field2: {record['field2']}, Field3: {record['field3']}, Time Multiplier: {record['time_multiplier']:.2f}, Score: {record['score']:.2f}")
            if st.button(f"Delete Record {i}"):
                records.pop(i)
                save_data(data)
                st.success("Record deleted")
                st.rerun()
        
        if st.button("Back to Leaderboard"):
            del st.session_state["selected_person"]
            st.rerun()

if __name__ == "__main__":
    main()
