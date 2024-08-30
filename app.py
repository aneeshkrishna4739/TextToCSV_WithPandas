from dotenv import load_dotenv
load_dotenv() ##laod all environment variables

import streamlit as st
import os
import sqlite3

import google.generativeai as genai

##Configure our API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

file_path = 'Attribute Details.txt'

# Use 'with' to open the file and read its content
with open(file_path, 'r') as file:
    attribute_details = file.read()

prompt_csv = [f"""
Context:
Assume the role of an expert data analyst specializing in cricket statistics. Our product generates Python code using Pandas based on "text prompts" input by users. These prompts often involve requests for data filtering, aggregation, or other data manipulation tasks using a cricket match dataset stored in a CSV file.

Your task is to convert these natural language prompts into accurate and efficient Python Pandas code. The dataset for each task will be provided, and you must ensure that the generated code correctly reflects the user's intent.

Instructions for Analysis:
- Convert the natural language prompt into valid Python Pandas code.
- The code should be concise, correct, and directly executable on the provided dataset.
- Avoid including unnecessary text or comments in the output code.
- Enclose each condition with (), especially when handling multiple conditions.
- Ensure that the code correctly handles the dataset's structure and column types.

The Dataset looks like this:

p_match	inns	bat	p_bat	team_bat	bowl	p_bowl	team_bowl	ball	score	out	over	noball	wide	max_balls	date	year	ground	country	winner	toss	competition	bat_hand	bowl_style	bowl_kind	batruns	ballfaced	bowlruns	pitchLine	pitchLength	shotType
1001349	1	Aaron Finch	5334	Australia	Lasith Malinga	49758	Sri Lanka	1	0	FALSE	1	0	0	120	2/17/2017	2017	Melbourne Cricket Ground	Australia	Sri Lanka	Sri Lanka	T20I	RHB	RF	pace bowler	0	1	0	ON_THE_STUMPS	SHORT_OF_A_GOOD_LENGTH	DEFENDED
1001349	1	Aaron Finch	5334	Australia	Lasith Malinga	49758	Sri Lanka	2	0	FALSE	1	0	0	120	2/17/2017	2017	Melbourne Cricket Ground	Australia	Sri Lanka	Sri Lanka	T20I	RHB	RF	pace bowler	0	1	0	ON_THE_STUMPS	GOOD_LENGTH	DEFENDED
1001349	1	Aaron Finch	5334	Australia	Lasith Malinga	49758	Sri Lanka	3	1	FALSE	1	0	0	120	2/17/2017	2017	Melbourne Cricket Ground	Australia	Sri Lanka	Sri Lanka	T20I	RHB	RF	pace bowler	1	1	1	ON_THE_STUMPS	SHORT_OF_A_GOOD_LENGTH	DEFENDED
1001349	1	Michael Klinger	6161	Australia	Lasith Malinga	49758	Sri Lanka	4	2	FALSE	1	0	0	120	2/17/2017	2017	Melbourne Cricket Ground	Australia	Sri Lanka	Sri Lanka	T20I	RHB	RF	pace bowler	2	1	2	ON_THE_STUMPS	GOOD_LENGTH	FLICK
1001349	1	Michael Klinger	6161	Australia	Lasith Malinga	49758	Sri Lanka	5	0	FALSE	1	0	0	120	2/17/2017	2017	Melbourne Cricket Ground	Australia	Sri Lanka	Sri Lanka	T20I	RHB	RF	pace bowler	0	1	0	OUTSIDE_OFFSTUMP	SHORT_OF_A_GOOD_LENGTH	DEFENDED
1001349	1	Michael Klinger	6161	Australia	Lasith Malinga	49758	Sri Lanka	6	3	FALSE	1	0	0	120	2/17/2017	2017	Melbourne Cricket Ground	Australia	Sri Lanka	Sri Lanka	T20I	RHB	RF	pace bowler	3	1	3	OUTSIDE_OFFSTUMP	GOOD_LENGTH	SQUARE_DRIVE

              
Metadata: csv has the following columns - 
    {attribute_details}


- Prompt 1: "Calculate Virat Kohli's batting performance, including total runs, boundaries, dot balls, and average."

Chain of Thought:
1. Group the DataFrame by player and bat to calculate unique matches, total runs, and balls faced.
2. Calculate the strike rate based on the total runs and balls faced.
3. Count the number of dismissals for the player.
4. Identify and summarize the boundary shots (4s and 6s).
5. Count the number of dot balls faced by the player.
6. Merge all the calculated data into a single DataFrame.
7. Calculate additional metrics such as dot percentage, boundary percentage, and batting average.
8. Filter the final DataFrame to show only the records for 'Virat Kohli'.

Generated Code:
# Grouping the DataFrame by player and bat to calculate unique matches, total runs, and balls faced
total_runs = df.groupby(['p_bat', 'bat']).agg({{'p_match': 'nunique', 'batruns': 'sum', 'ballfaced': 'sum'}}).reset_index()

# Calculating the strike rate and rounding it to two decimal places
total_runs['strike rate'] = (total_runs['batruns'] * 100 / total_runs['ballfaced']).round(2)

# Renaming the 'p_match' column to 'matches'
total_runs.rename(columns={{'p_match': 'matches'}}, inplace=True)

# Counting dismissals
total_outs = df[df['out'] == True].groupby(['p_bat', 'bat']).size().reset_index(name='dismissals')

# Filtering the DataFrame for boundary shots (4s and 6s) with only one ball faced
df1 = df[(df['batruns'].isin([4, 6])) & (df['ballfaced'] == 1)].copy()

# Creating new columns for counting 4s and 6s
df1['4s'] = df1['batruns'].apply(lambda x: 1 if x == 4 else 0)
df1['6s'] = df1['batruns'].apply(lambda x: 1 if x == 6 else 0)

# Grouping the DataFrame to calculate boundary runs and the number of 4s and 6s
total_boundaries = df1.groupby(['p_bat', 'bat']).agg({{'batruns': 'sum', 'ballfaced': 'count', '4s': 'sum', '6s': 'sum'}}).reset_index()

# Renaming columns to better reflect the calculated values
total_boundaries.rename(columns={{'batruns': 'boundary_runs', 'ballfaced': 'boundary_balls'}}, inplace=True)

# Counting the number of dot balls
total_dots = df[(df['batruns'] == 0) & (df['ballfaced'] == 1)].groupby(['p_bat', 'bat']).agg({{'ballfaced': 'sum'}}).reset_index()

# Renaming the 'ballfaced' column to 'dots'
total_dots.rename(columns={{'ballfaced': 'dots'}}, inplace=True)

# Merging the runs, outs, boundaries, and dots dataframes
merged_df = total_runs.merge(total_outs, on=['p_bat', 'bat']).merge(total_boundaries, on=['p_bat', 'bat']).merge(total_dots, on=['p_bat', 'bat'])

# Calculating dot percentage, boundary percentage, and batting average, then rounding to two decimal places
merged_df['dot%'] = (merged_df['dots'] * 100 / merged_df['ballfaced']).round(2)
merged_df['boundary%'] = (merged_df['boundary_runs'] * 100 / merged_df['batruns']).round(2)
merged_df['average'] = (merged_df['batruns'] / merged_df['dismissals']).round(2)

# Filtering the merged DataFrame to show only records for 'Virat Kohli'
result = merged_df[merged_df['bat'] == 'Virat Kohli']

Remove all the comments when fetching the generated code
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
    
    # Local variables for exec
    local_vars = {'df': df, 'plt': plt}
    
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
    df=pd.read_csv("cleaned_data.csv")
    print("data loaded")
    return df
st.header("Gemini App to Retrieve CSV Data")

df = load_data()

question = st.text_input("Input:", key="input")
submit = st.button("Ask the question")

# If the submit button is clicked
if submit:
    response = get_gemini_response_csv(question, prompt_csv)
    st.write(f"Generated Code:\n{response}")
    
    # Execute the generated code and store the result
    result = execute_pandas_code(response, "cleaned_data.csv")
    # Render the result based on its type
    if isinstance(result, Figure):
        st.subheader("The plot is given below:")
        st.pyplot(result)
    else:
        st.subheader("The response is:")
        st.write(result)
