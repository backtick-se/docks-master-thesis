import click
import requests
import pickle

def fetch_responses(token, url):
	responses = []
	while True:
		headers = {'Authorization': 'token ' + token}
		rsp = requests.get(url, headers=headers)
		responses.append(rsp)
		if 'next' in rsp.links:
			url = rsp.links['next']['url']
		else:
			break
	return responses

def parse_pull_requests(responses):
	pull_requests = []
	for r in responses:
		for issue in r.json():
			# Every PR is an issue but not every issue is a PR
			if 'pull_request' in issue:
				pull_requests.append(issue)

	return pull_requests

# General fetch+parse function
def fetch_data(token, url):
	responses = fetch_responses(token, url)
	remaining = responses[-1].headers['X-RateLimit-Remaining']
	
	ret = []

	for r in responses:
		data = r.json()

		if type(data) is list:
			ret += data
		else:
			ret.append(data)

	return ret, remaining

def parse_requests(input_file, output_file):
	with open(input_file, 'rb') as f:
		data = pickle.load(f)
	assert set([r.status_code for r in data]) == set([200])
	pr = parse_pull_requests(data)
	print(f"Found {len(pr)} prs")
	with open(output_file, 'wb') as f:
		pickle.dump(pr, f, protocol=pickle.HIGHEST_PROTOCOL)

@click.command()
@click.option('--token', '-t', help='GitHub API user authentication token')
@click.option('--url', '-u', help='URL to start fetching')
@click.option('--out', '-o', help='Output file')
def run(token: str, url: str, out: str):
	"""
	Ex. usage:
	python3 github_fetch.py -t $token -u "https://api.github.com/repos/pandas-dev/pandas/issues?per_page=100&state=open" -o issues.pickle

	python3
	import pickle
	from github_fetch import *
	parse_requests('issues.pickle', 'pr.pickle')
	"""
	responses = fetch_responses(token, url)
	print(len(responses), "responses", responses[:3])
	with open(out, 'wb') as f:
		pickle.dump(responses, f, protocol=pickle.HIGHEST_PROTOCOL)
	if responses:
		print(responses[-1].headers['X-RateLimit-Remaining'], "remaining api calls.")

if __name__ == '__main__':
	run()