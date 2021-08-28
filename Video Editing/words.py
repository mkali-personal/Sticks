import numpy as np

WORDS_NUMBER = 347222
VECTOR_LENGTH = 100

dataset = np.fromfile(r"C:\Users\mkali\Downloads\words_vectors-pos.npy")
with open(r"C:\Users\mkali\Downloads\words_list-pos.txt", encoding="utf-8") as words_file:
    words = words_file.readlines()
dataset = dataset[:-10].reshape(WORDS_NUMBER, VECTOR_LENGTH)

# %%



TORAH_INDEX = 1232

BIBLE_INDEX = 91085

x = dataset[TORAH_INDEX,:]
y = dataset[BIBLE_INDEX,:]
z = dataset[535,:]

print(x @ y.T)
print(x @ z.T)
print(y @ z.T)



close_words: np.ndarray = dataset @ x.T
close_words = close_words.argsort()
indexes = close_words[-10:]

for index in indexes:
    print(words[index])

print(words[TORAH_INDEX])

