import os
import subprocess
import json
import model

cwd = os.getcwd()
eval_wd = cwd + "/../eval-repo/"

def load_misses():
    with open(eval_wd + 'misses.json') as f:
        misses = json.loads(f.read())
    return misses

def extract_commits():
    subprocess.run("git log --reverse --format=format:%H > tmp_eval_commits.txt", shell=True, cwd=eval_wd)
    with open(eval_wd + 'tmp_eval_commits.txt') as f:
        commits = f.read().split('\n')
    os.remove(eval_wd + 'tmp_eval_commits.txt')
    return commits


misses = load_misses()
commits = extract_commits()

def evaluate(predict):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    for commit in commits:
        subprocess.run(f"git checkout {commit}", shell=True, cwd=eval_wd)
        should_flag = commit in misses
        prediction = predict(eval_wd, commit)
        if should_flag:
            if prediction:
                tp += 1
            else:
                fn += 1
        else:
            if predict:
                fp += 1
            else:
                tn += 1

    # Reset head of eval-repo
    subprocess.run(f"git checkout main", shell=True, cwd=eval_wd)

    print(f"#Right predictions: {tp + tn}")
    print(f"#Wrong predictions: {fp + fn}")
    print(f"Precision: {tp / (tp + fp)}")
    print(f"Recall: {tp / (tp + fn)}")

evaluate(model.predict)
print(cwd)