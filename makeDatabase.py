#Thanks Sentdex
import json
import datetime as datetime
from tqdm import tqdm
import re
import argparse
parser = argparse.ArgumentParser(
	description='Specifying data properties.',
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--joke_length', metavar='len', type=int, default=800, help='Length of joke. -1 to include all jokes')
parser.add_argument('--reddit_rating', metavar='re_rat', type=int, default=2, help='Minimum upvotes for reddit jokes')
parser.add_argument('--stupidstuff_rating', metavar='stu_rat', type=float, default=3.0, help='Minimum stars out of 5 for joke to be included')
parser.add_argument('--include_wocka', metavar='inc_wocka', type=bool, default=False, help='Include wocka.json')

text_file_name = None

def fix_encoding(s):#Thanks https://www.reddit.com/r/MachineLearning/comments/bgvzdu/d_jokes_generated_via_gpt2/
  return re.sub('[\xc2-\xf4][\x80-\xbf]+',lambda m: m.group(0).encode('latin1').decode('utf8'),s)


def format_data(data):
	data = data.replace('\n', " ").replace("\r", " ").replace("\t", " ").replace("    ", " ").replace("  ", " ").rstrip().strip().replace("  ", " ")
	data = data.replace(u"\u201c", '"').replace(u"\u201d", '"').replace(u"\u2019", "'").replace(u"\u2026", "...")
	data = fix_encoding(data)
	return data

id = 0
if __name__ == "__main__":
	args = parser.parse_args()
	joke_length = args.joke_length if args.joke_length != -1 else 10**7
	#assume the max joke lenght cannot exceed 10**7 characters
	text_file_name = f"jokes_{str(joke_length)}_{str(args.reddit_rating)}_{str(args.stupidstuff_rating)}_{str(0 if args.include_wocka else 1)}.txt"
	texts = []

	with open("./reddit_jokes.json") as f:
		jokes = json.load(f)
		for joke in tqdm(jokes):
			body = format_data(joke["body"])
			title = format_data(joke["title"])
			score = float(joke["score"])
			if score >= args.reddit_rating and len(body) > 0 and len(title) > 0 and len(body) < joke_length:
				text = "\n\n"+fix_encoding(title + " " + body + " <|endoftext|>" )
				texts.append(text)


	with open("./wocka.json") as f:
		jokes = json.load(f)
		if args.include_wocka:
			for joke in tqdm(jokes):
				body = format_data(joke["body"])
				category = format_data(joke["category"])
				title = format_data(joke["title"])
				if len(body) > 0 and len(title) > 0 and len(body) < joke_length:
					text = "\n\n"+fix_encoding(title + " " + body + " <|endoftext|>")
					texts.append(text)

	with open("./stupidstuff.json") as f:
		jokes = json.load(f)
		for joke in tqdm(jokes):
			body = format_data(joke["body"])
			category = format_data(joke["category"])
			score = float(joke["rating"])
			if score >= args.stupidstuff_rating and len(body) > 0 and len(title) > 0 and len(body) < joke_length:
				text = "\n\n"+fix_encoding(body + " <|endoftext|>")
				texts.append(text)
	import pandas as pd
	data = pd.read_csv("jokes.csv")
	indices = data.shape[0]
	for i in tqdm(range(indices)):
		body = data.iloc[i]["Joke"]
		if len(body) > 0 and len(body) < joke_length:
			text = "\n\n"+fix_encoding(body + " <|endoftext|>")
			texts.append(text)
	data = pd.read_csv("jokes_score_name_clean.csv")
	indices = data.shape[0]
	for i in tqdm(range(indices)):
		title = data.iloc[i]["q"]
		body = data.iloc[i]["a"]
		if len(body) > 0 and len(body) < joke_length:
			text = "\n\n"+fix_encoding(title + " " + body + " <|endoftext|>")
			texts.append(text)
	data = pd.read_csv("qajokes1.1.2.csv")
	indices = data.shape[0]
	for i in tqdm(range(indices)):
		title = data.iloc[i]["Question"]
		body = data.iloc[i]["Answer"]
		if len(body) > 0 and len(body) < joke_length:
			text = "\n\n"+fix_encoding(title + " " + body + " <|endoftext|>")
			texts.append(text)
	print("Writing to file")
	texts = set(texts)
	for text in tqdm(texts):
		try:
			with open(text_file_name, "a+") as f:
				f.write(text)
		except:
			pass
