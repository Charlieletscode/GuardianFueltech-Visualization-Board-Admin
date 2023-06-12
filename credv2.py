import streamlit as st
from datetime import *
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os
import requests
import pyodbc
from PIL import Image

def fetch_data():
    server = "GFTUE2PDGPSQL01"
    database = "GFT"
    username = os.environ.get("usernameGFT")
    password = os.environ.get("passwordGFT")
    conn_str = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
    conn = pyodbc.connect(conn_str)

    cursor = conn.cursor()

    query1 = """
    Exec [CF_Streamlit_Tickets]
    """

    cursor.execute(query1)
    q1 = cursor.fetchall()
    rows = []
    for row in q1:
        rows.append(list(row)) 
    q1_df = pd.DataFrame(rows, columns=[
        'Service_Call_ID', 'WS_Job_Number', 'Type_of_Problem', 'Technician', 'Technician_Team', 'Priority_of_Call',
        'Status_of_Call', 'CUSTNMBR', 'CUSTNAME', 'LOCATNNM', 'ADDRESS1', 'CITY', 'STATE', 'ZIP', 'Batch_Number',
        'Service_Description', 'Purchase_Order', 'Divisions', 'BranchName', 'GFT_Work_Flow_Status', 'Gilbarco_ID',
        'Payment_Terms', 'User_Define_4a', 'Type_of_Call', 'Call_Invoice_Number', 'ADRSCODE', 'Service_Area',
        'Completion_Date', 'Last_Service_Note', 'Last_Appointment_Status', 'Row_ID', 'Region'
    ])

    query2 = """
    Exec [CF_Streamlit_30day_His]
    """

    cursor.execute(query2)
    q2 = cursor.fetchall()
    rows = []
    for row in q2:
        rows.append(list(row)) 
    q2_df = pd.DataFrame(rows, columns=[
        'Service_Call_ID', 'ADRSCODE', 'CUSTNMBR', 'Technician_Team', 'Service_Area', 'CUSTNAME', 'LOCATNNM', 'Technician',
        'Type_of_Problem', 'Resolution_ID', 'Resolution_Description', 'Type_Call_Short', 'Type_of_Call', 'DATE1',
        'Divisions', 'BranchName', 'WS_Job_Number', 'TransferToWSJob', 'Bill_Customer_Number', 'Region'
    ])

    query3 = """
    Exec [CF_Streamlit_Daily_TLC]
    """

    cursor.execute(query3)
    q3 = cursor.fetchall()
    rows = []
    for row in q3:
        rows.append(list(row)) 
    q3_df = pd.DataFrame(rows, columns=['Branch_Abv', 'BranchName', 'InsertDate', 'Daily_TLC', 'CompleteBranch', 'CompleteBilling', 'OpenTickets', 'NewCallCount', 'Region'])

    cursor.close()
    conn.close()
    header_image_url = "https://github.com/Charlieletscode/GuardianFueltech-Visualization-Board-Admin/blob/main/Header.jpg?raw=true"
    response = requests.get(header_image_url)

    return q1_df, q2_df, q3_df, response

st.set_page_config("Visualization Board Admin", layout="wide")

if "q1" not in st.session_state:
    st.session_state.q1 = None
if "q2" not in st.session_state:
    st.session_state.q2 = None
if "q3" not in st.session_state:
    st.session_state.q3 = None
if "img" not in st.session_state:
    st.session_state.img = None

# if(st.session_state.q1 is None or st.session_state.q1.empty):
#     st.session_state.q1, st.session_state.q2, st.session_state.q3, st.session_state.img = fetch_data()


username = os.environ.get("usernameGFT")
st.write(username)
header_text = "Visualization Board Admin"

col1, col2 = st.columns([5, 2])
col1.title(header_text)

image = Image.open(io.BytesIO(st.session_state.img.content))
col2.image(image, use_column_width=True)

st.sidebar.subheader("Region")
region = sorted(st.session_state.q1['Region'].unique())
all_option = "All"
unique_region = [all_option] + list(region)
selected_region = st.sidebar.multiselect("Select Unique Region", unique_region, default=[all_option])

if all_option in selected_region:
    selected_region = unique_region[1:]

filtered_q1_df = st.session_state.q1[st.session_state.q1['Region'].isin(selected_region)]
st.sidebar.subheader("BranchName")
branch_names = sorted(filtered_q1_df['BranchName'].unique())
all_option = "All"
unique_branch_names = [all_option] + list(branch_names)
selected_branches = st.sidebar.multiselect("Select Branches", unique_branch_names, default=[all_option])

if all_option in selected_branches:
    selected_branches = unique_branch_names[1:]

filtered_q1_df = st.session_state.q1[st.session_state.q1['BranchName'].isin(selected_branches)]
filtered_q2_df = st.session_state.q2[st.session_state.q2['BranchName'].isin(selected_branches)]
filtered_q3_df = st.session_state.q3[st.session_state.q3['BranchName'].isin(selected_branches)]

last_30_days = pd.to_datetime('today') - pd.DateOffset(days=30)
filtered_df = filtered_q2_df[pd.to_datetime(filtered_q2_df['DATE1']) >= last_30_days]
top_10_customers = filtered_df['CUSTNMBR'].value_counts().nlargest(10)
top_10_df = pd.DataFrame({'CUSTNMBR': top_10_customers.index, 'Service_Call_Count': top_10_customers.values})
fig = go.Figure(data=go.Scatter(x=top_10_df['CUSTNMBR'], y=top_10_df['Service_Call_Count'], mode='lines+markers'))

for index, row in top_10_df.iterrows():
    fig.add_annotation(
        x=row['CUSTNMBR'],
        y=row['Service_Call_Count'],
        text=str(row['Service_Call_Count']),
        showarrow=False,
        font=dict(size=20),
        xshift=0,
        yshift=15
    )

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

filtered_q2_df['DATE1'] = pd.to_datetime(filtered_q2_df['DATE1'])
latest_dates = pd.Series(filtered_q2_df['DATE1'].unique()).nlargest(7).tolist()
filtered_data = filtered_q2_df[(filtered_q2_df['DATE1'].isin(latest_dates))]
grouped_data = filtered_data.groupby(['DATE1', 'BranchName']).size().reset_index(name='Count')
fig = px.scatter(grouped_data, x='DATE1', y='Count', color='BranchName', title='DailyTLC by Branch', 
                labels={'DATE1': 'DATE1', 'Count': 'Count'})

fig.add_shape(
    type='line',
    xref='paper',
    x0=0,
    x1=1,
    y0=10,
    y1=10,
    line=dict(color='royalblue', width=2)
)

for _, row in grouped_data.iterrows():
    fig.add_annotation(
        x=row['DATE1'],
        y=row['Count'],
        text=str(row['Count']),
        showarrow=False,
        font=dict(size=12),
        xshift=15,
        yshift=-1
    )

fig.update_xaxes(dtick='MTWTF', tickformat='%m-%d-%Y')

fig.update_layout(
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        title='',
    ),
    xaxis_title=None,
    yaxis_title=None,    
    title=dict(
        y=1 
    )
)

st.plotly_chart(fig, use_container_width=True)

# piv table
filtered_q3_df['InsertDate'] = pd.to_datetime(filtered_q3_df['InsertDate'])
latest_dates = pd.Series(filtered_q3_df['InsertDate'].unique()).nlargest(7).tolist()
filtered_data = filtered_q3_df[filtered_q3_df['InsertDate'].isin(latest_dates)]
pivot_table = pd.pivot_table(filtered_data, values=['NewCallCount', 'OpenTickets', 'CompleteBranch', 'CompleteBilling'],
                             index='InsertDate', columns='BranchName', fill_value=0)
st.table(pivot_table)


# last graph
filtered_q1_df['Completion_Date'] = pd.to_datetime(filtered_q1_df['Completion_Date'])
oldest_date = pd.Series(filtered_q1_df['Completion_Date'].unique()).nsmallest(10).tolist()
filtered_data = filtered_q1_df[(filtered_q1_df['Completion_Date'].isin(oldest_date))]
oldest_service_calls = filtered_data.sort_values(by='Completion_Date')
oldest_dates = oldest_service_calls['Completion_Date'].tolist()

st.write("Oldest Service Calls:")
st.dataframe(oldest_service_calls)
    
