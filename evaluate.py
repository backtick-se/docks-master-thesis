from utils import categories
from sklearn.metrics import confusion_matrix, classification_report
from transformers import AutoModelForSequenceClassification, AutoTokenizer, logging
import matplotlib.pyplot as plt
import torch

def eval(y_true, y_pred):
    print(classification_report(y_true, y_pred, labels=categories))
    print(confusion_matrix(y_true, y_pred, labels=categories))

def load_trained(path):
	logging.set_verbosity_error()
	
	cp = torch.load(path, map_location=torch.device('cpu'))
	base = cp['base']

	model = AutoModelForSequenceClassification.from_pretrained(base, num_labels=len(categories))
	tokenizer = AutoTokenizer.from_pretrained(base)

	best_state = cp['best_state']

	model.load_state_dict(best_state['model_state_dict'])
	metrics = cp['metrics']

	model.eval()

	def predict(text):
		inputs = tokenizer(text, padding='max_length', truncation=True, return_tensors="pt")
		outputs = model(**inputs)
		logits = outputs.logits
		pred = torch.argmax(logits, dim=-1)
		return categories[pred]

	def plot_progress():
		taccs = [*map(lambda e: e['train_acc']['accuracy'], metrics)]
		vaccs = [*map(lambda e: e['val_acc']['accuracy'], metrics)]
		tloss = [*map(lambda e: e['train_loss'], metrics)]
		vloss = [*map(lambda e: e['val_loss'], metrics)]
		tfone = [*map(lambda e: e['train_f1']['f1'], metrics)]
		vfone = [*map(lambda e: e['val_f1']['f1'], metrics)]

		fig, ax = plt.subplots(3, sharex=True)
		fig.suptitle('Model Training Progress')

		x = range(1, len(metrics) + 1)

		fig.set_figheight(8)
		fig.set_figwidth(10)

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
