import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from b2sdk.v1 import *
import socket
import pandas as pd


def is_connected():
    try:
        # Attempt to resolve a DNS hostname
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False


# Download database
# Replace with your Backblaze B2 credentials
application_key_id = 'fc58c8a67d36'
application_key = '005e83fe4dfcc9c78e7c429652b67e23806fa30047'

# Replace with your local path where you want to save the downloaded file
local_save_path = 'Cloud_data_base.db'

# Authenticate with Backblaze B2
info = InMemoryAccountInfo()
b2_api = B2Api(info)

if is_connected():
    try:
        b2_api.authorize_account("production", application_key_id, application_key)
        print("Successfully authenticated with Backblaze B2.")
    except Exception as e:
        print(f"Failed to authenticate: {e}")
else:
    print("Not Connected", "You are not connected to the internet. Cannot fetch data.")

# Bucket name and file name to download
bucket_name = 'sqlite3-data'
file_name = 'Database_2.db'  # Replace with the file you want to download


# Your code for downloading from Backblaze B2
bucket = b2_api.get_bucket_by_name(bucket_name)
download_dest = DownloadDestLocalFile(local_save_path)
bucket.download_file_by_name(file_name, download_dest)
print("Downloaded database")


app = Flask(__name__)

global formatted_test1, formatted_test2, formatted_midterm, formatted_final


@app.route('/')
def index():
    return render_template('new_index.html')


@app.route('/process', methods=['POST'])
def process():
    global formatted_test1, formatted_test2, formatted_midterm, formatted_final, data_to_render
    data = request.get_json()
    selected_button = data.get('button')
    student_id = data.get('studentID')
    selected_option = data.get('selectedOption')
    selected_date = data.get('selectedDate')  # Retrieve selected date

    # Format class button names
    if selected_button in ['Class 11', 'Class 12']:
        bucket.download_file_by_name(file_name, download_dest)
        print("Downloading latest database")
        selected_button = selected_button.replace(' ', '_')

    # Check if selected_date is empty or not provided
    if selected_date:
        # If date is provided, format it
        try:
            formatted_date = datetime.strptime(selected_date, '%m/%d/%Y').strftime('%Y_%m_%d')
        except ValueError:
            formatted_date = 'Invalid date'  # Handle invalid date format
    else:
        # If date is empty or not provided
        formatted_date = 'Date not provided'

        # Initialize data to be rendered in the HTML
    data_to_render = {
        'button': selected_button,
        'studentID': student_id,
        'selectedOption': selected_option,
        'selectedDate': formatted_date,
        'data': None  # Placeholder for retrieved data
    }

    if selected_option == 'View Attendance':
        conn = sqlite3.connect(local_save_path)
        formatted_attendance = f"attendance_{formatted_date}_{selected_button}"
        df = pd.read_sql_query(f"SELECT * FROM {formatted_attendance} WHERE student_id = ?", conn, params=(student_id,))
        if df.empty:  # Check if the DataFrame is empty
            data_to_render['data'] = '<p>No data found</p>'
        else:
            data_to_render['data'] = df.to_html()
        # print(df)
        # print(formatted_attendance, student_id)
    if selected_option == 'View Test1 Marks':
        conn = sqlite3.connect(local_save_path)
        formatted_test1 = f"Test_1_{selected_button}"
        df = pd.read_sql_query(f"SELECT * FROM {formatted_test1} WHERE student_id = ?", conn, params=(student_id,))
        if df.empty:  # Check if the DataFrame is empty
            data_to_render['data'] = '<p>No data found</p>'
        else:
            data_to_render['data'] = df.to_html()
        # print(df)
        # print(formatted_test1)
    elif selected_option == 'View Test2 Marks':
        conn = sqlite3.connect(local_save_path)
        formatted_test2 = f"Test_2_{selected_button}"
        df = pd.read_sql_query(f"SELECT * FROM {formatted_test2} WHERE student_id = ?", conn, params=(student_id,))
        if df.empty:  # Check if the DataFrame is empty
            data_to_render['data'] = '<p>No data found</p>'
        else:
            data_to_render['data'] = df.to_html()
        # print(df)
        # print(formatted_test2)
    elif selected_option == 'View Midterm Marks':
        conn = sqlite3.connect(local_save_path)
        formatted_midterm = f"Mid_Term_{selected_button}"
        df = pd.read_sql_query(f"SELECT * FROM {formatted_midterm} WHERE student_id = ?", conn, params=(student_id,))
        if df.empty:  # Check if the DataFrame is empty
            data_to_render['data'] = '<p>No data found</p>'
        else:
            data_to_render['data'] = df.to_html()
        # print(df)
        # print(formatted_midterm)
    elif selected_option == 'View Final Exam Marks':
        conn = sqlite3.connect(local_save_path)
        formatted_final = f"Final_Exam_{selected_button}"
        df = pd.read_sql_query(f"SELECT * FROM {formatted_final} WHERE student_id = ?", conn, params=(student_id,))
        if df.empty:  # Check if the DataFrame is empty
            data_to_render['data'] = '<p>No data found</p>'
        else:
            data_to_render['data'] = df.to_html()
        # print(df)
        # print(formatted_final)
        # Render the HTML template and pass the data

    # Print selected options
    # print(f"Button: {selected_button}, Student ID: {student_id}, Selected Option: {selected_option}, Selected Date: {formatted_date}")

    # Render the HTML template and pass the data
    return jsonify(data_to_render)


if __name__ == '__main__':
    app.run(debug=True)

