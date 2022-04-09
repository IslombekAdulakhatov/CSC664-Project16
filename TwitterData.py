import tweepy
import psycopg2
from textblob import TextBlob
from wordcloud import WordCloud
import pandas as pd
import numpy as np
from privatevars import *
import re
import matplotlib.pyplot as plt
import PySimpleGUI as sg
plt.style.use('fivethirtyeight')


authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
authenticate.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(authenticate, wait_on_rate_limit = True)

conn = None
cur = None

connection = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port = port_id
)

cursor = connection.cursor()

try:
    create_script = '''CREATE TABLE IF NOT EXISTS tweets( 
                                id SERIAL PRIMARY KEY,
                                tweet_id BIGINT NOT NULL, 
                                text VARCHAR NOT NULL, 
                                screen_name VARCHAR NOT NULL, 
                                author_id BIGINT 
                                )'''
    cursor.execute(create_script)

    posts = tweepy.Cursor(api.search_tweets,
                          q="Duragesic OR Fentanyl OR Hydrocodone OR Hydros OR Oxy OR Oxycodone OR Oxycotin OR Oxycotton OR Vicodin OR Vikes OR Oxycontin",
                          tweet_mode="extended").items(500)
    for tweet in posts:
        cursor.execute("SELECT id FROM tweets WHERE text = %s;", [tweet.full_text])
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO tweets (tweet_id, text, screen_name, author_id) VALUES (%s, %s, %s, %s);", (tweet.id, tweet.full_text, tweet.author.screen_name, tweet.author.id))
            connection.commit()
except Exception as error:
    print(error)
except UnicodeEncodeError:
    pass
finally:
    cursor.close()
    connection.close()


data = []
columns = ['User', 'Tweets']

posts = tweepy.Cursor(api.search_tweets,
                      q="Duragesic OR Fentanyl OR Hydrocodone OR Hydros OR Oxy OR Oxycodone OR Oxycotin OR Oxycotton OR Vicodin OR Vikes OR Oxycontin",
                      tweet_mode="extended").items(200)

for tweet in posts:
    data.append([tweet.user.screen_name, tweet.full_text])

df = pd.DataFrame(data, columns=columns)
print("***Keyword Search***", df)

headings1 = list(columns)
values1 = df.values.tolist()

def cleanText(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'RT[\s]+', '', text)
    text = re.sub(r'https?:\/\/\S+', '', text)

    return text


df['Tweets'] = df['Tweets'].apply(cleanText)
print("***Cleaned Tweets***", df)

headings2 = list(columns)
values2 = df.values.tolist()

def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity

def getPolarity(text):
    return TextBlob(text).sentiment.polarity

df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
df['Polarity'] = df['Tweets'].apply(getPolarity)

values3 = df.values.tolist()
print("******Subjectivity and Polarity******", df)


#Show plot
allWords = ' '.join([twts for twts in df['Tweets']])
wordCloud = WordCloud(width = 500, height = 300, random_state = 21, max_font_size = 119).generate(allWords)

plt.imshow(wordCloud, interpolation = "bilinear")
plt.axis('off')
#plt.show()




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

values4 = df.values.tolist()


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
#plt.show()


layout = [
    [sg.Text(text="Initial Retrieval"), sg.Text(text= "Polarity and Subjectivity", pad=(310,0))],
    [sg.Table(values=values1, headings= headings1, auto_size_columns=False, col_widths=[10, 30]), sg.VSeparator(),
     sg.Table(values=values3, headings= ["Users", "Tweets", "Subjectivity", "Polarity"], auto_size_columns=False, col_widths=[10, 30, 10, 10])],
    [sg.Text(text="Cleaned Tweets"), sg.Text(text= "Analysis", pad=(310,0))],
    [sg.Table(values=values2, headings= headings2, auto_size_columns=False, col_widths=[10, 30]), sg.VSeparator(),
     sg.Table(values=values4, headings= ["Users", "Tweets", "Subjectivity", "Polarity", "Analysis"], auto_size_columns=False, col_widths=[10, 30, 10, 10, 10])],

    [sg.Text(text = "Conclusion: In this sample of tweets, we found that " + str(round((ptweets.shape[0] / df.shape[0]) * 100, 1)) + "% of our tweets were positive. \n")],
    [sg.Text(text = "On the other hand, " + str(round((ntweets.shape[0] / df.shape[0] * 100), 1)) + "% of our tweets were negative. \n")],
    [sg.Text(text ="The final remaining " + str(round(100 - (ntweets.shape[0] / df.shape[0] * 100), 1) - round((ptweets.shape[0] / df.shape[0]) * 100, 1)) + "% was nuetral.")]
]
window = sg.Window("Data", layout)
event, values = window.read()