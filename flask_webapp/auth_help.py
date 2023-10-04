import sqlite3 

# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

conn = sqlite3.connect('myapp.db')
c = conn.cursor()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE teacher_name =? AND password = ?',(username,password))
	data = c.fetchall()
	return data