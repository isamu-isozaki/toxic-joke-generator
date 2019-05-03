#Thanks Sentdex
import sqlite3
import json
import datetime as datetime
from tqdm import tqdm
import re
import argparse
parser = argparse.ArgumentParser(
	description='Specifying data properties.',
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--joke_length', metavar='N', type=int, default=800, help='Length of joke. -1 to include all jokes')
connection = sqlite3.connect('Jokes.db')
c = connection.cursor()
sql_transaction = []

def fix_encoding(s):#Thanks https://www.reddit.com/r/MachineLearning/comments/bgvzdu/d_jokes_generated_via_gpt2/
  return re.sub('[\xc2-\xf4][\x80-\xbf]+',lambda m: m.group(0).encode('latin1').decode('utf8'),s)

def transaction_bldr(sql):
	global sql_transaction
	sql_transaction.append(sql)
	if len(sql_transaction) > 800:
		c.execute('BEGIN TRANSACTION')
		for s in sql_transaction:
			try:
				c.execute(s)
			except Exception as e:
				pass
		connection.commit()
		sql_transaction = []

def format_data(data):
	data = fix_encoding(data.replace("\r", "\n").replace('\"', "'").replace('"', "'"))
	return data

def create_table():
	c.execute("""CREATE TABLE IF NOT EXISTS jokes(id INTEGER PRIMARY KEY, title TEXT, body TEXT, category TEXT, score REAL)""")
id = 0
if __name__ == "__main__":
    args = parser.parse_args()
    joke_length = args.joke_length if args.joke_length != -1 else 10**7
    #assume the max joke lenght cannot exceed 10**7 characters

	create_table()
	row_counter = 0

	with open("./reddit_jokes.json") as f:
		jokes = json.load(f)
		for joke in tqdm(jokes):
			body = format_data(joke["body"])
			title = format_data(joke["title"])
			score = float(joke["score"])
			if score >= 1. and len(body) > 0 and len(title) > 0 and len(body) < joke_length:
				text = fix_encoding(title + "...." + body + "\n\n")
				try:
					with open("jokes.txt", "a+") as f:
						f.write(text)
					sql = """INSERT INTO jokes (id, title, body, score) VALUES ({}, "{}", "{}", {})""".format(id, title, body, score)
					transaction_bldr(sql)
					id += 1
				except:
					pass


	with open("./wocka.json") as f:
		jokes = json.load(f)

		for joke in tqdm(jokes):
            print(joke)
			body = format_data(joke["body"])
			category = format_data(joke["category"])
			title = format_data(joke["title"])
			if len(body) > 0 and len(title) > 0 and len(body) < joke_length:
				text = fix_encoding(title + "...." + body + "\n\n")

				try:
					with open("jokes.txt", "a+") as f:
						f.write(text)
					sql = """INSERT INTO jokes (id, category, body, title) VALUES ({}, "{}", "{}", "{}")""".format(id, category, body, title)
					transaction_bldr(sql)
					id += 1
				except:
					pass

	with open("./stupidstuff.json") as f:
		jokes = json.load(f)
		for joke in tqdm(jokes):
			body = format_data(joke["body"])
			category = format_data(joke["category"])
			score = float(joke["rating"])
			if score >= 1. and len(body) > 0 and len(title) > 0 and len(body) < joke_length:
				text = fix_encoding(body + "\n\n")
				try:
					with open("jokes.txt", "a+") as f:
						f.write(text)
					sql = """INSERT INTO jokes (id, category, body, score) VALUES ({}, "{}", "{}", {})""".format(id, category, body, score)
					transaction_bldr(sql)
					id += 1
				except:
					pass
import pandas as pd
data = pd.read_csv("shortjokes.csv")
indices = data.shape[0]
for i in tqdm(range(indices)):
	body = data.iloc[i]["Joke"]
    if len(body) > 0 and len(body) < joke_length:
    	text = fix_encoding(body + "\n\n")
    	try:
    		with open("jokes.txt", "a+") as f:
    			f.write(text)
    		sql = """INSERT INTO jokes (id, body) VALUES ({}, "{}")""".format(id, body)
    		transaction_bldr(sql)
    		id += 1
    	except:
    		pass
