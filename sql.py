import sqlite3

# Create SQLite database and table with boolean feedback
conn = sqlite3.connect('feedback.db')
c = conn.cursor()

# Create a table to store feedback
c.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT,
    generated_code TEXT,
    feedback INTEGER  -- 1 for thumbs up, 0 for thumbs down
)
''')

conn.commit()
conn.close()