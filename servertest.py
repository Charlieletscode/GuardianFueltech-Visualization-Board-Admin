import pyodbc
import pandas as pd
import requests
import os

def fetch_dataToLocal():
    server = "GFTUE2PDGPSQL01"
    database = "GFT"
    username = os.environ.get("username")
    password = os.environ.get("password")
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
    # 
    with open("q1_data.json", 'w') as file:
        file.write(q1_df.to_json(orient='records'))

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
    with open("q2_data.json", 'w') as file:
        file.write(q2_df.to_json(orient='records'))

    query3 = """
    Exec [CF_Streamlit_Daily_TLC]
    """

    cursor.execute(query3)
    q3 = cursor.fetchall()
    rows = []
    for row in q3:
        rows.append(list(row)) 
    q3_df = pd.DataFrame(rows, columns=[
        'Branch_Abv', 'BranchName', 'InsertDate', 'Daily_TLC', 'CompleteBranch', 'CompleteBilling', 'OpenTickets',
        'NewCallCount', 'Region'
    ])
    with open("q3_data.json", 'w') as file:
        file.write(q3_df.to_json(orient='records'))

    cursor.close()
    conn.close()

    # check server operating
    # st.write(q1_df)
    # st.write(q2_df)
    # st.write(q3_df)

fetch_dataToLocal()

def fetch_data():
    server = "GFTUE2PDGPSQL01"
    database = "GFT"
    username = os.environ.get("username")
    password = os.environ.get("password")
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

fetch_data()
