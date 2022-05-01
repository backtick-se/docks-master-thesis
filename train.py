from exjobb.utils import load, dump, load_diff_data, categories
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_scheduler
from torch.utils.data import DataLoader
from torch.optim import AdamW
from datasets import Dataset, DatasetDict
from os import getcwd, path
from tqdm import tqdm
import statistics
import pickle
import torch
from tqdm.auto import tqdm
from datasets import load_metric
import os
import numpy as np
import time


class DiffTrainer:
    def __init__(self, checkpoint, datafile, config={
            'rmo': True,
            'per_file': False,
            'distill': True,
            'max_length': 512,
            'batch_size': 32,
            'num_epochs': 10,
            'split': 0.8,
            'seed': 42,
            'thaw': 0,
            'lr': 1e-3,
    }):
        self.checkpoint = checkpoint
        self.datafile = datafile
        self.config = config

        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)

        self.train_dataloader, self.eval_dataloader = \
            self.create_dataloaders(datafile)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            checkpoint, num_labels=len(categories)
        )

        # Freeze all base layers, unfeeze thaw
        self.shape_model(self.config['thaw'])

        self.optimizer = AdamW(self.model.parameters())

        self.lr_scheduler = get_scheduler(
            name="linear", optimizer=self.optimizer, num_warmup_steps=0, num_training_steps=len(self.train_dataloader)
        )

        # Either load checkpoint or create a
        # new path and initialized variables
        self.PATH = self.load_checkpoint()

        # Optimizer to cuda
        for state in self.optimizer.state.values():
            for k, v in state.items():
                if isinstance(v, torch.Tensor):
                    state[k] = v.cuda()

    def show_model(self):
        for name, param in self.model.named_parameters():
            print(name, param.requires_grad)

    def shape_model(self, thaw):
        if thaw != -1:
            # Freeze all base model layers
            for param in self.model.base_model.parameters():
                param.requires_grad = False

            # Thaw some encoder layers
            for i in range(thaw):
                try:
                    for param in self.model.base_model.transformer.layer[-(i+1)].parameters():
                            param.requires_grad = True
                except:
                    for param in self.model.base_model.encoder.layer[-(i+1)].parameters():
                        param.requires_grad = False

    def load_checkpoint(self):
        thaw = self.config['thaw']
        lr = self.config['lr']
        per_file = self.config['per_file']
        distill = self.config['distill']

        state = "solid" if thaw == 0 else "liquid" if thaw == - \
            1 else "thaw" + str(thaw)
        rate = f'_{lr:.0e}' if lr != 1e-3 else ''
        level = '_pf' if per_file else '_pp'
        dis = '_dis' if distill else ''

        try:
            name = self.checkpoint.split('/')[1]
        except:
            name = self.checkpoint

        PATH = f'out/{name}_diffs{level}{dis}{rate}_{state}.pt'

        if path.isfile(PATH):
            print(f'Loading checkpoint from: {PATH}')
            cp = torch.load(PATH)
            self.model.load_state_dict(cp['model_state_dict'])
            self.optimizer.load_state_dict(cp['optimizer_state_dict'])
            self.lr_scheduler.load_state_dict(cp['scheduler_state_dict'])
            self.epoch_start = cp['epoch'] + 1
            self.metrics = cp['metrics']
            self.best_state = cp['best_state']
        else:
            self.metrics = []
            self.epoch_start = 1
            self.best_state = None

        return PATH

    def create_dataloaders(self, datafile):
        inputs, labels = load_diff_data(
            datafile, per_file=self.config['per_file'], dis=self.config['distill'])

        split = round(len(inputs)*self.config['split'])

        toolong = []

        for i, diff in tqdm(enumerate(inputs[split:])):
            tokens = self.tokenizer(
                diff, padding='max_length', truncation=False)
            length = sum(tokens['attention_mask'])
            if length > self.config['max_length']:
                toolong.append(i)

        def remove_outliers(inputs, labels):
            ri, rl = [], []

            for i in range(len(inputs)):
                if i not in toolong:
                    ri.append(inputs[i])
                    rl.append(labels[i])

            return ri, rl

        if self.config['rmo']:
            print(f'Remvoing {len(toolong)} datapoint outliers...')
            inputs, labels = remove_outliers(inputs, labels)

        train_inputs = inputs[:split]
        train_labels = labels[:split]
        valid_inputs = inputs[split:]
        valid_labels = labels[split:]

        raw_datasets = DatasetDict({
            'train': Dataset.from_dict({
                'inputs': train_inputs,
                'labels': [categories.index(c) for c in train_labels]
            }),
            'valid': Dataset.from_dict({
                'inputs': valid_inputs,
                'labels': [categories.index(c) for c in valid_labels]
            })
        })

        def tokenize_function(examples):
            return self.tokenizer(examples["inputs"], padding='max_length', max_length=self.config['max_length'], truncation=True)

        tokenized_datasets = raw_datasets.map(tokenize_function, batched=True)
        tokenized_datasets = tokenized_datasets.remove_columns(["inputs"])
        tokenized_datasets.set_format("torch")

        train_dataloader = DataLoader(
            tokenized_datasets["train"].shuffle(seed=self.config['seed']), shuffle=True, batch_size=self.config['batch_size'])
        eval_dataloader = DataLoader(
            tokenized_datasets["valid"].shuffle(seed=self.config['seed']), batch_size=self.config['batch_size'])

        return train_dataloader, eval_dataloader

    def train(self):
        device = torch.device("cuda")
        self.model.to(device)
        self.model.train()

        for epoch in range(self.epoch_start, self.config['num_epochs'] + 1):
            print(f"Starting epoch {epoch}/{self.config['num_epochs']}")

            train_acc = load_metric('accuracy')
            train_f1 = load_metric('f1')
            val_acc = load_metric('accuracy')
            val_f1 = load_metric('f1')
            start_time = time.time()
            train_loss = 0
            val_loss = 0

            # Training loop
            for batch in tqdm(self.train_dataloader):
                batch = {k: v.to(device) for k, v in batch.items()}
                outputs = self.model(**batch)
                loss = outputs.loss
                train_loss += loss.item()
                loss.backward()

                self.optimizer.step()
                self.lr_scheduler.step()
                self.optimizer.zero_grad()

                # Training metrics
                logits = outputs.logits
                labels = batch['labels']
                preds = torch.argmax(logits, dim=-1)
                train_acc.add_batch(predictions=preds, references=labels)
                train_f1.add_batch(predictions=preds, references=labels)

            # Validation metrics
            with torch.no_grad():
                for batch in self.eval_dataloader:
                    batch = {k: v.to(device) for k, v in batch.items()}
                    outputs = self.model(**batch)
                    val_loss += outputs.loss.item()
                    logits = outputs.logits
                    labels = batch['labels']
                    preds = torch.argmax(logits, dim=-1)
                    val_acc.add_batch(predictions=preds, references=labels)
                    val_f1.add_batch(predictions=preds, references=labels)

                train_acc = train_acc.compute()
                train_f1 = train_f1.compute(average='macro')
                val_acc = val_acc.compute()
                val_f1 = val_f1.compute(average='macro')

                vpoint = {
                    'train_acc': train_acc,
                    'train_f1': train_f1,
                    'train_loss': train_loss / len(self.train_dataloader),
                    'val_acc': val_acc,
                    'val_f1': val_f1,
                    'val_loss': val_loss / len(self.eval_dataloader)
                }

                self.metrics.append(vpoint)

            print(
                f'train_loss: {vpoint["train_loss"]:.3f}, val_loss: {vpoint["val_loss"]:.3f}')

            print(
                f"Epoch time: {((time.time() - start_time) / 60):.3f} minutes")

            curr_state = {
                **vpoint,
                'model_state_dict': self.model.state_dict()
            }

            if not self.best_state or self.best_state['val_loss'] > curr_state['val_loss']:
                self.best_state = curr_state

            torch.save({
                'base': self.checkpoint,
                'epoch': epoch,
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'scheduler_state_dict': self.lr_scheduler.state_dict(),
                'best_state': self.best_state,
                'metrics': self.metrics,
                'max_length': self.config['max_length']
            }, self.PATH)

        print(f"{self.config['num_epochs']}/{self.config['num_epochs']} done")
