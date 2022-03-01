from os import listdir
from os.path import isfile, isdir
class Extractor:

	def __init__(self, file_type: str):
		self.file_type = file_type

	# Find all files under start directory
	def find_files(self, start: str):
		files = []

		for fd in listdir(start):
			path = f'{start}/{fd}'

			if isfile(path):
				ext = f'.{self.file_type}'
				if fd[-len(ext):] == ext: files.append(path)
			else:
				f = self.find_files(path)
				files += f if f else []
	
		return files
	
	# Get the contents of a file as string
	def get_content(self, file: str, skip_on_error: bool=True):
		if not isfile(file):
			raise ValueError(f'{file} is not a file')

		try:
			with open(file) as f:
				return f.read()
		except Exception as e:
			if skip_on_error: print(f'Parsing error, skipping file: {file}, {e}')
			else: raise e
		
		return None
	
	# Extract all paths & contents from directory
	def extract(self, dir: str):
		if not isdir(dir):
			raise ValueError(f'{dir} is not a directory')

		# Find all files
		paths = self.find_files(dir)

		# Extract all content
		contents = [*map(self.get_content, paths)]

		return paths, contents
		
		# Map function to file
		# Choose n_files random files
		# Extract n_funcs from each file
		# Save context as {function_id: [context_function_id]}

		#context_files = random.sample(files, min(n_files, len(files)))
		#context = {}

		#for path in n_files:
			#context[]

		



