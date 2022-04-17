import pickle
import pandas as pd
from markdown import markdown
from bs4 import BeautifulSoup as bf
from packaging import version
from os.path import isfile
from os import getcwd
import subprocess
import json
import re
import csv

quiet_flag = '&> /dev/null'

# Keep subset of keys from dict: keyper(tuple_with_keys)(dict)
keyper = lambda keys: lambda dict: {k: dict[k] for k in keys}

categories = (
	'fix-bugs',
	'new-features',
	'documentation',
	'non-functional'
)

def load_ft_data(path, balanced=False):
	ptrn = re.compile('__label__(.*?)\s(.*)')
	ft_data = load(path)
	ft_data = ft_data.split('\n')[:-1]
	labels = [*map(lambda row: ptrn.match(row).group(1), ft_data)]
	titles = [*map(lambda row: ptrn.match(row).group(2), ft_data)]
	return titles, labels

def load_scraped_data(path):
	data = load(path)
	labels = []
	inputs = []

	emstr = lambda v: v if v else ''

	for val in data.values():
		labels.append(val['category'])
		inputs.append(
			' '.join([val['title'], emstr(val['body']), *val['commit_messages']])
		)
	
	return inputs, labels

def load_ex_data(path):
	df = pd.read_csv(path)
	labels = df['category']
	labels = labels.replace('new features', 'new-features')
	labels = labels.replace('issues fixed', 'fix-bugs')
	inputs = df['title'] + ' ' + df['body'].fillna('') + df['commits'].fillna('')
	return inputs, labels

# Load file
def load(file):
	if not isfile(file):
		raise FileNotFoundError('File does not exist')
	
	if '.pickle' in file:
		with open(file, 'rb') as f:
			data = pickle.load(f)
	else:
		with open(file) as f:
			if '.json' in file:
				data = json.load(f)
			else:
				data = f.read()

	return data

# Dump data to file
def dump(data, file):
	if '.pickle' in file:
		with open(file, 'wb') as f:
			pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
	else:
		with open(file, 'w') as f:
			if '.json' in file:
				json.dump(data, f)
			else:
				f.write(data)

# Rendered markdown text
def md_to_text(md: str):
	html = markdown(md)
	return ''.join(bf(html).findAll(text=True))

# Get latest release from list of tags
def get_latest(tags):
	return sorted(tags, key=version.parse)[-1]

# Return only first item from list-returning function
def single(fnc):
	def wrapper(*args, **kwargs):
		return fnc(*args, **kwargs)[0]

	return wrapper

# Decorate function taking cwd with @cloned(url) to clone and clean
def cloned(url):
	name = re.search('.*\/(.*).git', url).group(1)
	cwd = f'{getcwd()}/{name}' 	# Repo directory

	subprocess.run(f'git clone {url} {cwd} {quiet_flag}', shell=True)
	clean = lambda: subprocess.run(f'rm -rf {cwd}', shell=True)

	def decorator(fnc):
		def wrapper(*args, **kwargs):
			try:
				ret = fnc(cwd, *args, **kwargs)
			finally:
				clean()
			return ret

		return wrapper
	
	return decorator
	

def fasttext_csv(data_path = "data/fasttext_data.valid"):
    """Export DeepRelease data as csv so that it can be imported and annotated in tools like Google Spreadsheets """
    titles, labels = load_ft_data(data_path)
    with open('data/fasttext_data.valid.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'label'])
        writer.writeheader()
        for title, label in zip(titles, labels):
            writer.writerow({'title': title, 'label': label})
