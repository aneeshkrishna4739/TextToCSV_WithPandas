import sqlite3
import csv
import json

# Define the context for the prompts
prompt_csv = """
Context:
Assume the role of an expert data analyst specializing in cricket statistics. Our product generates Python code using Pandas based on "text prompts" input by users. These prompts often involve requests for data filtering, aggregation, or other data manipulation tasks using cricket data stored in DataFrames.

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
                bat_hand                object
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
                bowl_kind               object
                runs_conceded            int64
                ball_bowled              int64
                matches played           int64
                bowling_style           object
                economy                float64
                dismissals               int64
                bowling_average        float64
                bowling_strike_rate    float64
    df3.dtypes:
                player_id                int64
                batsman                 object
                bat_hand                object
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
                bowl_kind               object
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

- Prompt 1: "top 5 batting average against Offspinners among batsmen who played more than 50 matches."

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
                  
Return only generated code. Always store the output in variable 'result'.Ensure you do not add any extra quotes on the code.
"""


# Connect to the SQLite database
def extract_feedback_data(db_path='feedback.db'):
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute('SELECT prompt, generated_code, feedback FROM feedback')
        feedback_data = cursor.fetchall()
    finally:
        conn.close()
    return feedback_data

# Convert the feedback data to CSV format
def create_csv_for_finetuning(feedback_data, output_file='train.csv'):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['prompt', 'completion']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        
        for prompt, generated_code, feedback in feedback_data:
            generated_code = generated_code.replace("```python", "").replace("```", "")
            if feedback == 1:
                # Correctly concatenate the prompt with context
                full_prompt = prompt
                writer.writerow({
                    'prompt': full_prompt,
                    'completion': generated_code
                })

def csv_to_json(csv_file, json_file):
    # Open the CSV file for reading
    with open(csv_file, mode='r', newline='') as file:
        # Read CSV file into a list of dictionaries
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]
    
    # Write the data into a JSON file
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

# Extract data from the database
feedback_data = extract_feedback_data()

# Create CSV file for fine-tuning
#create_csv_for_finetuning(feedback_data)

# Convert the feedback CSV data into JSON format
csv_to_json("train.csv", "train.json")
