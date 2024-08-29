from dotenv import load_dotenv
load_dotenv() ##laod all environment variables

import streamlit as st
import os
import sqlite3

import google.generativeai as genai

##Configure our API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load google gemini model and provide sql query as response
# def get_gemini_response_sql(question,prompt):
#     model=genai.GenerativeModel('gemini-pro')
#     response=model.generate_content([prompt[0],question])
#     return response.text

# # Function to retreive query from sql database
# def read_sql_query(sql,db):
#     conn=sqlite3.connect(db)
#     cur=conn.cursor()
#     cur.execute(sql)
#     rows=cur.fetchall()
#     conn.commit()
#     conn.close()
#     for row in rows:
#         print(row)
#     return rows

# prompt_sql=[
#     """
#     You are an expert in converting English questions to SQL query!
#     The SQL database has the name students and has the following columns - 
#     first_name, last_name, date_of_birth, email, enrollment_date \n\nFor example,\nExample 1 - How many entries of records are present?, 
#     the SQL command will be something like this SELECT COUNT(*) FROM students ;
#     \nExample 2 - Tell me all the students born in 2000-01-15?, 
#     the SQL command will be something like this SELECT * FROM student 
#     where date_of_birth="2000-01-15"; 
#     also the sql code should not have ``` in beginning or end and sql word in output

#     """
# ]

# #Streamlit page
# st.set_page_config(page_title="I can retreive any SQL query")
# st.header("Gemini APp to Retreive SQL Data")

# question=st.text_input("Input:", key="input")

# submit=st.button("Ask the question")

# #If the submit is clicked

# if submit:
#     response=get_gemini_response_sql(question,prompt)
#     print(response)
#     data=read_sql_query(response,"student.db")
#     st.subheader("The response is:")
#     for row in data:
#         print(row)
#         st.header(row)

prompt_csv = [
    """
    Context:
Assume the role of an expert data analyst. Our product generates Python code using Pandas based on "text prompts" input by users. These prompts often involve requests for data filtering, aggregation, or other data manipulation tasks using a dataset stored in a CSV file.

Your task is to convert these natural language prompts into accurate and efficient Python Pandas code. The dataset for each task will be provided, and you must ensure that the generated code correctly reflects the user's intent.

Instructions for Analysis:
- Convert the natural language prompt into valid Python Pandas code.
- The code should be concise, correct, and directly executable on the provided dataset.
- Avoid including unnecessary text or comments in the output code.
- Enclose each conditions with (), especially with multiple conditions.

For example:
- Prompt: "John Doe's birthday"
  Output: df1=df[(df['first_name'] == 'John') & (df['last_name'] == 'Doe')]['date_of_birth']

- Prompt: "Show all the students born on 2000-01-15?"
  Output: df1=df[df['date_of_birth'] == '2000-01-15']

Ensure the code handles the dataset's structure correctly, and only provide the Pandas code snippet needed to fulfill the user's request.

Remember, the generated code should be a valid Python Pandas code snippet and should not include any extra explanations or comments.

Metadata: csv has the following columns - 
    first_name, last_name, date_of_birth, email, enrollment_date
    df.dtypes
    student_id                  int64
    first_name                 object
    last_name                  object
    date_of_birth      datetime64[ns]
    email                      object
    enrollment_date    datetime64[ns]
    """
]

def get_gemini_response_csv(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    generation_config = genai.GenerationConfig(stop_sequences = None,
  temperature=0.6,
  top_p=1.0,
  top_k=32,
  candidate_count=1,)
    response = model.generate_content([prompt[0], question], generation_config=generation_config)
    return response.text

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
# Function to execute the generated Pandas code
def execute_pandas_code(code, csv_file):
    # Load and preprocess the DataFrame
    df = pd.read_csv(csv_file)
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    df['enrollment_date'] = pd.to_datetime(df['enrollment_date'])
    
    # Local variables for exec
    local_vars = {'df': df, 'plt': plt}
    
    # Execute the code
    exec(code, {}, local_vars)
    
    # Retrieve the updated DataFrame or result
    result = local_vars.get('df1', local_vars.get('df', None))
    
    # Check if a plot has been created
    figure = plt.gcf() if plt.get_fignums() else None
    
    # Determine what to return based on what was generated
    if figure and plt.get_fignums():
        return figure  # Return the plot
    elif isinstance(result, pd.DataFrame) or isinstance(result, pd.Series):
        return result  # Return the DataFrame or Series
    else:
        return None

# Streamlit page
st.set_page_config(page_title="I can retrieve data using Pandas")
st.header("Gemini App to Retrieve CSV Data")

question = st.text_input("Input:", key="input")
submit = st.button("Ask the question")

# If the submit button is clicked
if submit:
    response = get_gemini_response_csv(question, prompt_csv)
    st.write(f"Generated Code:\n{response}")
    
    # Execute the generated code and store the result
    result = execute_pandas_code(response, "students.csv")
    # Render the result based on its type
    if isinstance(result, Figure):
        st.subheader("The plot is given below:")
        st.pyplot(result)
    else:
        st.subheader("The response is:")
        st.write(result)
