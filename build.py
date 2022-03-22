import click
import subprocess
from tqdm import tqdm
from extract import Extractor
from github_fetch import fetch_responses, parse_pull_requests
from utils import dump, quiet_flag, cloned

# Values to extract from PR json response
keys = (
	'number',
	'title',
	'labels',
	'state',
	'pull_request',
	'body'
)

# Get url for repo cloning from user/repo
cl_url = lambda user, repo: f'https://github.com/{user}/{repo}.git'
# Get url for PR fetching from user/repo
pr_url = lambda user, repo: f'https://api.github.com/repos/{user}/{repo}/issues?per_page=100&state=closed'

# Checkout every PR and extend with doc data
def extract_docs(cwd, data):
	dwd = f'{cwd}/docs'

	def checkout_extract(pr):
		pr_num = pr['number']

		if 'merged_at' in pr['pull_request']:
			subprocess.run(f'git pr {pr_num} {quiet_flag}', cwd=cwd, shell=True)
			paths, contents = Extractor('md').extract(dwd)
			return {'paths': paths, 'contents': contents}
		else:
			raise ValueError('PR not merged')

	ret = []

	# Remove from dataset if ValueError (doc folder does not exist or pr not merged)
	for pr in tqdm(data):
		try:
			ret.append({**checkout_extract(pr), **pr})
		except ValueError:
			pass
	
	return ret

@click.command()
@click.option('--auth', '-a', help='GitHub API user authentication token')
@click.option('--target', '-t', help='Target user and repo: e.g backtick-se/cowait')
def run(auth: str, target: str):
	"""
    Ex. usage:
    python build.py -t $token -r backtick-se/cowait -o dataset.pickle
    """

	# User, repo
	u, r = target.split('/')

	# Get the PR data
	responses = fetch_responses(auth, pr_url(u, r))
	prs = parse_pull_requests(responses)

	# Only keep the desired keys
	pr_data = [*map(lambda pr: {k: pr[k] for k in keys}, prs)]

	# Clone, checkout and save doc state for every PR
	data = cloned(cl_url(u, r))(extract_docs)(pr_data)

	dump(data, f'data/prd_{u}_{r}.pickle')

if __name__ == '__main__':
	run()

