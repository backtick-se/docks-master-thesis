from utils import categories
from sklearn.metrics import confusion_matrix, classification_report
from transformers import AutoModelForSequenceClassification as AMFSC, AutoTokenizer, logging
import matplotlib.pyplot as plt
import numpy as np
import torch

class Evaluator:
	def __init__(self, path):
		logging.set_verbosity_error()
		cp = torch.load(path, map_location=torch.device('cpu'))

		self.max_length = cp['max_length']
		self.metrics = cp['metrics']
		self.base = cp['base']
		
		self.tokenizer = AutoTokenizer.from_pretrained(self.base)

		self.model = AMFSC.from_pretrained(self.base, num_labels=len(categories))
		self.model.load_state_dict(cp['best_state']['model_state_dict'])
		self.model.eval()

		self.taccs = [*map(lambda e: e['train_acc']['accuracy'], self.metrics)]
		self.vaccs = [*map(lambda e: e['val_acc']['accuracy'], self.metrics)]
		self.tloss = [*map(lambda e: e['train_loss'], self.metrics)]
		self.vloss = [*map(lambda e: e['val_loss'], self.metrics)]
		self.tfone = [*map(lambda e: e['train_f1']['f1'], self.metrics)]
		self.vfone = [*map(lambda e: e['val_f1']['f1'], self.metrics)]
	
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
	
	def compare(self, other):
		pass

	def plot_progress(self):
		fig, ax = plt.subplots(3, sharex=True)
		fig.suptitle('Model Training Progress')

		fig.set_figheight(10)
		fig.set_figwidth(10)

		x = range(1, len(self.metrics) + 1)

		## Stackoverflow magic ##
		xmin = x[np.argmin(self.vloss)]
		ymin = min(self.vloss)
		text = f'Best model (loss: {ymin:.3f})'
		bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
		arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=60")
		kw = dict(xycoords='data',textcoords="axes fraction", arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
		ax[0].annotate(text, xy=(xmin, ymin), xytext=(0.94,0.96), **kw)
		###########################

		ax[0].plot(x, self.tloss, 'bo-')
		ax[0].plot(x, self.vloss, 'go-')
		ax[0].set_ylabel('Loss')

		ax[1].plot(x, self.taccs, 'bo-', label='Training')
		ax[1].plot(x, self.vaccs, 'go-', label='Validation')
		ax[1].set_ylabel('Accuracy')

		ax[2].plot(x, self.tfone, 'bo-')
		ax[2].plot(x, self.vfone, 'go-')
		ax[2].set_ylabel('Macro F1')

		fig.legend()
		plt.xlabel('Epoch')
		plt.xticks(x)
		plt.show()

def eval(y_true, y_pred):
    print(classification_report(y_true, y_pred, labels=categories))
    print(confusion_matrix(y_true, y_pred, labels=categories))

def load_trained(path):
	
	
	cp = torch.load(path, map_location=torch.device('cpu'))
	max_length = cp['max_length']
	base = cp['base']

	model = AMFSC.from_pretrained(base, num_labels=len(categories))
	tokenizer = AutoTokenizer.from_pretrained(base)

	best_state = cp['best_state']

	model.load_state_dict(best_state['model_state_dict'])
	metrics = cp['metrics']

	model.eval()

	def predict(text):
		inputs = tokenizer(text, padding='max_length', truncation=True, max_length=max_length, return_tensors="pt")
		outputs = model(**inputs)
		logits = outputs.logits
		pred = torch.argmax(logits, dim=-1)
		return categories[pred]

	def compare(other):
		cp = torch.load(path, map_location=torch.device('cpu'))
		other_metrics = cp['metrics']



	def plot_progress():
		taccs = [*map(lambda e: e['train_acc']['accuracy'], metrics)]
		vaccs = [*map(lambda e: e['val_acc']['accuracy'], metrics)]
		tloss = [*map(lambda e: e['train_loss'], metrics)]
		vloss = [*map(lambda e: e['val_loss'], metrics)]
		tfone = [*map(lambda e: e['train_f1']['f1'], metrics)]
		vfone = [*map(lambda e: e['val_f1']['f1'], metrics)]

		fig, ax = plt.subplots(3, sharex=True)
		fig.suptitle('Model Training Progress')

		fig.set_figheight(10)
		fig.set_figwidth(10)

		x = range(1, len(metrics) + 1)

		## Stackoverflow magic ##
		xmin = x[np.argmin(vloss)]
		ymin = min(vloss)
		text = f'Best model (loss: {ymin:.3f})'
		bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
		arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=60")
		kw = dict(xycoords='data',textcoords="axes fraction", arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
		ax[0].annotate(text, xy=(xmin, ymin), xytext=(0.94,0.96), **kw)
		###########################

		ax[0].plot(x, tloss, 'bo-')
		ax[0].plot(x, vloss, 'go-')
		ax[0].set_ylabel('Loss')

		ax[1].plot(x, taccs, 'bo-', label='Training')
		ax[1].plot(x, vaccs, 'go-', label='Validation')
		ax[1].set_ylabel('Accuracy')

		ax[2].plot(x, tfone, 'bo-')
		ax[2].plot(x, vfone, 'go-')
		ax[2].set_ylabel('Macro F1')

		fig.legend()
		plt.xlabel('Epoch')
		plt.xticks(x)
		plt.show()
	
	return predict, plot_progress
