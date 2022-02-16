from os import listdir
from os.path import isfile, isdir
import numpy as np
from tqdm import tqdm

class Extractor:

	def __init__(self, fileType: str):
		self.fileType = fileType

	def find_files(self, start: str):
		files = []

		for fd in listdir(start):
			path = f'{start}/{fd}'

			if isfile(path):
				ext = f'.{self.fileType}'
				if fd[-len(ext):] == ext: files.append(path)
			else:
				f = self.find_files(path)
				files += f if f else []
	
		return files
	
	def get_content(self, file: str, skipError: bool=True):
		if not isfile(file):
			raise ValueError(f'{file} is not a file')

		try:
			with open(file) as f:
				return f.read()
		except Exception as e:
			if skipError: print(f'Parsing error, skipping file: {file}, {e}')
			else: raise e
	
	def extract(self, dir: str):
		if not isdir(dir):
			raise ValueError(f'{dir} is not a directory')
		
		files = self.find_files(dir)
		return np.array([self.get_content(f) for f in tqdm(files)])

		



