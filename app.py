import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="Habit & Productivity Tracker",
    page_icon="🎯",
    layout="wide"
)

# 2. Load Data with Cache Handling
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv')
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Date_Time', 'Habit', 'Status', 'Category', 'Notes'])
        df.to_csv('data.csv', index=False)
        return df

df = load_data()

# 3. Main Dashboard Title
st.title("🎯 Habit & Productivity Tracker")
st.markdown("Welcome to your personal habit and productivity control panel.")

# 4. Top KPI Metrics (مؤشرات الأداء السريعة)
if not df.empty:
    total_habits = len(df)
    completed_habits = len(df[df['Status'] == 'Completed'])
    completion_rate = int((completed_habits / total_habits) * 100) if total_habits > 0 else 0
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Habits Recorded", total_habits)
    col_m2.metric("Completed Habits", completed_habits)
    col_m3.metric("Completion Rate", f"{completion_rate}%")
    st.markdown("---")

# 5. Sidebar for Adding, Deleting & Exporting Data
st.sidebar.header("⚙️ Manage Habits")

action_tab = st.sidebar.radio("Choose Action", ["Add New Habit", "Delete Habit"])

if action_tab == "Add New Habit":
    with st.sidebar.form("add_habit_form"):
        habit_name = st.text_input("Habit Name (e.g., Reading, Workout)")
        category = st.selectbox("Category", ["Health", "Self-Development", "Work", "Study", "Other"])
        status = st.radio("Status", ["Completed", "Missed"])
        
        col_d, col_t = st.columns(2)
        with col_d:
            habit_date = st.date_input("Date", datetime.today())
        with col_t:
            habit_time = st.time_input("Time", datetime.now().time())
            
        notes = st.text_area("Additional Notes")
        submit_button = st.form_submit_button(label="Save Habit")

    if submit_button:
        if habit_name.strip() == "":
            st.sidebar.error("Please enter the habit name!")
        else:
            combined_datetime = f"{habit_date} {habit_time.strftime('%H:%M')}"
            new_data = pd.DataFrame([{
                "Date_Time": combined_datetime,
                "Habit": habit_name,
                "Status": status,
                "Category": category,
                "Notes": notes
            }])
            
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv('data.csv', index=False)
            st.cache_data.clear()
            st.sidebar.success("Habit saved successfully! 🎉")
            st.rerun()

else:
    with st.sidebar.form("delete_habit_form"):
        st.write("### Delete a Habit")
        if not df.empty:
            habit_to_delete = st.selectbox("Select Habit to Remove", df['Habit'].unique())
            delete_button = st.form_submit_button(label="Delete Habit")
        else:
            st.write("No data available to delete.")
            delete_button = False

    if delete_button and not df.empty:
        df = df[df['Habit'] != habit_to_delete]
        df.to_csv('data.csv', index=False)
        st.cache_data.clear()
        st.sidebar.success("Habit deleted successfully! 🗑️")
        st.rerun()

# Data Export Option in Sidebar
st.sidebar.markdown("---")
st.sidebar.header("📥 Export Data")
if not df.empty:
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Habits CSV",
        data=csv_data,
        file_name='habits_backup.csv',
        mime='text/csv',
    )

# 6. Interactive Table with Direct Status Editing
st.subheader("📋 Current Habits Record (Editable Status)")
if not df.empty:
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    
    if not edited_df.equals(df):
        edited_df.to_csv('data.csv', index=False)
        st.cache_data.clear()
        st.success("Changes saved successfully!")
else:
    st.info("No records found. Add your first habit from the sidebar.")

# 7. Analytics and Charts
if not df.empty:
    st.markdown("---")
    st.subheader("📊 Performance Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        status_counts = df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_status = px.pie(
            status_counts, 
            names='Status', 
            values='Count', 
            title="Habit Completion Ratio (Completed vs Missed)",
            hole=0.4
        )
        st.plotly_chart(fig_status, use_container_width=True)
        
    with col2:
        category_counts = df['Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        fig_cat = px.bar(
            category_counts, 
            x='Category', 
            y='Count', 
            title="Habits Distribution by Category",
            color='Category'
        )
        st.plotly_chart(fig_cat, use_container_width=True)

# 8. Weekly Schedule & Appointments Tracker
st.markdown("---")
st.subheader("📅 Weekly Schedule & Appointments Tracker")

schedule_file = 'weekly_schedule.csv'

@st.cache_data
def load_schedule():
    try:
        return pd.read_csv(schedule_file)
    except FileNotFoundError:
        default_sched = pd.DataFrame(columns=['Day', 'Time', 'Task_Appointment', 'Completed'])
        default_sched.to_csv(schedule_file, index=False)
        return default_sched

sched_df = load_schedule()

st.sidebar.markdown("---")
st.sidebar.header("🗓️ Manage Schedule")
sched_action = st.sidebar.radio("Schedule Action", ["Add Appointment", "Delete Appointment"])

if sched_action == "Add Appointment":
    with st.sidebar.form("sched_form"):
        day_choice = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        sched_time = st.time_input("Appointment Time", datetime.now().time())
        task_name = st.text_input("Task / Appointment Description")
        task_status = st.checkbox("Mark as Completed")
        
        sched_submit = st.form_submit_button("Add to Schedule")
        
    if sched_submit:
        if task_name.strip() == "":
            st.sidebar.error("Please enter a task description.")
        else:
            new_sched = pd.DataFrame([{
                "Day": day_choice,
                "Time": sched_time.strftime('%H:%M'),
                "Task_Appointment": task_name,
                "Completed": task_status
            }])
            sched_df = pd.concat([sched_df, new_sched], ignore_index=True)
            sched_df.to_csv(schedule_file, index=False)
            st.cache_data.clear()
            st.sidebar.success("Appointment added successfully!")
            st.rerun()
else:
    with st.sidebar.form("delete_sched_form"):
        st.write("### Delete an Appointment")
        if not sched_df.empty:
            sched_to_delete = st.selectbox("Select Task to Remove", sched_df['Task_Appointment'].unique())
            delete_sched_button = st.form_submit_button(label="Delete Appointment")
        else:
            st.write("No appointments available.")
            delete_sched_button = False

    if delete_sched_button and not sched_df.empty:
        sched_df = sched_df[sched_df['Task_Appointment'] != sched_to_delete]
        sched_df.to_csv(schedule_file, index=False)
        st.cache_data.clear()
        st.sidebar.success("Appointment deleted successfully! 🗑️")
        st.rerun()

if not sched_df.empty:
    st.write("### Your Schedule Overview (Editable)")
    edited_sched = st.data_editor(sched_df, use_container_width=True, num_rows="dynamic")
    if not edited_sched.equals(sched_df):
        edited_sched.to_csv(schedule_file, index=False)
        st.cache_data.clear()
        st.success("Schedule updated!")
else:
    st.info("No appointments added for this week yet.")
