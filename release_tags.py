import click
import re
import requests
import time
from tqdm import tqdm
import pickle
from os.path import exists
from utils import load

def parse_response(response):
    remaining = int(response.headers['X-RateLimit-Remaining'])
    releases = response.json()
    data = {}
    if response.status_code == 200:
        for release in releases:
            tag = release['tag_name']
            data[tag] = {
                'tag': tag,
                'html_url': release['html_url'],
                'created_at': release['created_at'],
                'published_at': release['published_at'],
                'body': release['body'],
            }
    elif response.status_code == 404:
        # Some repositories don't have any tagged releases,
        # ex. https://github.com/HonzaKral/django-threadedcomments/releases
        pass
    else:
        print('raising exception...')
        raise Exception('Unexpected status code:', response.status_code, response.reason)
    return data, remaining

def dump(data, outfile):
    with open(outfile, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

@click.command()
@click.option('--src', '-s', help='Source file with extension (e.g repos.txt)')
@click.option('--token', '-t', help='GitHub API user authentication token')
@click.option('--out', '-o', help='Output folder (defaults to data)', default='data')
def get_releases(src: str, token: str, out: str):
    outfile = out + '/release_tags.pickle'

    with open(src) as f:
        repos = f.read().split('\n')

    data = {}
    for repo in tqdm(repos):

        # Avoid unecessary API calls
        if repo in data:
            continue

        # Load cached data from disk
        if exists(outfile):
            data = load(outfile)

        # Uncomment to debug crash
        #print(repo)

        headers = {'Authorization': 'token ' + token}
        name = re.search('.*\/(.*\/.*).git', repo).group(1)
        response = requests.get(f'https://api.github.com/repos/{name}/releases', headers=headers)
        data[repo], remaining = parse_response(response)

        # Store data often
        dump(data, outfile)

        if not remaining > 0:
            print('Reached GitHub rate limit')
            time.sleep(60 * 60)
            print('Retrying...')

if __name__ == '__main__':
    get_releases()
