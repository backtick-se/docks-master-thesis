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
def checkout_extract(tag: str, cwd: str, exts: tuple[str]):
	data = {}

	for ext in exts:
		subprocess.run(f'git checkout tags/{tag} {quiet_flag}', shell=True, cwd=cwd)
		data[ext] = Extractor(ext).extract(cwd)
	
	return data

# Clone repo an extract all the release tags
# Checkout all releases and extract {tag: {extension: (paths, contents)}}
def get_release_data(url: str, exts: tuple[str]):
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
@click.option('--src', '-s', help='Source file with extension (e.g repos.txt)')
@click.option('--out', '-o', help='Output folder (defaults to data)', default='data')
@click.option('--ext', '-e', help='Extensions to look for', multiple=True, default=('py', 'md'))
def get_data(src: str, out: str, ext: tuple[str]):

	with open(src) as f:
		repos = f.read().split('\n')

	clen = colored(len(repos), 'green')
	cext = colored(ext, 'green')
	click.echo(f'Gathering {cext} data from {clen} repos...\n')
	
	for repo in repos:
		name = re.search('.*\/(.*).git', repo).group(1)
		
		crep = colored(repo, 'green')
		click.echo(f'Processing {crep}')

		data = get_release_data(repo, ext)
		outfile = f'{out}/{name}.pickle'

		outf = colored(outfile, 'green')
		click.echo(f'Saving to: {outf}\n')

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

