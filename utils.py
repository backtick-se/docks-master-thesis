import pickle
from markdown import markdown
from bs4 import BeautifulSoup as bf
from packaging import version
from os.path import isfile
from os import getcwd
import subprocess
import json
import re

quiet_flag = '&> /dev/null'

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
def get_latest(tags: list[str]):
	return sorted(tags, key=version.parse)[-1]

# Decorate function taking cwd with @cloned(url) to clone and clean
def cloned(url):
	name = re.search('.*\/(.*).git', url).group(1)
	cwd = f'{getcwd()}/{name}' 	# Repo directory

	subprocess.run(f'git clone {url} {cwd} {quiet_flag}', shell=True)
	clean = lambda: subprocess.run(f'rm -rf {cwd}', shell=True)

	def decorator(fnc):
		def wrapper(*args):
			ret = fnc(cwd, *args)
			clean()
			return ret

		return wrapper
	
	return decorator
	

	