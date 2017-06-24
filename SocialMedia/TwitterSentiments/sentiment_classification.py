from pattern.web import Twitter  
from pattern.en import tag  
from pattern.vector import KNN, count

twitter, knn = Twitter(), KNN()

for i in range(1, 3):
    for tweet in twitter.search('#trump OR #obama', start=i, count=100):
        s = tweet.text.lower()
        p = 'A' if '#obama' in s else 'B'
        v = tag(s)
        v = [word for word, pos in v if pos == 'JJ'] # JJ = adjective
        v = count(v) # {'sweet': 1}
        if v:
            knn.train(v, type=p)

print knn.classify('hope')
print knn.classify('good')
print knn.classify('bad')


