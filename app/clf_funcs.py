import nltk
from nltk.corpus import stopwords

from sklearn.base import BaseEstimator, TransformerMixin



# Needed for vectorizer later
def dummy(doc):
    return doc

# Remove stopwords and punctuation
def remove_stopwords_doc(doc):
    # load stopwords and
    stop_words = set(stopwords.words("english"))
    words = [w for w in doc if (w not in stop_words) & (w.isalpha())]
    return words

# Lemmatise a tokenised sentence
def lemmatize_sent(sent):
    lemmatizer = nltk.WordNetLemmatizer()
    sent_out = [lemmatizer.lemmatize(w) for w in sent]
    return sent_out

def tokenize_doc(doc):
    '''For each doc:
    - sentence tokenize
    - word tokenize
    - remove stopwords
    - lemmatize each word
    - add n_grams'''
    
    # Tidy up doc
    doc = doc.lower()               # Lower case the whole doc
    doc = doc.replace('\n',' ')     # Replace line breaks with spaces for tokenisation with weird formatting
    
    # Might eventually add n-grams in this loop
    sents_list = nltk.sent_tokenize(doc)                               # Sentence tokenise the document (into list of sentences)
    sents_list = [nltk.word_tokenize(sent) for sent in sents_list]          # Word tokenize each sentence
    sents_list = [remove_stopwords_doc(sent) for sent in sents_list]        # Remove stopwords from each sentence
    sents_list = [lemmatize_sent(sent) for sent in sents_list]              # Lemmatize each sentence
    words_to_remove = ['scientist', 'science', 'analyst', 'analysis', 'engineer'] # Hardcoded words to remove
    sents_list = [[w for w in sent if w not in words_to_remove] for sent in sents_list] # Remove unwanted words
    ngrams_list = [nltk.ngrams(sent,2) for sent in sents_list]
    
    # Flatten lists
    sent_expanded = [word for sent in sents_list for word in sent]          # [item for sublist in sents_list for item in sublist]
    ngrams_expanded = [gram for sent in ngrams_list for gram in sent]       # Same for ngrams_list
    ngrams_expanded = [' '.join(gram) for gram in ngrams_expanded]          # Convert ngram tuples to string token
    tokens_list = sent_expanded + ngrams_expanded                          # Join into one long list

    return tokens_list


class TextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self):
        return
        
    def fit(self, X, y=None): # the fit method does nothing
        return self  
    
    def transform(self, X):
        X = [tokenize_doc(doc) for doc in X]
        return X