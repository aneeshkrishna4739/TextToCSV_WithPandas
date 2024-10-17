from dotenv import load_dotenv
import os
import streamlit as st
#import sqlite3
from google.cloud import firestore
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.figure import Figure
import base64
import json
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

# Configure our API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Load Streamlit secrets
credentials_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")

missing_padding = len(credentials_base64) % 4
if missing_padding != 0:
    credentials_base64 += '=' * (4 - missing_padding)

# Decode and load the credentials
credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
credentials_info = json.loads(credentials_json)

print(credentials_info)

# Use the credentials to initialize Firestore
credentials = service_account.Credentials.from_service_account_info(credentials_info)
db = firestore.Client(credentials=credentials)

firestore_collection=os.getenv("FIRESTORE_COLLECTION")

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
                df1=pd.read_excel("batters_against_bowlingtype.csv")
                df2=pd.read_excel("Bowling_against_left_right_handers.csv")
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
                bat_hand                object
                bowling_style           object
                matches_played           int64
                runs_scored              int64
                balls_faced              int64
                batting_strike_rate    float64
                dismissals               int64
                batting_average        float64
                Country                 object
    df2.dtypes:
                player_id                int64
                bowler                  object
                bat_hand                object
                bowl_kind               object
                runs_conceded            int64
                ball_bowled              int64
                matches_played           int64
                bowling_style           object
                economy                float64
                dismissals               int64
                bowling_average        float64
                bowling_strike_rate    float64
                Country                 object
    df3.dtypes:
                player_id                int64
                batsman                 object
                bat_hand                object
                matches_played           int64
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
                Country                 object
    df4.dtypes:
                player_id                int64
                bowler                  object
                bowl_kind               object
                runs_conceded            int64
                ball_bowled              int64
                matches_played           int64
                bowling_style           object
                economy                float64
                dismissals               int64
                dotballs                 int64
                dotballs_percent       float64
                bowling_average        float64
                bowling_strike_rate    float64
                Country                 object
               
    Columns 'bowling_style' has values :'Left Off Spin', 'Right Medium', 'Right Fast', 'Left Medium',
       'Right Wrist Spin', 'Left Fast', 'Right Off Spin',
       'Left Wrist Spin', 'Mixed'.
    Columns 'bat_hand' has values :'RHB', 'LHB'.
                'RHB' stands for Right Hand Batsman
                'LHB' stands for Left Hand Batsman
    Columns 'bat_hand' has values :'RHB', 'LHB'.
                'RHB' stands for Right Hand Batsman
                'LHB' stands for Left Hand Batsman
    Columns 'bowl_kind' has values :'spin bowler', 'pace bowler'.

- Prompt 1: "top 5 batting average against right arm Offspinners among batsmen who played more than 50 matches."

    Generated Code:
    result=df1[(df1['matches_played']>50) & (df1['bowling_style']=='Right Off Spin')].sort_values(by='batting_average',ascending=False).head(5)

- Prompt 2: "5 Lowest economy among bowlers against Right handed batsmen who played more than 75 matches"

    Generated Code:
    result=df2[(df2['matches_played']>75) & (df2['bat_hand']=='RHB')].sort_values(by='economy',ascending=True).head(5)
              
- Prompt 3: "bar plot of Top 10 batting strike rate who faced more than 1000 balls"

    Generated Code:
    result=df3[(df3['balls_faced']>1000)].sort_values(by='batting_strike_rate',ascending=False).head(10).plot(kind='bar',x='batsman',y='batting_strike_rate')

- Prompt 4: "5 right arm fast Bowlers with lowest bowling average who bowled more than 2000 balls"

    Generated Code:
    result=df4[(df4['ball_bowled']>2000) & (df4['bowling_style']=='Right Fast')].sort_values(by='bowling_average',ascending=True).head(5)    

- Prompt 5: "bar plot 5 pace bowlers bowled 1000+ balls  with lowest bowling average"

    Generated Code:
    result=df4[(df4['ball_bowled']>1000) & (df4['bowl_kind']=='pace bowler')].sort_values(by='bowling_average',ascending=True).head(5).plot(kind='bar',x='bowler',y='bowling_average')

- Prompt 6: "pie chart for all bowling types"

    Generated Code:
    result=df1['bowling_style'].value_counts().plot(kind='pie',title='Distribution of bowling types')

- Prompt 7: "highest 10 run scorers, bar plot, color bars for players with different countries, add legends to respective countries"

    Generated Code:
    top_10 = df3[['batsman', 'runs_scored', 'Country']].sort_values(by='runs_scored', ascending=False).head(10)\nunique_countries = top_10['Country'].unique()\ncolor_map = {country: color for country, color in zip(unique_countries, plt.get_cmap('tab10').colors)}\ncolors = top_10['Country'].map(color_map)\ntop_10.plot(kind='bar', x='batsman', y='runs_scored', color=colors, legend=False)\nhandles = [plt.Rectangle((0, 0), 1, 1, color=color_map[country]) for country in unique_countries]\nplt.legend(handles, unique_countries, title='Country')\nplt.xlabel('Batsman')\nplt.ylabel('Runs Scored')\nplt.title('Top 10 Highest Run Scorers')\nresult=plt.show()
                              
Return only plain code. Always store the output in variable 'result'.
"""
]

# Define functions
def get_gemini_response_csv(question, prompt):
    #model = genai.GenerativeModel('gemini-pro')
    model = genai.GenerativeModel('tunedModels/generate-num-1897')
    generation_config = genai.GenerationConfig(
        temperature=0.6,
        top_p=1.0,
        top_k=32,
        candidate_count=1,
    )
    print("model:",model)
    response = model.generate_content([prompt[0], question], generation_config=generation_config)
    return response.text

def execute_pandas_code(code):
    code = code.replace("```python", "").replace("```", "")
    local_vars = {'df1': df1, 'df2': df2, 'df3': df3, 'df4': df4, 'pd': pd, 'plt': plt, 'cm':cm}
    try:
        exec(code, {}, local_vars)
        result = local_vars.get('result', next((v for v in (local_vars.get('df1'), local_vars.get('df2'), local_vars.get('df3'), local_vars.get('df4')) if v is not None), None))
    except Exception as e:
        raise e
    figure = plt.gcf() if plt.get_fignums() else None    
    return figure if figure else result

def insert_feedback(prompt, generated_code, feedback):
    #feedback_ref = db.collection('feedback_dev').document()  # Create a new document
    feedback_ref = db.collection('feedback_public').document()  # Create a new document
    feedback_data = {
        'prompt': prompt,
        'generated_code': generated_code,
        'feedback': feedback
    }
    feedback_ref.set(feedback_data)  # Insert the data into Firestore
    st.success("Feedback submitted successfully")

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
st.set_page_config(page_title="Cricket Statistics LLM Chatbot")

@st.cache_data
def load_data():
    df1 = pd.read_csv("data/batters_against_bowlingtype.csv")
    df2 = pd.read_csv("data/Bowling_against_left_right_handers.csv")
    df3 = pd.read_csv("data/batting_stats.csv")
    df4 = pd.read_csv("data/bowling_stats.csv")
    return df1, df2, df3, df4

st.header("Cricket Statistics LLM Chatbot")

df1, df2, df3, df4 = load_data()

# Custom CSS to add a background image
background_image = '''
    <style>
    .stApp {
        background-image: url("data/cricbot-2.png");
        background-size: cover;
    }
    </style>
    '''

# Inject the CSS with the background image
st.markdown(background_image, unsafe_allow_html=True)

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
    
    st.write(f"Generated Code:\n{response}")
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