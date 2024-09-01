from dotenv import load_dotenv
load_dotenv() ##laod all environment variables

import streamlit as st
import os
import sqlite3

import google.generativeai as genai


import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
##Configure our API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

file_path = 'Attribute Details.txt'

# Use 'with' to open the file and read its content
with open(file_path, 'r') as file:
    attribute_details = file.read()

prompt_csv = ["""
Context:
Assume the role of an expert data analyst specializing in cricket statistics. Our product generates Python code using Pandas based on "text prompts" input by users. These prompts often involve requests for data filtering, aggregation, or other data manipulation tasks using a cricket data stored in a DataFrames.

Your task is to convert these natural language prompts into accurate and efficient Python Pandas code. The dataframes for each task will be provided, and you must ensure that the generated code correctly reflects the user's intent.

Instructions for Analysis:
- Convert the natural language prompt into valid Python Pandas code.
- The code should be concise, correct, and directly executable on the provided dataset.
- Avoid including unnecessary text or comments in the output code.
- Enclose each condition with (), especially when handling multiple conditions.
- Ensure that the code correctly handles the dataset's structure and column types.

Metadata: There are 4 dataframes df1,df2,df3,df4 which extracted data from files in below codes:
                df1=pd.read_excel("batters_against_bowlingtype.xlsx")
                df2=pd.read_excel("Bowling_against_left_right_handers.xlsx")
                df3=pd.read_csv("batting_stats.csv")
                df4=pd.read_csv("bowling_stats.csv")
Column Details in each dataframes:
    df1.dtypes:
                player_id                int64
                batsman                 object
                bowling_style           object
                matches played           int64
                runs_scored              int64
                balls_faced              int64
                batting_strike_rate    float64
                dismissals               int64
                batting_average        float64
    df2.dtypes:
                player_id                int64
                bowler                  object
                bat_hand                object
                runs_conceded            int64
                ball_bowled              int64
                matches played           int64
                bowling_style           object
                economy                float64
                dismissals               int64
                bowling_average        float64
                bowling_strike rate    float64
    df3.dtypes:
                player_id                int64
                batsman                 object
                matches played           int64
                runs_scored              int64
                balls_faced              int64
                batting_strike_rate    float64
                dismissals               int64
                boundary_runs            int64
                boundary_balls           int64
                4s                       int64
                6s                       int64
                dots                     int64
                dot_percent            float64
                boundary_percent       float64
                batting_average        float64
    df4.dtypes:
                player_id                int64
                bowler                  object
                runs_conceded            int64
                ball_bowled              int64
                matches played           int64
                bowling_style           object
                economy                float64
                dismissals               int64
                dotballs                 int64
                dotballs_percent       float64
                bowling_average        float64
                bowling_strike rate    float64
               
    Columns 'bowling_style' has values :'LFM', 'SLA', 'RM', 'LWS', 'OB', 'RWS', 'RF', 'RFM', 'LF', 'LM', 'LSM'.
                'LFM' stands for Left Arm Medium Fast
                'SLA' stands for Left Arm OffSpinner
                'RM'  stands for Right Arm Medium
                'LWS' stands for Left Arm WristSpinner, 
                'OB'  stands for Right Arm OffSpinner
                'RWS' stands for Right Arm WristSpinner
                'RF'  stands for Right Arm Fast
                'RFM' stands for Left Arm Medium Fast
                'LF'  stands for Left Arm Fast
                'LM'  stands for Left Arm Medium
                'LSM' stands for Left Arm Slow Medium
    Columns 'bat_hand' has values :'RHB', 'LHB'.
                'RHB' stands for Right Hand Batsman
                'LHB' stands for Left Hand Batsman

- Prompt 1: "Calculate top 5 batting average against Offspinners among batsmen who played more than 50 matches."

    Generated Code:
    result=df1[(df1['matches played']>50) & (df1['bowling_style']=='OB')].sort_values(by='batting_average',ascending=False).head(5)

- Prompt 2: "5 Lowest economy among bowlers against Right handed batsmen who played more than 75 matches"

    Generated Code:
    df2[(df2['matches played']>75) & (df2['bat_hand']=='RHB')].sort_values(by='economy',ascending=True).head(5)
              
- Prompt 3: "5 Batsmen with lowest dot ball percentage who played more than 2000 balls"

    Generated Code:
    df3[(df3['balls_faced']>2000)].sort_values(by='dot_percent',ascending=True).head(5)

- Prompt 4: "5 right arm fast Bowlers with lowest bowling average who bowled more than 2000 balls"

    Generated Code:
    df4[(df4['ball_bowled']>2000) & (df4['bowling_style']=='RF')].sort_values(by='bowling_average',ascending=True).head(5)    
                  
Return only generated code. Always store the output in variable 'result'.
"""
]


# prompt_csv=["""


# """
# ]
def get_gemini_response_csv(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    generation_config = genai.GenerationConfig(stop_sequences = None,
  temperature=0.6,
  top_p=1.0,
  top_k=32,
  candidate_count=1,)
    response = model.generate_content([prompt[0], question], generation_config=generation_config)
    return response.text

# Function to execute the generated Pandas code

def execute_pandas_code(code):
    
    # Local variables for exec
    local_vars = {'df1': df1,'df2': df2,'df3': df3,'df4': df4, 'pd': pd, 'plt': plt}
    
    # Execute the code
    exec(code, {}, local_vars)
    
    # Retrieve the updated DataFrame or result
    result = local_vars.get('result', local_vars.get('df', None))

    # Check if a plot has been created
    figure = plt.gcf() if plt.get_fignums() else None
    
    # Determine what to return based on what was generated
    if figure and plt.get_fignums():
        return figure  # Return the plot
    else:
        return result

# Streamlit page

st.set_page_config(page_title="I can retrieve data using Pandas")

@st.cache_data
def load_data():
    # This function will be called only once
    df1=pd.read_excel("data/batters_against_bowlingtype.xlsx")
    df2=pd.read_excel("data/Bowling_against_left_right_handers.xlsx")
    df3=pd.read_csv("data/batting_stats.csv")
    df4=pd.read_csv("data/bowling_stats.csv")
    print("data loaded")
    return df1,df2,df3,df4
st.header("Gemini App to Retrieve CSV Data")

df1,df2,df3,df4 = load_data()

question = st.text_input("Input:", key="input")
submit = st.button("Ask the question")

# If the submit button is clicked
if submit:
    response = get_gemini_response_csv(question, prompt_csv)
    st.write(f"Generated Code:\n{response}")
    
    # Execute the generated code and store the result
    result = execute_pandas_code(response)
    # Render the result based on its type
    if isinstance(result, Figure):
        st.subheader("The plot is given below:")
        st.pyplot(result)
    else:
        st.subheader("The response is:")
        st.write(result)
