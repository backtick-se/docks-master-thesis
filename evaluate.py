from utils import categories
from sklearn.metrics import confusion_matrix, classification_report
from transformers import AutoModelForSequenceClassification as AMFSC, AutoTokenizer, logging
import matplotlib.pyplot as plt
import numpy as np
import torch

def eval(y_true, y_pred):
    print(classification_report(y_true, y_pred, labels=categories))
    print(confusion_matrix(y_true, y_pred, labels=categories))

class Evaluator:
	fig_width = 15
	fig_height = 15

	def __init__(self, path):
		logging.set_verbosity_error()
		cp = torch.load(path, map_location=torch.device('cpu'))
		self.file = path.split('/')[-1]

		self.base = cp['base']
		self.epochs = cp['epoch']
		self.max_length = cp['max_length']
		
		self.tokenizer = AutoTokenizer.from_pretrained(self.base)

		self.model = AMFSC.from_pretrained(self.base, num_labels=len(categories))
		self.model.load_state_dict(cp['best_state']['model_state_dict'])
		self.model.eval()

		metrics = cp['metrics']

		self.metrics = {
			'loss': {
				'train': [*map(lambda e: e['train_loss'], metrics)],
				'valid': [*map(lambda e: e['val_loss'], metrics)]
			},
			'accuracy': {
				'train': [*map(lambda e: e['train_acc']['accuracy'], metrics)],
				'valid': [*map(lambda e: e['val_acc']['accuracy'], metrics)]
			},
			'f1': {
				'train': [*map(lambda e: e['train_f1']['f1'], metrics)],
				'valid': [*map(lambda e: e['val_f1']['f1'], metrics)]
			}
		}
	
	def predict(self, input):
		inputs = self.tokenizer(
			input,
			padding='max_length',
			truncation=True,
			max_length=self.max_length,
			return_tensors="pt"
		)
		outputs = self.model(**inputs)
		logits = outputs.logits
		pred = torch.argmax(logits, dim=-1)
		return categories[pred]

	def plot_progress(self):
		fig, ax = plt.subplots(len(self.metrics), sharex=True)
		fig.suptitle(f'Model Training Progress: {self.file}')

		fig.set_figheight(self.fig_height)
		fig.set_figwidth(self.fig_width)

		x = range(1, self.epochs + 1)

		## Stackoverflow magic ##
		xmin = x[np.argmin(self.metrics['loss']['valid'])]
		ymin = min(self.metrics['loss']['valid'])
		text = f'Best model (loss: {ymin:.3f})'
		bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
		arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=60")
		kw = dict(xycoords='data',textcoords="axes fraction", arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
		ax[0].annotate(text, xy=(xmin, ymin), xytext=(0.94,0.96), **kw)
		###########################

		for i, (metric, splits) in enumerate(self.metrics.items()):
			for split, values in splits.items():
				if i == 0:
					ax[i].plot(x, values, '-o', markersize=3, label=split)
				else:
					ax[i].plot(x, values, '-o', markersize=3)
			
			ax[i].set_ylabel(metric)

		fig.legend()
		plt.xlabel('Epoch')
		plt.xticks(x)
		plt.show()
	
	@staticmethod
	def compare(*models):
		
		evaluators = [Evaluator(m) if type(m) != Evaluator else m for m in models]

		fig, ax = plt.subplots(3, sharex=True)
		fig.set_figheight(Evaluator.fig_height)
		fig.set_figwidth(Evaluator.fig_width)

		l = min([*map(lambda ev: ev.epochs, evaluators)])
		x = range(1, l + 1)

		for ev in evaluators:
			ax[0].plot(x, ev.metrics['loss']['valid'][:l], '-o', markersize=3, label=ev.file)
			ax[1].plot(x, ev.metrics['accuracy']['valid'][:l], '-o', markersize=3)
			ax[2].plot(x, ev.metrics['f1']['valid'][:l], '-o', markersize=3)

		ax[0].set_ylabel('Loss')
		ax[1].set_ylabel('Accuracy')
		ax[2].set_ylabel('Macro F1')

		fig.legend()
		plt.xlabel('Epoch')
		plt.xticks(x)
		plt.show()
