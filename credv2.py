import streamlit as st
from datetime import *
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from PIL import Image
from servertest import fetch_data

st.set_page_config("Visualization Board Admin", layout="wide")

if "q1" not in st.session_state:
    st.session_state.q1 = None
if "q2" not in st.session_state:
    st.session_state.q2 = None
if "q3" not in st.session_state:
    st.session_state.q3 = None
if "img" not in st.session_state:
    st.session_state.img = None

if(st.session_state.q1 is None or st.session_state.q1.empty):
    st.session_state.q1, st.session_state.q2, st.session_state.q3, st.session_state.img = fetch_data()

header_text = "Visualization Board Admin"

col1, col2 = st.columns([5, 2])
col1.title(header_text)

image = Image.open(io.BytesIO(st.session_state.img.content))
col2.image(image, use_column_width=True)

st.sidebar.subheader("BranchName")
branch_names = sorted(st.session_state.q1['BranchName'].unique())
all_option = "All"
unique_branch_names = [all_option] + list(branch_names)
selected_branches = st.sidebar.multiselect("Select Branches", unique_branch_names, default=[all_option])

if all_option in selected_branches:
    selected_branches = unique_branch_names[1:]

filtered_q1_df = st.session_state.q1[st.session_state.q1['BranchName'].isin(selected_branches)]

# unique_service_call_ids = filtered_q1_df['Service_Call_ID'].unique()
# all_option = "All"
# unique_service_call_ids = [all_option] + list(unique_service_call_ids)
# selected_service_call_ids = st.sidebar.multiselect("Select Service Call IDs", unique_service_call_ids, default=[all_option])

# if all_option in selected_service_call_ids:
#     selected_service_call_ids = unique_service_call_ids[1:]

filtered_q2_df = st.session_state.q2
# print(len(filtered_q2_df))
# filtered_q1_df = st.session_state.q1[st.session_state.q1['Service_Call_ID'].isin(selected_service_call_ids)]
# please use filtereddata

last_30_days = pd.to_datetime('today') - pd.DateOffset(days=30)
filtered_df = filtered_q2_df[pd.to_datetime(filtered_q2_df['DATE1']) >= last_30_days]
# print("sec",len(filtered_df))
print((filtered_q2_df['CUSTNMBR'] == 'CIR0001').sum())
# filtered_df = filtered_q2_df[filtered_q2_df['Service_Call_ID'].isin(selected_service_call_ids)]
# print(len(filtered_df))
top_10_customers = filtered_df['CUSTNMBR'].value_counts().nlargest(10)
# print(top_10_customers)
top_10_df = pd.DataFrame({'CUSTNMBR': top_10_customers.index, 'Service_Call_Count': top_10_customers.values})
fig = go.Figure(data=go.Scatter(x=top_10_df['CUSTNMBR'], y=top_10_df['Service_Call_Count'], mode='lines+markers'))

fig.update_layout(
    title='Top 10 Customers by Service Call Count (Last 30 Days)',
    xaxis_title='',
    yaxis_title='',        
)

cols = st.columns(6)
total_service_calls_q1 = filtered_q1_df['Service_Call_ID'].count()
count_ws_job_number_q1 = filtered_q1_df['WS_Job_Number'].nunique()
redispatch_calls = (filtered_q1_df['Last_Appointment_Status'] == 'REDISPATCH ').sum()
quote_needed = (filtered_q1_df['Last_Appointment_Status'] == 'QUOTE ').sum()
parts_hold = (filtered_q1_df['Last_Appointment_Status'] == 'PARTS HOLD ').sum()
hold_other = (filtered_q1_df['Last_Appointment_Status'] == 'HOLD OTHER ').sum()
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
latest_dates = filtered_q2_df['DATE1'].nlargest(7).unique()
print(latest_dates)
filtered_data = filtered_q2_df[(filtered_q2_df['BranchName'].isin(selected_branches)) & (filtered_q2_df['DATE1'].isin(latest_dates))]
grouped_data = filtered_data.groupby(['DATE1', 'BranchName']).size().reset_index(name='Count')
fig = px.scatter(grouped_data, x='DATE1', y='Count', color='BranchName', title='DailyTLC by Branch', 
                labels={'DATE1': 'DATE1', 'Count': 'Count'})

fig.update_xaxes(dtick='MTWTF', tickformat='%m-%d-%Y')
fig.update_layout(width=350)

# charttable

filtered_data = filtered_q2_df[(filtered_q2_df['BranchName'].isin(selected_branches)) & (filtered_q2_df['DATE1'].isin(latest_dates))]
grouped_data = filtered_data.groupby(['BranchName', 'DATE1']).size().reset_index(name='Count')
pivot_table = pd.pivot_table(grouped_data, values='Count', index='DATE1', columns='BranchName', fill_value=0)
latest_dates = grouped_data['DATE1'].nlargest(7).unique()

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


# last graph
oldest_service_calls = filtered_q2_df.sort_values(by='DATE1').tail(10)
oldest_dates = oldest_service_calls['DATE1'].tolist()

st.write("Oldest Service Calls:")
st.dataframe(oldest_service_calls)

# if(login):
    
# else:
#     st.title("GeoTab API Credentials")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#     database = st.text_input("Database")

#     with open('authauth.json', 'r') as f:
#         api_key = json.load(f)
#     username = api_key["username"]
#     password = api_key["password"]
#     database = api_key["database"]

    # if st.button("Submit") or login:
    #     api = mygeotab.API(username=username, password=password, database=database)
    #     try:
    #         api.authenticate()
    #     except mygeotab.AuthenticationException as ex:
    #         st.error("Credentials incorrect")
    #     else:
    #         # after login container is cleaned
    #         st.success("Credentials correct!")
    #         login = True
    #         from_date = datetime(2023,1,1)
    #         to_date = date.today()
    #         results_limit = ""


            # st.empty() 
            # st.experimental_rerun()


    

    
