from dotenv import load_dotenv
import os
import streamlit as st
import sqlite3
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Load environment variables
load_dotenv()

# Configure our API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Read the prompt template from a text file
file_path = 'Attribute Details.txt'
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
              
small description for each of the four dataframes:
    df1: This dataframe captures the performance of batsmen against various types of bowling styles.
    df2: This dataframe focuses on the performance of bowlers against batsmen of different batting hands (left-handed or right-handed).
    df3: This dataframe provides an in-depth overview of a batsman's performance across various matches.
    df4: This dataframe offers a detailed breakdown of a bowler's performance across multiple matches.

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
    result=df2[(df2['matches played']>75) & (df2['bat_hand']=='RHB')].sort_values(by='economy',ascending=True).head(5)
              
- Prompt 3: "5 Batsmen with lowest dot ball percentage who played more than 2000 balls"

    Generated Code:
    result=df3[(df3['balls_faced']>2000)].sort_values(by='dot_percent',ascending=True).head(5)

- Prompt 4: "5 right arm fast Bowlers with lowest bowling average who bowled more than 2000 balls"

    Generated Code:
    result=df4[(df4['ball_bowled']>2000) & (df4['bowling_style']=='RF')].sort_values(by='bowling_average',ascending=True).head(5)    
                  
Return only generated code. Always store the output in variable 'result'.
"""
]


# Define functions
def get_gemini_response_csv(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    generation_config = genai.GenerationConfig(
        temperature=0.6,
        top_p=1.0,
        top_k=32,
        candidate_count=1,
    )
    response = model.generate_content([prompt[0], question], generation_config=generation_config)
    return response.text

def execute_pandas_code(code):
    local_vars = {'df1': df1, 'df2': df2, 'df3': df3, 'df4': df4, 'pd': pd, 'plt': plt}
    try:
        exec(code, {}, local_vars)
        result = local_vars.get('result', next((v for v in (local_vars.get('df1'), local_vars.get('df2'), local_vars.get('df3'), local_vars.get('df4')) if v is not None), None))
    except Exception as e:
        raise e
    figure = plt.gcf() if plt.get_fignums() else None    
    return figure if figure else result

def insert_feedback(prompt, generated_code, feedback):
    conn = sqlite3.connect('feedback.db')
    try:
        with conn:
            conn.execute('''
                INSERT INTO feedback (prompt, generated_code, feedback)
                VALUES (?, ?, ?)
            ''', (prompt, generated_code, feedback))
    finally:
        conn.close()

# Initialize session state
if 'app_state' not in st.session_state:
    st.session_state.app_state = {
        'feedback_submitted': False,
        'response': None,
        'question': None,
        'thumbs_clicked': False
    }

def reset_feedback():
    st.session_state.app_state.update({
        'feedback_submitted': False,
        'response': None,
        'question': None
    })

# Streamlit page configuration
st.set_page_config(page_title="Gemini App to Retrieve CSV Data")

@st.cache_data
def load_data():
    df1 = pd.read_excel("data/batters_against_bowlingtype.xlsx")
    df2 = pd.read_excel("data/Bowling_against_left_right_handers.xlsx")
    df3 = pd.read_csv("data/batting_stats.csv")
    df4 = pd.read_csv("data/bowling_stats.csv")
    return df1, df2, df3, df4

st.header("Gemini App to Retrieve CSV Data")

df1, df2, df3, df4 = load_data()

question = st.text_input("Input:", key="input")
submit = st.button("Ask the question")

# If the submit button is clicked
if submit:
    response = get_gemini_response_csv(question, prompt_csv)
    st.session_state.app_state.update({
        'response': response,
        'question': question,
        'feedback_submitted': False
    })
    st.write(f"Generated Code:\n{response}")
    
    try:
        result = execute_pandas_code(response)
        if isinstance(result, Figure):
            st.subheader("The plot is given below:")
            st.pyplot(result)
        else:
            st.subheader("The response is:")
            st.write(result)
    except Exception as e:
        st.write("An error occurred while executing the code.")
        st.write(f"Error: {e}")
        insert_feedback(question, response, 0)  # Log failure as feedback

# Feedback stage
if st.session_state.app_state['response'] and not st.session_state.app_state['feedback_submitted']:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👍"):
            insert_feedback(st.session_state.app_state['question'], st.session_state.app_state['response'], 1)  # 1 for thumbs up
            st.success("Thank you for your feedback!")
            st.session_state.app_state['feedback_submitted'] = True
    
    with col2:
        if st.button("👎"):
            insert_feedback(st.session_state.app_state['question'], st.session_state.app_state['response'], 0)  # 0 for thumbs down
            st.success("Thank you for your feedback!")
            st.session_state.app_state['feedback_submitted'] = True

# Display a reset button to restart the process
if st.session_state.app_state['feedback_submitted']:
    if st.button("Reset"):
        reset_feedback()
        st.cache_data.clear()  # Clear cache to reset the page