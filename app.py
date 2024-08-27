from dotenv import load_dotenv
load_dotenv() ##laod all environment variables

import streamlit as st
import os
import sqlite3

import google.generativeai as genai

##Configure our API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load google gemini model and provide sql query as response
def get_gemini_response(question,prompt):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content([prompt[0],question])
    return response.text

# Function to retreive query from sql database
def read_sql_query(sql,db):
    conn=sqlite3.connect(db)
    cur=conn.cursor()
    cur.execute(sql)
    rows=cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows

prompt1=[
    """
    You are an expert in converting English questions to SQL query!
    The SQL database has the name students and has the following columns - 
    first_name, last_name, date_of_birth, email, enrollment_date \n\nFor example,\nExample 1 - How many entries of records are present?, 
    the SQL command will be something like this SELECT COUNT(*) FROM students ;
    \nExample 2 - Tell me all the students born in 2000-01-15?, 
    the SQL command will be something like this SELECT * FROM student 
    where date_of_birth="2000-01-15"; 
    also the sql code should not have ``` in beginning or end and sql word in output

    """
]
prompt = [
    """
    You are an expert in converting English questions to Python Pandas code!
    The dataset is stored in a CSV file named 'students.csv' and has the following columns:
    first_name, last_name, date_of_birth, email, enrollment_date.
    
    For example,
    Example 1 - How many records are present in the dataset?
    The Pandas code will be something like this: df.shape[0]
    
    Example 2 - Show all the students born on 2000-01-15?
    The Pandas code will be something like this: df[df['date_of_birth'] == '2000-01-15']
    
    The code should be a valid Python Pandas code snippet and should not include unnecessary text.
    """
]
# #Streamlit page
# st.set_page_config(page_title="I can retreive any SQL query")
# st.header("Gemini APp to Retreive SQL Data")

# question=st.text_input("Input:", key="input")

# submit=st.button("Ask the question")

# #If the submit is clicked

# if submit:
#     response=get_gemini_response(question,prompt)
#     print(response)
#     data=read_sql_query(response,"student.db")
#     st.subheader("The response is:")
#     for row in data:
#         print(row)
#         st.header(row)


def get_gemini_response_sql(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

import pandas as pd

# Function to execute the generated Pandas code
def execute_pandas_code(code, csv_file):
    df = pd.read_csv(csv_file)
    print(df)
    # Execute the generated code within the context of the local variables
    result = eval(code, {'df': df})
    print(result)
    return result

# Streamlit page
st.set_page_config(page_title="I can retrieve data using Pandas")
st.header("Gemini App to Retrieve CSV Data")

question = st.text_input("Input:", key="input")
submit = st.button("Ask the question")

# If the submit button is clicked
if submit:
    response = get_gemini_response_sql(question, prompt)
    st.write(f"Generated Code:\n{response}")
    data = execute_pandas_code(response, "students.csv")
    st.subheader("The response is:")
    st.write(data)
