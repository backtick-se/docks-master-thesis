## Data annotation

1. **Fetch data for repository**

- `source venv/bin/activate`
- `python build.py -t $GH_PA_TOKEN -r owner/repo -f json -l`
- Fetched data will be outputted to data/prd_{owner}_{repo}.{format}

2. **Annotate the fetched data**

- `cd annotator && yarn install`
- `yarn start`
- Select the fetched data file
- Annotate a PR by selecting category in "Label" section
- Click "Accept Datapoint" to add annotated PR
- Click "Reject Datapoint" to exclude PR from dataset
- When done, click "Save" to download the annotated dataset

Keep in mind that refreshing the Annotator app will reset the annotation process
