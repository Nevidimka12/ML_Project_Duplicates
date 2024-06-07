import pickle
import nltk
from nltk.corpus import stopwords
import re
from nltk.stem.porter import *
import joblib

with open('random_forest_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

vectorizer = joblib.load('vectorizer.pkl')


def predict(data, f):
    prediction = loaded_model.predict(data)
    if (f or prediction[0]):
        return "Duplicate"
    else:
        return "Not duplicate"


def preprocess_text(text):
    text = re.sub(r"[^\w\s]", '', text.lower())
    return text.split()


def delete_stop_words(text):
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    return ' '.join([word for word in preprocess_text(text) if word not in stop_words])


def preprocess_stem(text):
    stemmer = PorterStemmer()
    return ' '.join([stemmer.stem(word) for word in text.split()])


def prepare_data(s1, s2):
    s1 = delete_stop_words(s1)
    s2 = delete_stop_words(s2)

    s1 = preprocess_stem(s1)
    s2 = preprocess_stem(s2)

    s1_bow = vectorizer.transform([s1])
    s2_bow = vectorizer.transform([s2])

    data_features = s1_bow + s2_bow

    if s1 == s2:
        return [data_features, 1]
    else:
        return [data_features, 0]

