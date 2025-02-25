import streamlit as st
import pandas as pd
from sqlalchemy.sql import text

# Connect to Neon database
conn = st.connection("neon", type="sql")

def init_db():
    create_table_query = text("""
    CREATE TABLE IF NOT EXISTS scores (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        points_deducted INTEGER,
        base_multiplier INTEGER,
        time_seconds INTEGER,
        total_score REAL
    );
    """)
    with conn.session as session:
        session.execute(create_table_query)
        session.commit()

def add_record(name, points_deducted, base_multiplier, time_seconds, total_score):
    insert_query = text("""
    INSERT INTO scores (name, points_deducted, base_multiplier, time_seconds, total_score)
    VALUES (:name, :points_deducted, :base_multiplier, :time_seconds, :total_score);
    """)
    with conn.session as session:
        session.execute(insert_query, {
            "name": name,
            "points_deducted": points_deducted,
            "base_multiplier": base_multiplier,
            "time_seconds": time_seconds,
            "total_score": total_score
        })
        session.commit()

def get_leaderboard():
    query = text("""
    SELECT name, MAX(total_score) AS highest_score
    FROM scores
    GROUP BY name
    ORDER BY highest_score DESC;
    """)
    with conn.session as session:
        result = session.execute(query).fetchall()
        return pd.DataFrame(result, columns=["name", "highest_score"])

def get_person_history(name):
    query = text("SELECT * FROM scores WHERE name = :name ORDER BY id;")
    with conn.session as session:
        result = session.execute(query, {"name": name}).fetchall()
        return pd.DataFrame(result, columns=["id", "name", "points_deducted", "base_multiplier", "time_seconds", "total_score"])

def delete_person(name):
    query = text("DELETE FROM scores WHERE name = :name;")
    with conn.session as session:
        session.execute(query, {"name": name})
        session.commit()

def delete_record(record_id):
    query = text("DELETE FROM scores WHERE id = :record_id;")
    with conn.session as session:
        session.execute(query, {"record_id": record_id})
        session.commit()

def calculate_score(points_deducted, base_multiplier, time_seconds):
    base_score = max(100 - points_deducted, 0)
    time_multiplier = max(0.5, min(1.5, 1.5 - 0.1 * max(0, time_seconds - 6)))
    return base_score * base_multiplier * time_multiplier

def main():
    st.title("Score Leaderboard using Neon Database")
    init_db()
    
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
    
    st.header("Leaderboard")
    leaderboard = get_leaderboard()
    if not leaderboard.empty:
        st.dataframe(leaderboard)
    
    st.header("Person History")
    if not leaderboard.empty:
        selected_person = st.selectbox("View records for", leaderboard["name"].tolist())
        if selected_person:
            history = get_person_history(selected_person)
            if not history.empty:
                st.dataframe(history)
                record_to_delete = st.selectbox("Select record ID to delete", history["id"].tolist())
                if st.button("Delete Selected Record"):
                    delete_record(record_to_delete)
                    st.success("Record deleted")
                    st.experimental_rerun()
        
        person_to_delete = st.selectbox("Delete person", leaderboard["name"].tolist())
        if st.button("Delete Selected Person"):
            delete_person(person_to_delete)
            st.success(f"Deleted {person_to_delete}")
            st.experimental_rerun()

if __name__ == "__main__":
    main()
