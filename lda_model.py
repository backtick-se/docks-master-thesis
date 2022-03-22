from gensim.models import TfidfModel, LdaMulticore
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim.corpora import Dictionary
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
import nltk

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

def train_lda_model(docs, num_topics, tfidf=False, passes=2, workers=2):
	processed_docs = [*map(preprocess, docs)]
	dictionary = Dictionary(processed_docs)
	dictionary.filter_extremes(no_below=3, no_above=0.5, keep_n=100000)
	bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

	corpus = TfidfModel(bow_corpus)[bow_corpus] if tfidf else bow_corpus

	lda_model = LdaMulticore(
		corpus,
		num_topics=num_topics,
		id2word=dictionary,
		passes=passes,
		workers=workers
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

if __name__ == '__main__':
	from extract import Extractor
	from os import getcwd
	import subprocess
	import re

	url = 'git@github.com:backtick-se/cowait.git'
	quiet_flag = '&> /dev/null'

	name = re.search('.*\/(.*).git', url).group(1)
	cwd = f'{getcwd()}/{name}' 	# Repo directory
	dwd = f'{cwd}/docs' 		# Docs directory

	subprocess.run(f'git clone {url} {cwd} {quiet_flag}', shell=True)
	clean = lambda: subprocess.run(f'rm -rf {cwd}', shell=True)

	paths, contents = Extractor('md').extract(dwd)

	model, dictionary, corpus = train_lda_model(contents, 10)
	
	#test_predict(model, dictionary)

	#i=2
	#print(f'{contents[i]}\n{preprocess(contents[i])}')

	clean()