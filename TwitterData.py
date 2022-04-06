import tweepy
from textblob import TextBlob
from wordcloud import WordCloud
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

consumerKey = 'HFQ4Q2lpgyv8MxP4iQF5icimc'
consumerSecret = 'tmt5wTAiHEQXvjpDcd0Ph1KrH4Lg9fxjT5pHn0rz6PA0blsBkK'
accessToken = '1509962661844307969-QtjrQDIUSZT0NO1ZOf7iKXa1phViF1'
accessTokenSecret = 'gmjt6v6rNqIwJ97HYul6gutPcMw8u9J4Zan9De9o7G0Pg'

authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
authenticate.set_access_token(accessToken, accessTokenSecret)

api = tweepy.API(authenticate, wait_on_rate_limit = True)

data = []
columns = ['User', 'Tweets']

posts = tweepy.Cursor(api.search_tweets,
                      q="Duragesic OR Fentanyl OR Hydrocodone OR Hydros OR Oxy OR Oxycodone OR Oxycotin OR Oxycotton OR Vicodin OR Vikes OR Oxycontin",
                      tweet_mode="extended").items(200)

for tweet in posts:
    data.append([tweet.user.screen_name, tweet.full_text])

df = pd.DataFrame(data, columns=columns)
print("***Keyword Search***", df)


def cleanText(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'RT[\s]+', '', text)
    text = re.sub(r'https?:\/\/\S+', '', text)

    return text


df['Tweets'] = df['Tweets'].apply(cleanText)
print("***Cleaned Tweets***", df)


def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity

def getPolarity(text):
    return TextBlob(text).sentiment.polarity

df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
df['Polarity'] = df['Tweets'].apply(getPolarity)

print("******Subjectivity and Polarity******", np)


#Show plot
allWords = ' '.join([twts for twts in df['Tweets']])
wordCloud = WordCloud(width = 500, height = 300, random_state = 21, max_font_size = 119).generate(allWords)

plt.imshow(wordCloud, interpolation = "bilinear")
plt.axis('off')
plt.show()




#Analysis

def getAnalysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


df['Analysis'] = df['Polarity'].apply(getAnalysis)
print("********Analysis**********",df)




#Print positive tweets

print("*********Positive Tweets*********")
j = 1
sortedDF = df.sort_values(by=['Polarity'])
for i in range(0, sortedDF.shape[0]):
    if (sortedDF['Analysis'][i] == 'Positive'):
        print(str(j) + ') ' +sortedDF['Tweets'][i])
        print()
        j += 1



#Print Negative tweets

print("*************Negative Tweets*************")
j = 1
sortedDF = df.sort_values(by=['Polarity'])
for i in range(0, sortedDF.shape[0]):
    if (sortedDF['Analysis'][i] == 'Negative'):
        print(str(j) + ') ' +sortedDF['Tweets'][i])
        print()
        j += 1





#Plot Polarity

plt.figure(figsize=(8, 6))
for i in range(0, df.shape[0]):
    plt.scatter(df['Polarity'][i], df['Subjectivity'][i], color='Blue')

plt.title('Sentiment Analysis')
plt.xlabel('Polarity')
plt.ylabel('Subjectivity')



#positive tweets percentage
ptweets = df[df.Analysis == 'Positive']
ptweets = ptweets['Tweets']

round((ptweets.shape[0] / df.shape[0]) * 100, 1)


#negative tweets percentage
ntweets = df[df.Analysis == 'Negative']
ntweets = ntweets['Tweets']

round((ntweets.shape[0] / df.shape[0] * 100), 1)



#plot
df['Analysis'].value_counts()

plt.title('Sentiment Analysis')
plt.xlabel('Sentiment')
plt.ylabel('Count')
df['Analysis'].value_counts().plot(kind='bar')
plt.show()