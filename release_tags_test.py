from utils import load

repos = set()
files = [
    'repos/AwesomePython/all.txt',
    'repos/AwesomePython/docs_folder.txt',
    'repos/CodeSearchNet/all.txt',
    'repos/CodeSearchNet/docs_folder.txt',
]
for file in files:
    with open(file) as f:
        repos = repos.union(f.read().split('\n'))

data = load('data/release_tags.pickle')
print(len(data), len(repos))

assert len(repos) == len(data)
for repo in repos:
    assert repo in data