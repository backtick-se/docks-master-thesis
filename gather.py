import pickle
import subprocess
from os import getcwd
from uuid import uuid1
from extract import Extractor
import click
import re
import ast

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
			for name, code, docstr, codewithdoc in funclist:
				id = f'{path}: {name}'
				value = (code, docstr, codewithdoc)
				
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
		fund = []

		for fun, doc, codewithdoc in value.values():
			if ast.parse(fun) not in [*map(ast.parse, funs)] and doc not in docs:
				funs.append(fun)
				docs.append(doc)
				fund.append(codewithdoc)

		if len(funs) > 1: data[key] = [*zip(funs, docs, fund)]

	with open(f'{out}.pickle', 'wb') as f:
		pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
	get_data()


