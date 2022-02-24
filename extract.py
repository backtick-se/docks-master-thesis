from os import listdir
from os.path import isfile, isdir
from visitor import Visitor
class Extractor:

	def __init__(self, fileType: str):
		self.fileType = fileType

	# Find all files under start directory
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
	
	# Get the contents of a file as string
	def get_content(self, file: str, skipError: bool=True):
		if not isfile(file):
			raise ValueError(f'{file} is not a file')

		try:
			with open(file) as f:
				return f.read()
		except Exception as e:
			if skipError: print(f'Parsing error, skipping file: {file}, {e}')
			else: raise e
	
	# Extract all methods and their project context from directory
	def extract(self, dir: str, n_files: int = 10, n_funcs: int = 10):
		if not isdir(dir):
			raise ValueError(f'{dir} is not a directory')

		# Find all files + id
		paths = self.find_files(dir)

		# Find all functions
		def path_to_funcs(path):
			try:
				return Visitor.get_functions(self.get_content(path))
			except Exception as e:
				print(f'Error parsing file {path}: {e}')
				return []
				
		funcs = [*map(path_to_funcs, paths)]

		return paths, funcs
		
		# Map function to file
		# Choose n_files random files
		# Extract n_funcs from each file
		# Save context as {function_id: [context_function_id]}

		#context_files = random.sample(files, min(n_files, len(files)))
		#context = {}

		#for path in n_files:
			#context[]

		



