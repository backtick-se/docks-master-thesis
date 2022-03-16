import subprocess
from os import getcwd
from os.path import isdir
from extract import Extractor
from termcolor import colored as c
from utils import get_latest, load, dump
from packaging import version
from tqdm import tqdm
import click
import re

quiet_flag = '&> /dev/null'

# Checkout to given tag and extract {extension: (paths, contents)}
def checkout_extract(tag: str, cwd: str, exts: list[str]):
	try:
		subprocess.run(f'git checkout tags/{tag} {quiet_flag}', shell=True, cwd=cwd)
	except FileNotFoundError:
		return {ext: ([], []) for ext in exts}

	return {
		ext: Extractor(ext).extract(cwd)
		for ext in exts
	}

# Checkout all releases and extract {tag: {extension: (paths, contents)}}
def get_release_data(url: str, cext: list[str], dext: list[str], tags: list[str] = []):
	name = re.search('.*\/(.*).git', url).group(1)
	cwd = f'{getcwd()}/{name}' 	# Repo directory
	dwd = f'{cwd}/docs' 		# Docs directory

	try:
		# Clone the repo
		subprocess.run(f'git clone {url} {cwd} {quiet_flag}', shell=True)
		clean = lambda: subprocess.run(f'rm -rf {cwd}', shell=True)
		
		# Extract tags if not provided
		if not tags:
			subprocess.run(f'git tag -l > tags.txt', shell=True, cwd=cwd)
			tags = load(f'{cwd}/tags.txt').split('\n')[:-1]

		# Assert that tags and doc directory exist
		if not tags or not isdir(dwd):
			raise ValueError(f'Repo must contain docs folder and release tags')
		
		data = {
			tag: {
				**checkout_extract(tag, cwd, cext),
				**checkout_extract(tag, dwd, dext)
			} for tag in tqdm(tags)
		}

		clean()
		return data

	except Exception as e:
		clean()
		raise e


@click.command()
@click.option('--src', '-s', help='Source file with extension (e.g repos.txt)')
@click.option('--out', '-o', help='Output folder (defaults to data)', default='data')
@click.option('--rel', '-r', help='Release tag file (default data/release_tags.pickle)', default='data/release_tags.pickle')
@click.option('--cext', '-ce', help='Code extensions to look for', multiple=True, default=['py'])
@click.option('--dext', '-de', help='Doc extensions to look for', multiple=True, default=['md', 'rst'])
def get_data(src: str, out: str, rel: str, cext: list[str], dext: list[str]):

	repos = load(src).split('\n')

	click.echo('Gathering {0} data from {1} repos...\n'.format(c(cext + dext, 'green'), c(len(repos), 'green')))

	try:
		release_tags = load(rel)
		auto = False
	except FileNotFoundError:
		auto = True
		release_tags = {}
	
	if auto:
		click.echo('{0} Release tag file not found. Using "git tag -l"\n'.format(c('WARNING:', 'yellow')))
	
	for repo in repos:
		# Name for output file (username-reponame)
		r = re.search('.*\/(.*)\/(.*).git', repo)
		name = f'{r.group(1)}-{r.group(2)}'
		outfile = f'{out}/{name}.pickle'
		
		click.echo('Processing {0} -> {1}'.format(c(repo, 'green'), outfile))

		# Get the release data
		try:
			tags = [*release_tags[repo]] if repo in release_tags else []

			if not tags and not auto:
				raise ValueError('No releases found in tag file')

			data = get_release_data(repo, cext, dext, tags)
		except ValueError as e:
			click.echo(c(f'{e}. Skipping...\n', 'red'))
			continue

		extens, counts, *passed = verify(data, dext)
		data = process(data, dext)

		if False not in passed:
			# Stringified stats
			extens = '\t'.join([*extens])
			counts = '\t'.join([*map(str, counts)])

			click.echo(f'Latest release ({get_latest(data.keys())}):')
			click.echo(c(extens, 'green'))
			click.echo(f'{counts}\n')

			dump(data, outfile)
		
		else:
			indices = [i for i, c in enumerate(passed) if c == False]
			click.echo(c(f'Data did not pass criteria {indices}. Discarding...\n', 'red'))

# Process the data
def process(data, dext: list[str]):
	latest = get_latest(data.keys())

	return {
		**data,
		'latest': data[latest]
	}

# Verify release data with specific criteria
def verify(data, dext: list[str]):
	latest = get_latest(data.keys())

	extens = [*data[latest]]
	counts = [*map(
		lambda t: len(t[0]),
		data[latest].values()
	)]

	# Check data
	tagcnt = len(data.keys())
	doccnt = sum([counts[i] for i, ext in enumerate(extens) if ext in dext])
	chrcnt = sum([sum(map(len, data[latest][ext][1])) for ext in dext])
	
	return (
		extens,
		counts,
		doccnt >= 1,
		chrcnt >= 1000,
		tagcnt >= 2
	)

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

