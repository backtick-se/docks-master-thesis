import pickle
import subprocess
from os import getcwd
from extract import Extractor
from visit import Visitor
from termcolor import colored
from tqdm import tqdm
import click
import re

quiet_flag = '&> /dev/null'

# Checkout to given tag and extract {extension: (paths, contents)}
def checkout_extract(tag: str, cwd: str, exts: list[str]):
	data = {}

	for ext in exts:
		subprocess.run(f'git checkout tags/{tag} {quiet_flag}', shell=True, cwd=cwd)
		data[ext] = Extractor(ext).extract(cwd)
	
	return data

# Clone repo an extract all the release tags
# Checkout all releases and extract {tag: {extension: (paths, contents)}}
def get_release_data(url: str, exts: list[str]):
	name = re.search('.*\/(.*).git', url).group(1)
	cwd = f'{getcwd()}/{name}'

	subprocess.run(f'git clone {url} {cwd} {quiet_flag}', shell=True)
	subprocess.run(f'git tag -l > tags.txt', shell=True, cwd=cwd)
	
	with open(f'{cwd}/tags.txt') as f:
		tags = f.read().split('\n')[:-1]
	
	data = {tag: checkout_extract(tag, cwd, exts) for tag in tqdm(tags)}

	subprocess.run(f'rm -rf {cwd}', shell=True)

	return data

@click.command()
@click.option('--source', '-s', help='Source file with extension (e.g repos.txt)')
@click.option('--out', '-o', help='Output file without extension (e.g data/release_data)', default='data/release_data')
@click.option('--ext', '-e', help='Extensions to look for', multiple=True, default=['py', 'md'])
def get_data(source: str, out: str, ext: list[str]):

	with open(source) as f:
		repos = f.read().split('\n')
	
	def process(repo):
		crep = colored(repo, 'green')
		click.echo(f'Processing {crep}')
		return get_release_data(repo, ext)

	data = {repo: process(repo) for repo in repos}

	outfile = f'{out}.pickle'
	outf = colored(outfile, 'green')

	click.echo(f'\nSaving to: {outf}\n')

	with open(outfile, 'wb') as f:
		pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
	get_data()


# Specific extraction of python functions from repo (old)
# def get_release_functions(url: str):
# 	data = get_release_data(url, ['py'])
	
# 	ids, funcs = [], []
	
# 	for tag in data.keys():
# 		paths, contents = data[tag]['py']
# 		funcdata = [*map(Visitor.get_functions, contents)]
		
# 		for path, data in zip(paths, funcdata):
# 			for n, c, d, cd in data:
# 				id = f'{path}: {n}'
# 				value = (c, d, cd)

# 				if id in ids:
# 					i = ids.index(id)
# 					funcs[i].append(value)
# 				else:
# 					ids.append(id)
# 					funcs.append([value])
	
# 	return funcs, ids

# @click.command()
# @click.option('--repo')
# @click.option('--out', default='funcdata')
# def get_func_data(repo: str, out: str):
# 	name = re.search('.*\/(.*).git', repo).group(1)
# 	funcs = get_release_functions(repo, name)[0]

# 	def process(fdata):
# 		codes, docs, codocs = [], [], []

# 		for c, d, cd in fdata:
# 			if c not in codes and d not in docs:
# 				codes.append(c)
# 				docs.append(d)
# 				codocs.append(cd)
		
# 		if len(codes) > 1:
# 			return [*zip(codes, docs, codocs)]
		
# 		return None

# 	data = filter(lambda e: e != None, [*map(process, funcs)])

# 	with open(f'{out}.pickle', 'wb') as f:
# 		pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

