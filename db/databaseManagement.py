# DB Management
import sqlite3
try:
    conn = sqlite3.connect('data.db', check_same_thread=False)
except:
    conn = sqlite3.connect('data/users.db', check_same_thread=False)
    
c = conn.cursor()

# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY,password TEXT,status TEXT)')
	conn.commit()

def add_userdata(username,password,status):
	c.execute('REPLACE INTO userstable (username,password,status) VALUES (?,?,?)',(username,password,status))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

def view_all_tables():
	c.execute('SELECT name FROM sqlite_master WHERE type="table"')
	data = c.fetchall()
	return data

def delete_user(username):
	try:
		c.execute('DELETE FROM userstable WHERE username = ?',(username,))
		conn.commit()
	except:
		print('Error')
