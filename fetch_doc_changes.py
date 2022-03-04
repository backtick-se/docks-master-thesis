import shutil
import subprocess
import os
import json

if __name__ == "__main__":

    def extract_repo_changes(repo_path):
        # Hämta tags
        subprocess.run(f'git tag -l > __tags.txt', shell=True, cwd=f"{repo_path}")
        with open(repo_path + '/__tags.txt') as f:
            tags = f.read().split('\n')
        os.remove(repo_path + '/__tags.txt')

        # Extrahera data från alla tag-ändringar
        repo_changes = []
        for i in range(1, len(tags)):
            tag_from = tags[i-1]
            tag_to = tags[i]
            subprocess.run(f'git diff {tag_from} {tag_to} --name-only > __changes.txt', shell=True, cwd=f"{repo_path}")
            with open(repo_path + '/__changes.txt') as f:
                changed_files = f.read().split('\n')
                doc_filter = lambda x: x.startswith('docs/') and (x.endswith('.md') or x.endswith('.rst'))
                changes = filter(doc_filter, changed_files)
            os.remove(repo_path + '/__changes.txt')
            repo_changes.append({
                'tag_from': tag_from,
                'tag_to': tag_to,
                'changed_doc': list(changes)
            })
        return repo_changes

    with open('./docs.txt') as f:
        repo_urls = f.read().split('\n')
    #repo_urls = repo_urls[:4] # testing

    out_path = 'data/doc_validation.json'
    data = {}
    with open(out_path, 'w') as f:
        f.write(json.dumps(data))

    # Spara output för varje iteration ifall något skulle hänga upp sig...
    for repo_url in repo_urls:
        with open(out_path) as f:
            data = json.loads(f.read())
        repo_name = "__repo"
        subprocess.run(f"git clone {repo_url} {repo_name}", shell=True)
        data[repo_url] = extract_repo_changes(os.getcwd() + '/' + repo_name)
        shutil.rmtree(repo_name)
        with open(out_path, 'w') as f:
            f.write(json.dumps(data))