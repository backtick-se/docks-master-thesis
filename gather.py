import pickle
import subprocess
from os import getcwd
from uuid import uuid1
from extract import Extractor
import click
import re

def get_release_functions(url: str, name: str):
	cwd = f'{getcwd()}/{name}'
	
	subprocess.run(f'git clone {url} {cwd}', shell=True)
	subprocess.run(f'git tag -l > tags.txt', shell=True, cwd=cwd)
	
	with open(f'{cwd}/tags.txt') as f:
		tags = f.read().split('\n')[:-1]
	
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
	
	subprocess.run(f'rm -rf {cwd}', shell=True)
	
	return data

@click.command()
@click.option('--repo')
@click.option('--out', default='funcdata')
def get_data(repo: str, out: str):
	name = re.search('.*\/(.*).git', repo).group(1)
	funcdata = get_release_functions(repo, name)
	data = {}
	
	for key, value in funcdata.items():
		funs = []
		docs = []

		for fun, doc in value.values():
			if doc not in docs and fun not in funs:
				funs.append(fun)
				docs.append(doc)

		if len(funs) > 1: data[key] = zip(funs, docs)

	with open(f'{out}.pickle', 'wb') as f:
		pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
	get_data()


