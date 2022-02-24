import pickle

def load(file):
	with open(file, 'rb') as f:
		data = pickle.load(f)

	return data