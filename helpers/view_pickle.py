import pickle

with open("../known_words.pkl", "rb") as f:
    print(pickle.load(f))
