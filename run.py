from train import DiffTrainer

if __name__ == '__main__':
    config = {
        'rmo': True,
        'per_file': False,
        'distill': True,
        'max_length': 512,
        'batch_size': 32,
        'num_epochs': 3,
        'split': 0.8,
        'seed': 42,
        'thaw': 0,
        'lr': 1e-5,
    }
    trainer = DiffTrainer('distilbert-base-uncased',
                          'temp.pickle', config=config)
    trainer.train()
