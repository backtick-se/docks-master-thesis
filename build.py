import click
import subprocess
from tqdm import tqdm
from extract import Extractor
from github_fetch import fetch_responses, parse_pull_requests, fetch_data
from utils import dump, quiet_flag, cloned, keyper, single, load
from os import getcwd

"""
Dataset building script. PRs from provided repo will be fetched in the following format:
Out: [{**pr_keys, commits:[{**cm_keys}], docs (optional):[(filepath, content)]}]

Detailed info on cm and pr keys: https://docs.github.com/en/rest/reference/issues

Ex. usage:
python build.py -t $token -r backtick-se/cowait -o dataset.pickle
"""

categories = (
	'fix-bugs',
	'new-features',
	'documentation',
	'non-functional'
)

# Values to extract from PR json response
pr_keys = (
	'number',
	'title',
	'labels',
	'state',
	'pull_request',
	'body'
)

# Values to extract from commit json response
cm_keys = (
	'sha',
	'html_url',
	'commit',
	'files',
	'stats'
)

API_BASE = 'https://api.github.com'
GIT_BASE = 'https://github.com'

# Get url for repo cloning from user/repo
cl_url = lambda user, repo: f'{GIT_BASE}/{user}/{repo}.git'
# Get url for PR fetching from user/repo
pr_url = lambda user, repo: f'{API_BASE}/repos/{user}/{repo}/issues?per_page=100&state=closed'
# Get url for commits belonging to a PR
cs_url = lambda user, repo, pnr: f'{API_BASE}/repos/{user}/{repo}/pulls/{pnr}/commits'
# Get url for commit content of certain commit
cm_url = lambda user, repo, sha: f'{API_BASE}/repos/{user}/{repo}/commits/{sha}'
# Get url for listing all available repo labels
lb_url = lambda user, repo: f'{API_BASE}/repos/{user}/{repo}/labels'

# Checkout every PR and extend with doc data
def extract_docs(cwd, data):
	dwd = f'{cwd}/docs'

	def checkout_extract(pr):
		pr_num = pr['number']

		if 'merged_at' in pr['pull_request']:
			subprocess.run(f'git pr {pr_num} {quiet_flag}', cwd=cwd, shell=True)
			mdpaths, mdcontents = Extractor('md').extract(dwd)
			rspaths, rscontents = Extractor('rst').extract(dwd)

			paths = mdpaths + rspaths
			contents = mdcontents + rscontents

			# Make paths relative to repo root
			paths = [*map(lambda p: p.replace(f'{getcwd()}/', ''), paths)]

			return [*zip(paths, contents)]
		else:
			raise ValueError('PR not merged')

	ret = []

	# Remove from dataset if ValueError (doc folder does not exist or pr not merged)
	for pr in data:
		try:
			ret.append({'docs': checkout_extract(pr), **pr})
		except ValueError:
			pass
	
	return ret

def get_pull_requests(token, u, r):
	responses = fetch_responses(token, pr_url(u, r))
	prs = parse_pull_requests(responses)

	# Filter keys
	return [*map(keyper(pr_keys), prs)]


def get_commits(pnr, token, u, r):
	# Get extended commit info for a sha
	get_commit = lambda sha: single(fetch_data)(
		token, cm_url(u, r, sha)
	)

	# Get from /pr url, extract sha and fetch full
	pr_cms, rem	= fetch_data(token, cs_url(u, r, pnr), get_remaining=True)
	shas = [*map(lambda c: c['sha'], pr_cms)]

	if int(rem) < len(shas):
		raise ConnectionError('Out of API calls')
	else:
		commits = [*map(get_commit, shas)]

	return [*map(keyper(cm_keys), commits)]

def categorize(data, label_map):

	def extract_category(pr):
		labels = [*map(lambda l: l['name'], pr['labels'])]
		cats =  [label_map[l] for l in labels]
		return max(set(cats), key=cats.count) if cats else None
	
	return [{'category': extract_category(pr), **pr} for pr in data]
	


@click.command()
@click.option('--token', '-t', help='GitHub API user authentication token')
@click.option('--repo', '-r', help='Target owner and repo: e.g backtick-se/cowait')
@click.option('--format', '-f', help='Output file format, defaults to pickle', default='pickle')
@click.option('--docs', '-d', help='Boolean flag for doc state extraction', is_flag=True, default=False)
@click.option('--resume', '-c', help='Resume from paused dataset build', is_flag=True, default=False)
@click.option('--labelcat', '-l', help='Set categories based on labels', is_flag=True, default=False)
def run(token: str, repo: str, format: str, docs: bool, resume: bool, labelcat: bool):

	# User, repo
	u, r = repo.split('/')

	out = f'data/prd_{u}_{r}.{format}'

	label_map = {}

	if labelcat:
		scheme = [(i, k) for i, k in enumerate(categories)]
		click.echo(scheme)
		labels = fetch_data(token, lb_url(u, r))
		click.echo(f'Please select category mapping for each label ({len(labels)=})')
		
		for l in labels:
			name = l['name']
			desc = l['description']
			cat = input(f'{name} // {desc}: ')
			label_map[name] = categories[int(cat)] if cat else None

		print(label_map)
		
	if not resume:
		# Get the PR data
		click.echo('Fetching PR data...')
		data = get_pull_requests(token, u, r)
		click.echo(f'Fetched {len(data)} PRs...')

		if docs:
			# Clone, checkout and save doc state for every PR
			click.echo('Extracting doc states...')
			data = cloned(cl_url(u, r))(extract_docs)(tqdm(data))
	
		click.echo('Fetching commit data...')
	else:
		# Load from "out" file location
		data = load(out)
		click.echo('Resuming commit data fetch...')
	
	# Fetch, filter and add commit data to PRs
	try:
		for pr in tqdm([*filter(lambda p: 'commits' not in p, data)]):
			pr['commits'] = get_commits(pr['number'], token, u, r)
	except ConnectionError as e:
		fetched = len([*filter(lambda pr: 'commits' in pr, data)])
		click.echo(f'Ran out of API calls, {fetched}/{len(data)} prs complete')

	click.echo(f'Attempting automatic categorization...')
	data = categorize(data, label_map)

	click.echo(f'Done! Saving to {out}')

	dump(data, out)

if __name__ == '__main__':
	run()
