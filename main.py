import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_csv("reviews.csv")

vectorizer = TfidfVectorizer(
    stop_words="english"
)

X = vectorizer.fit_transform(df["review"])

words = vectorizer.get_feature_names_out()

print(X.shape)
print(words[100:])