import re
from nltk.stem import WordNetLemmatizer
import pickle

test_question = input("Enter the question:-")
def main(test_question):
    filename='finalized_model.sav'
    svm_classifier = pickle.load(open(filename, 'rb'))

    filename2='finalized_model2.sav'
    tf_idf = pickle.load(open(filename2, 'rb'))

    lemmatizer = WordNetLemmatizer()

    stopwords = ['a', 'the', 'is', 'an', 'of', 'at']
    review = re.sub('[^a-zA-Z]', ' ', test_question)
    review = review.lower()
    review = review.split()
    review = [lemmatizer.lemmatize(word)
            for word in review if not word in set(stopwords)]
    review = ' '.join(review)
    cleaned_test_question=review
    cleaned_test_question_tf = tf_idf.transform([cleaned_test_question])
    return svm_classifier.predict(cleaned_test_question_tf)[0]
predicted_class=main(test_question)
print("The predicted class is:-",predicted_class)
