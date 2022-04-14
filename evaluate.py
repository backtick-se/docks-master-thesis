from utils import categories
from sklearn.metrics import confusion_matrix, classification_report
from transformers import AutoModelForSequenceClassification as AMFSC, AutoTokenizer, logging
import matplotlib.pyplot as plt
import numpy as np
import torch

def eval(y_true, y_pred):
    print(classification_report(y_true, y_pred, labels=categories))
    print(confusion_matrix(y_true, y_pred, labels=categories))

def get_figax(num_metrics):
	num_rows = round(num_metrics / 2)
	rc = lambda i: int(f'{str(num_rows)}2{i}')
	fig = plt.figure()
	ax = [fig.add_subplot(rc(i+1)) for i in range(num_metrics)]
	return fig, ax

class Evaluator:
	fig_width = 15
	fig_height = 8

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
		num_metrics = len(self.metrics)
		fig, ax = get_figax(num_metrics)

		#fig, ax = plt.subplots(len(self.metrics), sharex=True)
		fig.suptitle(f'Model Training Progress: {self.file}')

		fig.set_figheight(self.fig_height)
		fig.set_figwidth(self.fig_width)

		x = range(1, self.epochs + 1)

		def annotate_best(ax, ys, text, maximize=True):
			geti, gety = (np.argmax, max) if maximize else (np.argmin, min)
			tx = x[geti(ys)]
			ty = gety(ys)
			text = text(ty)
			## Stackoverflow magic ##
			bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
			arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=90")
			kw = dict(xycoords='data',textcoords="axes fraction", arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
			ax.annotate(text, xy=(tx, ty), xytext=(0.9,0.9 + - 0.8*int(maximize)), **kw)
			###########################
		
		annotate_best(
			ax[0],
			self.metrics['loss']['valid'],
			lambda y: f"Best loss: {y:.3f}",
			maximize=False
		)

		annotate_best(
			ax[1],
			self.metrics['accuracy']['valid'],
			lambda y: f"Best accuracy: {y:.3f}"
		)

		annotate_best(
			ax[2],
			self.metrics['f1']['valid'],
			lambda y: f"Best f2¨1: {y:.3f}"
		)

		for i, (metric, splits) in enumerate(self.metrics.items()):
			for split, values in splits.items():
				if i == 0:
					ax[i].plot(x, values, '-o', markersize=3, label=split)
				else:
					ax[i].plot(x, values, '-o', markersize=3)
			
			ax[i].set_ylabel(metric)

		ax[1].set_ylim([0, 1])
		ax[2].set_ylim([0, 1])

		fig.legend(loc='center', bbox_to_anchor=(0.75, 0.3))
		plt.xlabel('Epoch')
		plt.xticks(x)
		plt.show()
	
	@staticmethod
	def compare(*models):
		
		evaluators = [Evaluator(m) if type(m) != Evaluator else m for m in models]

		num_metrics = 3
		fig, ax = get_figax(num_metrics)

		#fig, ax = plt.subplots(3, sharex=True)
		fig.set_figheight(Evaluator.fig_height)
		fig.set_figwidth(Evaluator.fig_width)
		fig.suptitle(f'Model Comparison: Validation set results')

		l = min([*map(lambda ev: ev.epochs, evaluators)])
		x = range(1, l + 1)

		for ev in evaluators:
			ax[0].plot(x, ev.metrics['loss']['valid'][:l], '-o', markersize=3, label=ev.file)
			ax[1].plot(x, ev.metrics['accuracy']['valid'][:l], '-o', markersize=3)
			ax[2].plot(x, ev.metrics['f1']['valid'][:l], '-o', markersize=3)
			
		ax[0].set_ylabel('Loss')
		ax[1].set_ylabel('Accuracy')
		ax[2].set_ylabel('Macro F1')
		ax[1].set_ylim([0, 1])
		ax[2].set_ylim([0, 1])

		fig.legend(loc='center', bbox_to_anchor=(0.75, 0.3))
		plt.xlabel('Epoch')
		plt.xticks(x)
		plt.show()
