from utils import cloned
from extract import Extractor
from itertools import chain
from gensim.models import TfidfModel, LdaMulticore
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim.corpora import Dictionary
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
import nltk
import re

# Code from shorturl.at/cntDM

np.random.seed(2022)
nltk.download('wordnet')
nltk.download('omw-1.4')

def lem_stem(text):
    return SnowballStemmer('english').stem(
		WordNetLemmatizer().lemmatize(text, pos='v')
	)

def preprocess(text, min_len=3):
	return [
		lem_stem(token) for token in simple_preprocess(text)
		if token not in STOPWORDS and len(token) > min_len
	]

def train_lda_model(docs, num_topics, passes=2, alpha=1, tfidf=True, workers=2):
	processed_docs = [*map(preprocess, docs)]
	dictionary = Dictionary(processed_docs)
	dictionary.filter_extremes(no_below=1, no_above=0.9, keep_n=100000)
	bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

	corpus = TfidfModel(bow_corpus)[bow_corpus] if tfidf else bow_corpus

	lda_model = LdaMulticore(
		corpus,
		num_topics=num_topics,
		id2word=dictionary,
		passes=passes,
		workers=workers,
		alpha=alpha
	)

	for idx, topic in lda_model.print_topics(-1):
		print(f'Topic: {idx} \nWords: {topic}')
	
	return lda_model, dictionary, corpus

def predict(model, dictionary, doc):
	bow_vector = dictionary.doc2bow(preprocess(doc))

	return [
		(index, score)
		for index, score in
		sorted(model[bow_vector], key=lambda tup: -1*tup[1])
	]

def test_predict(model, dictionary, doc):
	topics = predict(model, dictionary, doc)

	for index, score in topics:
		print(f'Score: {score}\nTopic: {model.print_topic(index, 5)}')

def test(cwd):
	dwd = f'{cwd}/docs' # Docs directory

	paths, contents = Extractor('md').extract(dwd)

	# Remove title table
	pattern = r'(---\ntitle:.*\n---\n)'
	notitle = lambda c: ''.join(re.split(pattern, c)[2:])
	data = [*map(notitle, contents)]

	# Split on sections
	pattern = r'# .*\n'
	split = lambda d: re.split(pattern, d)
	sect_data = [*map(split, data)]

	# Find sentences?
	ptrn = r'[A-Z].*?[\.!?][\s]'
	pat = re.compile(ptrn, re.M)
	text_data = [''.join(pat.findall(par)) for page in sect_data for par in page]
	print(text_data[10])

	# Filter out duplicates
	set_data = []
	set_paths = []

	for path, page in zip(paths, data):
		if page not in set_data:
			set_data.append(page)
			set_paths.append(path)

	model, dictionary, corpus = train_lda_model(set_data, len(set_paths), alpha=0.1, passes=2)
	
	predicted = [predict(model, dictionary, page)[0] for page in set_data]

	for pred, path in zip(predicted, set_paths):	
		print(path, pred)

	pr = """
	User-wide Configuration & API Provider improvements
	Configuration
	Adds support for a user-wide configuration file, ~/.cowait.yml
	Clusters are now defined in the user-wide configuration.
	docker and kubernetes are available as default clusters.
	Renamed provider CLI argument to cluster.
	The default cluster can be overridden in the task context config by setting the cluster option.
	API Provider
	Improved error handling
	Includes an authentication token in the Cowait-Key header. This token is set in the cluster configuration.
	fix dask-notebook image name
	update dask notebook example
	buffer upstream messages when not connected
	set images for examples
	fix cluster args
	retry upstream connections
	update agent cli command to use cluster config
	api provider includes authentication tokens in requests
	add support for user-wide cluster configuration
	fix dashboard path
	"""

	pr_prediction = predict(model, dictionary, pr)
	print(pr_prediction)
	
	#print(pr_prediction, [*predicted.keys()][[*predicted.values()].index(pr_prediction[0][0])])

if __name__ == '__main__':
	cloned('git@github.com:backtick-se/cowait.git')(test)()