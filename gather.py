import pickle
import subprocess
from os import getcwd
from extract import Extractor
from visit import Visitor
from termcolor import colored
from packaging import version
from tqdm import tqdm
import click
import re

quiet_flag = '&> /dev/null'

# Checkout to given tag and extract {extension: (paths, contents)}
def checkout_extract(tag: str, cwd: str, exts: tuple[str]):
	subprocess.run(f'git checkout tags/{tag} {quiet_flag}', shell=True, cwd=cwd)

	return {
		ext: Extractor(ext).extract(cwd)
		for ext in exts
	}

# Clone repo an extract all the release tags
# Checkout all releases and extract {tag: {extension: (paths, contents)}}
def get_release_data(url: str, exts: tuple[str]):
	name = re.search('.*\/(.*).git', url).group(1)
	cwd = f'{getcwd()}/{name}'

	subprocess.run(f'git clone {url} {cwd} {quiet_flag}', shell=True)
	subprocess.run(f'git tag -l > tags.txt', shell=True, cwd=cwd)
	
	with open(f'{cwd}/tags.txt') as f:
		tags = f.read().split('\n')[:-1]

	if not tags: 
		raise ValueError(f'No tags could be extracted from {url}: {tags}')
	
	data = {tag: checkout_extract(tag, cwd, exts) for tag in tqdm(tags)}

	subprocess.run(f'rm -rf {cwd}', shell=True)

	return data

# Verify release data with specific criterion
def verify(data):
	amtrsh = 1000 # Characters
	docext = ['md', 'rst']

	latest = sorted(data.keys(), key=version.parse)[-1]

	extens = data[latest].keys()
	counts = [*map(
		lambda t: len(t[0]),
		data[latest].values()
	)]

	# Checks
	docfiles = 0

	for i, ext in enumerate(extens):
		if ext in docext: docfiles += counts[i]
	
	docamt = 0

	for ext in docext:
		docamt += sum(map(len, data[latest][ext][1]))
	
	return latest, docfiles > 0 and docamt > amtrsh, extens, counts

@click.command()
@click.option('--src', '-s', help='Source file with extension (e.g repos.txt)')
@click.option('--out', '-o', help='Output folder (defaults to data)', default='data')
@click.option('--ext', '-e', help='Extensions to look for', multiple=True, default=('py', 'md', 'rst'))
def get_data(src: str, out: str, ext: tuple[str]):

	with open(src) as f:
		repos = f.read().split('\n')

	clen = colored(len(repos), 'green')
	cext = colored(ext, 'green')
	click.echo(f'Gathering {cext} data from {clen} repos...\n')
	
	for repo in repos:
		# Name for output file (username-reponame)
		r = re.search('.*\/(.*)\/(.*).git', repo)
		name = f'{r.group(1)}-{r.group(2)}'
		outfile = f'{out}/{name}.pickle'
		
		crep = colored(repo, 'green')
		click.echo(f'Processing {crep} -> {outfile}')

		# Get the release data
		try:
			data = get_release_data(repo, ext)
		except ValueError:
			click.echo(colored(f'Error processing {repo}. Skipping...\n', 'red'))
			continue

		latest, passed, extens, counts = verify(data)

		if passed:
			# Stringified stats
			extens = '\t'.join(extens)
			counts = '\t'.join(map(str, counts))

			cextes = colored(extens, 'green')
			click.echo(f'Latest release ({latest}):')
			click.echo(cextes)
			click.echo(counts)
			click.echo()

			with open(outfile, 'wb') as f:
				pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
		
		else:
			click.echo(colored('Data did not pass verification. Discarding...', 'red'))

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

