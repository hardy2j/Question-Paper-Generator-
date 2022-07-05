import pandas as pd
import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from gensim import parsing
from joblib import dump, load
from gensim.corpora import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.matutils import sparse2full
import gensim
import nltk
import string
import re
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn import metrics
from nltk.stem import WordNetLemmatizer
import pickle
import spacy
from tfvectorizer import TfidfVectorizer
from sklearn.model_selection import train_test_split
nltk.download('wordnet')
nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()
f = open("dataset/dataset.txt", encoding="mbcs")
text_data = f.read()
text_data = text_data.split('â€¢')
text_data = text_data[1:]

questions = []
labels = []
for i in range(len(text_data)):
    temp = text_data[i].split('\n')
    for j in range(1, len(temp)):
        if(temp[j] != ''):
            questions.append(temp[j])
            labels.append(temp[0])

stopwords = ['a', 'the', 'is', 'an', 'of', 'at']

cleaned_questions = []
for i in range(0, len(questions)):
    review = re.sub('[^a-zA-Z]', ' ', questions[i])
    review = review.lower()
    review = review.split()
    review = [lemmatizer.lemmatize(word)
              for word in review if not word in set(stopwords)]
    review = ' '.join(review)
    cleaned_questions.append(review)


tf_idf = TfidfVectorizer()

question_tf = tf_idf.fit_transform(cleaned_questions)
X_train,X_test,y_train,y_test= train_test_split(question_tf,labels,test_size=0.10)

svm_classifier = SVC()
svm_classifier.fit(X_train, y_train)

y_pred2 = svm_classifier.predict(X_test)
c = 0
for i in range(len(y_pred2)):
    if(y_pred2[i] == y_test[i]):
        c = c+1
print("Accuracy for test data:-", ((c/len(y_pred2))*100))

y_pred3 = svm_classifier.predict(X_train)
c = 0
for i in range(len(y_pred3)):
    if(y_pred3[i] == y_train[i]):
        c = c+1
print("Accuracy for train data:-", ((c/len(y_pred3))*100))

filename = 'finalized_model.sav'
print("Saving the model for SVM")
pickle.dump(svm_classifier, open(filename, 'wb'))
print("Model saved")


filename2 = 'finalized_model2.sav'
print("Saving the model for TFIDF")
pickle.dump(tf_idf, open(filename2, 'wb'))
print("Model saved")

