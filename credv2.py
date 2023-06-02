import streamlit as st
import json
from datetime import *
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests


def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day
def to_timestamp(int_val):
    year = int(int_val / 10000)
    month = int((int_val % 10000) / 100)
    day = int(int_val % 100)
    return pd.Timestamp(year=year, month=month, day=day).timestamp()

st.set_page_config("Visualization Board Admin", layout="wide")

if "q1" not in st.session_state:
        st.session_state.q1 = None
if "q2" not in st.session_state:
        st.session_state.q2 = None
if "q3" not in st.session_state:
        st.session_state.q3 = None
# if "login" not in st.session_state:
#         st.session_state.login = False
if "change" not in st.session_state:
        st.session_state.change = None

url = "https://raw.githubusercontent.com/Charlieletscode/GuardianFueltech-Visualization-Board-Admin/main/sampleData/q1.json"
response = requests.get(url)
data = json.loads(response.text)
st.session_state.q1 = pd.DataFrame(data)

url = "https://raw.githubusercontent.com/Charlieletscode/GuardianFueltech-Visualization-Board-Admin/main/sampleData/q2.json"
response = requests.get(url)
data = json.loads(response.text)
st.session_state.q2 = pd.DataFrame(data)

url = "https://raw.githubusercontent.com/Charlieletscode/GuardianFueltech-Visualization-Board-Admin/main/sampleData/q2.json"
response = requests.get(url)
data = json.loads(response.text)
st.session_state.q2 = pd.DataFrame(data)
header_image = "./header.jpg"
header_text = "Visualization Board Admin"

col1, col2 = st.columns([5, 2])
col1.title(header_text)
col2.image(header_image, use_column_width=True)

st.sidebar.subheader("BranchName")
q1_df = st.session_state.q1
q2_df = st.session_state.q2
q3_df = st.session_state.q3
branch_names = q1_df['BranchName'].unique()
all_option = "All"
unique_branch_names = [all_option] + list(branch_names)

selected_branches = st.sidebar.multiselect("Select Branches", unique_branch_names)

if all_option in selected_branches:
    selected_branches = unique_branch_names[1:]

filtered_q1_df = q1_df[q1_df['BranchName'].isin(selected_branches)]
filtered_q2_df = q2_df[q2_df['Service_Call_ID'].isin(filtered_q1_df['Service_Call_ID'])]

unique_service_call_ids = filtered_q2_df['Service_Call_ID'].unique()
all_option = "All"
selected_service_call_ids = st.sidebar.multiselect("Select Service Call IDs", unique_service_call_ids,
                                              default=unique_service_call_ids)

unique_service_call_ids = [all_option] + list(unique_service_call_ids)
if all_option in selected_service_call_ids:
    selected_service_call_ids = unique_service_call_ids[1:]
filtered_data = filtered_q2_df[(filtered_q2_df['BranchName'].isin(selected_branches)) &
                           (filtered_q2_df['Service_Call_ID'].isin(selected_service_call_ids))]

filtered_q2_df = filtered_q2_df[filtered_q2_df['Service_Call_ID'].isin(selected_service_call_ids)]
oldest_service_calls = filtered_q2_df.sort_values(by='DATE').head(10)

last_30_days = pd.to_datetime('today') - pd.DateOffset(days=30)
filtered_df = filtered_q2_df[pd.to_datetime(filtered_q2_df['DATE']) >= last_30_days]
top_10_customers = filtered_df['CUSTNMBR'].value_counts().nlargest(10)
top_10_df = pd.DataFrame({'CUSTNMBR': top_10_customers.index, 'Service_Call_Count': top_10_customers.values})
fig = go.Figure(data=go.Scatter(x=top_10_df['CUSTNMBR'], y=top_10_df['Service_Call_Count'], mode='lines+markers'))

fig.update_layout(
    title='Top 10 Customers by Service Call Count (Last 30 Days)',
    xaxis_title='',
    yaxis_title='',        
)

cols = st.columns(6)
total_service_calls_q1 = len(filtered_q1_df)
count_ws_job_number_q1 = filtered_q1_df['WS_Job_Number'].nunique()
redispatch_calls = "blank"
quote_needed = "blank"
parts_hold = "blank"
hold_other = "blank"
cols[0].markdown("<div style='text-align: center; height: 75px; '>"
            "<h4 style='margin-bottom: 0;'>Total Service Calls</h4>"
            "</div>"
            "<div style='text-align: center; padding-top: 10px;'>"
            f"<h4>{total_service_calls_q1}</h4>"
            "</div>", unsafe_allow_html=True)

cols[1].markdown("<div style='text-align: center; height: 75px; '>"
                "<h4 style='margin-bottom: 0;'>Total service call w/ jobs</h4>"
                "</div>"
                "<div style='text-align: center; padding-top: 10px;'>"
                f"<h4>{count_ws_job_number_q1}</h4>"
                "</div>", unsafe_allow_html=True)

cols[2].markdown("<div style='text-align: center; height: 75px; '>"
                "<h4 style='margin-bottom: 0;'>Redispatch Calls</h4>"
                "</div>"
                "<div style='text-align: center; padding-top: 10px;'>"
                f"<h4>{redispatch_calls}</h4>"
                "</div>", unsafe_allow_html=True)

cols[3].markdown("<div style='text-align: center; height: 75px; '>"
                "<h4 style='margin-bottom: 0;'>Quote Needed</h4>"
                "</div>"
                "<div style='text-align: center; padding-top: 10px;'>"
                f"<h4>{quote_needed}</h4>"
                "</div>", unsafe_allow_html=True)

cols[4].markdown("<div style='text-align: center; height: 75px; '>"
                "<h4 style='margin-bottom: 0;'>Parts Hold</h4>"
                "</div>"
                "<div style='text-align: center; padding-top: 10px;'>"
                f"<h4>{parts_hold}</h4>"
                "</div>", unsafe_allow_html=True)

cols[5].markdown("<div style='text-align: center; height: 75px; '>"
                "<h4 style='margin-bottom: 0;'>Hold Other</h4>"
                "</div>"
                "<div style='text-align: center; padding-top: 10px;'>"
                f"<h4>{hold_other}</h4>"
                "</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("---")
    # st.markdown("<h2 style='text-align: center;'>Line Chart</h2>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

col1,col2 = st.columns(2)
filtered_q2_df['DATE'] = pd.to_datetime(filtered_q2_df['DATE'])
latest_dates = filtered_q2_df['DATE'].nlargest(7).unique()
# print(latest_dates)
filtered_data = filtered_q2_df[(filtered_q2_df['BranchName'].isin(selected_branches)) & (filtered_q2_df['DATE'].isin(latest_dates))]
grouped_data = filtered_data.groupby(['DATE', 'BranchName']).size().reset_index(name='Count')
fig = px.scatter(grouped_data, x='DATE', y='Count', color='BranchName', title='DailyTLC by Branch', 
                labels={'DATE': 'DATE', 'Count': 'Count'})

fig.update_xaxes(dtick='MTWTF', tickformat='%m-%d-%Y')
fig.update_layout(width=350)

# charttable

filtered_data = filtered_q2_df[(filtered_q2_df['BranchName'].isin(selected_branches)) & (filtered_q2_df['DATE'].isin(latest_dates))]
grouped_data = filtered_data.groupby(['BranchName', 'DATE']).size().reset_index(name='Count')
pivot_table = pd.pivot_table(grouped_data, values='Count', index='DATE', columns='BranchName', fill_value=0)
latest_dates = grouped_data['DATE'].nlargest(7).unique()

new_columns = []
for branch in selected_branches:
    new_columns.append((branch, 'New Call Count'))
    new_columns.append((branch, 'Open Tickets'))
pivot_table = pivot_table.reindex(columns=new_columns).fillna(0)


with col1:
    st.plotly_chart(fig)

with col2:
    if pivot_table.empty:
        st.write("No data available.")
    else:
        pivot_table = pivot_table.loc[latest_dates]
        pivot_table.columns = pd.MultiIndex.from_tuples(pivot_table.columns)
        st.table(pivot_table)


st.write("Oldest Service Calls:")
st.dataframe(oldest_service_calls)

# if(st.session_state.login):
    
# else:
#     st.title("GeoTab API Credentials")
#     st.session_state.username = st.text_input("Username")
#     st.session_state.password = st.text_input("Password", type="password")
#     st.session_state.database = st.text_input("Database")

#     with open('authauth.json', 'r') as f:
#         api_key = json.load(f)
#     st.session_state.username = api_key["username"]
#     st.session_state.password = api_key["password"]
#     st.session_state.database = api_key["database"]

    # if st.button("Submit") or st.session_state.login:
    #     api = mygeotab.API(username=st.session_state.username, password=st.session_state.password, database=st.session_state.database)
    #     try:
    #         api.authenticate()
    #     except mygeotab.AuthenticationException as ex:
    #         st.error("Credentials incorrect")
    #     else:
    #         # after login container is cleaned
    #         st.success("Credentials correct!")
    #         st.session_state.login = True
    #         from_date = datetime(2023,1,1)
    #         to_date = date.today()
    #         results_limit = ""


            # st.empty() 
            # st.experimental_rerun()
