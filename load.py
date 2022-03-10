import pickle
from os.path import isfile

def load(file):
	if not isfile(file):
		raise FileNotFoundError('File does not exist')
		
	with open(file, 'rb') as f:
		data = pickle.load(f)

	return data

def load_data():
	return load('funcdata.pickle')