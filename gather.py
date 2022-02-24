import pickle
import subprocess
from os import getcwd
from uuid import uuid1
from extract import Extractor

def get_release_functions(url: str, name: str = uuid1()):
	cwd = f'{getcwd()}/{name}'
	
	subprocess.run(f'git clone {url} {cwd}', shell=True)
	subprocess.run(f'git tag -l > tags.txt', shell=True, cwd=cwd)
	
	with open(f'{cwd}/tags.txt') as f:
		tags = f.read().split('\n')
	
	data = {}
	
	for tag in tags:
		subprocess.run(f'git checkout tags/{tag}', shell=True, cwd=cwd)
		
		paths, funcs = Extractor('py').extract(cwd)
		
		for path, funclist in zip(paths, funcs):
			for name, code, docstr in funclist:
				id = f'{path}: {name}'
				value = (code, docstr)
				
				if id in data.keys():
					data[id][tag] = value
				else:
					data[id] = {
						tag: value
					}
	
	return data

if __name__ == '__main__':
	funcdata = get_release_functions('https://github.com/pallets/click.git', 'click')
	data = {}
	
	for key, value in funcdata.items():
		unique = set(value.values())
		if len(unique) > 1: data[key] = unique

	with open('funcdata_no_methods.pickle', 'wb') as f:
		pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


