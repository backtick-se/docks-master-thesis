import pickle
from os.path import isfile

def load(file):
	if not isfile(file):
		raise FileNotFoundError('File does not exist')
	
	if '.pickle' in file:
		with open(file, 'rb') as f:
			data = pickle.load(f)
	else:
		with open(file) as f:
			data = f.read()

	return data

def dump(data, file):
	if '.pickle' in file:
		with open(file, 'wb') as f:
			pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
	else:
		with open(file, 'w') as f:
			f.write(data)