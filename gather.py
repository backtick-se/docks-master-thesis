import pickle
import subprocess
from os import getcwd
from extract import Extractor
from visit import Visitor
import click
import re
import base64

def get_release_functions(url: str, name: str):
	cwd = f'{getcwd()}/{name}'
	
	subprocess.run(f'git clone {url} {cwd}', shell=True)
	subprocess.run(f'git tag -l > tags.txt', shell=True, cwd=cwd)
	
	with open(f'{cwd}/tags.txt') as f:
		tags = f.read().split('\n')[:-1]
	
	ids, funcs = [], []
	
	for tag in tags:
		subprocess.run(f'git checkout tags/{tag}', shell=True, cwd=cwd)

		# List of paths, list of contents
		# List of tuples (name, code, docstr, code with docstr)
		paths, contents = Extractor('py').extract(cwd)
		funcdata = [*map(Visitor.get_functions, contents)]
		
		for path, data in zip(paths, funcdata):
			for n, c, d, cd in data:
				id = f'{path}: {n}'
				value = (c, d, cd)

				if id in ids:
					i = ids.index(id)
					funcs[i].append(value)
				else:
					ids.append(id)
					funcs.append([value])
	
	subprocess.run(f'rm -rf {cwd}', shell=True)
	
	return funcs, ids

@click.command()
@click.option('--repo')
@click.option('--out', default='funcdata')
def get_data(repo: str, out: str):
	name = re.search('.*\/(.*).git', repo).group(1)
	funcs = get_release_functions(repo, name)[0]

	def process(fdata):
		codes, docs, codocs = [], [], []

		for c, d, cd in fdata:
			if c not in codes and d not in docs:
				codes.append(c)
				docs.append(d)
				codocs.append(cd)
		
		if len(codes) > 1:
			return [*zip(codes, docs, codocs)]
		
		return None

	data = filter(lambda e: e != None, [*map(process, funcs)])

	with open(f'{out}.pickle', 'wb') as f:
		pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
	get_data()


