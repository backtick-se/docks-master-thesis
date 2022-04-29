from train import DiffTrainer

if __name__ == '__main__':
    base_config = {
        'rmo': True,
        'per_file': False,
        'distill': True,
        'max_length': 512,
        'batch_size': 32,
        'num_epochs': 3,
        'split': 0.8,
        'seed': 42,
        'thaw': 0,
        'lr': 1e-3,
    }

    schedule = [{
        'cp': 'distilbert-base-uncased',
        'configs': [{
            'thaw': 1
        }]
    }, {
        'cp': 'huggingface/CodeBERTa-small-v1',
        'configs': [{
            'thaw': 1
        }]
    }, {
        'cp': 'microsoft/codebert-base',
        'configs': [{
            'thaw': 0
        }, {
            'thaw': 1
        }]
    }, {
        'cp': 'jeniya/BERTOverflow',
        'configs': [{
            'thaw': 0
        }, {
            'thaw': 1
        }]
    }]

    for entry in schedule:
        cp = entry['cp']

        for config in entry['configs']:
            cf = {**base_config, **config}
            trainer = DiffTrainer(cp, 'scraped_diffs.pickle', config=cf)
            trainer.train()
