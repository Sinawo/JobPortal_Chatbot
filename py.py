import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('example.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table to store user information
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, name TEXT, username TEXT)''')

# Insert some data into the table
cursor.execute("INSERT INTO users (name, username) VALUES (?, ?)", ('John Doe', 'johndoe'))
cursor.execute("INSERT INTO users (name, username) VALUES (?, ?)", ('Jane Smith', 'janesmith'))

# Commit the changes
conn.commit()

# Retrieve data from the table
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# Print the retrieved data
for row in rows:
    print(row)

# Close the cursor and connection
cursor.close()
conn.close()