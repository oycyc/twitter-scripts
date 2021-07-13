from secret import twitterAuthentication
from collections import Counter
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tweepy
import re

twitterAPI = tweepy.API(twitterAuthentication())


def getAllTweets(user):
        mediaTweets = []
        # tweet_mode is set to "extended" because some tweets are truncated ("truncated": true), causing ["media"] to not be there
        fetchedTweets = twitterAPI.user_timeline(screen_name = user, count = 200, tweet_mode="extended")
        mediaTweets.extend(fetchedTweets)
        lastTweetInList = mediaTweets[-1].id - 1

        while (len(fetchedTweets) > 0):
                fetchedTweets = twitterAPI.user_timeline(screen_name = user, count = 200, max_id = lastTweetInList, tweet_mode="extended")
                mediaTweets.extend(fetchedTweets)
                lastTweetInList = mediaTweets[-1].id - 1
                print(f"Catched {len(mediaTweets)} tweets so far.")
        print("\n\n")
        return twitterAPI.get_user(user).name, mediaTweets

def countWords(tweets):
        allWords = []
        for tweet in tweets:
                # Filter out retweets -- it'll mess w/ the data
                try:
                        tweet.retweeted_status # if this is valid, it means it's a rt
                except AttributeError: # retweeted_status isn't an attribute, so not rt                  
                        cleaned = removeMentionAndURL(tweet.full_text.lower())
                        allWords.extend(cleaned.split())
                        
        return Counter(allWords) # returns collections object

def removeMentionAndURL(text):
        # Remove the mentions (@SpaceX, @Twitter, etc)
        # Match '@' & at least any one character except \s & ends with \s or symbols or end of string
        text = re.sub(r"\s*@[^\s]+(\s|\W|$)", "", text)
        # Remove any URLS (google.com, www.google.com, https://docs.github.com
        # Match optional http/https & any subdomain & any domain names with ending (ends w/ space or symbols or end of string)
        text = re.sub(r"\s*((http|https):\/\/)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)(\s|\W|$)",
                      "", text)
        # Replace any punctuation with space to help .split() better later
        text = re.sub(r"(\s+\W)|(\W\s+)|(\W$)", " ", text)
        return text

def removeStopwords(counterObj):
        wordList = list(counterObj.keys())
        for word in wordList:
                if word in stopwords.words():
                        counterObj.pop(word)
        # no need to return, object reference stays

def barChart(dataset1, dataset2, info):
        with plt.style.context('ggplot'):
                fig, ax = plt.subplots(1, 2, figsize=(11, 6))
                fig.canvas.set_window_title(f"{info['name']}'s Word Frequency")
                fig.suptitle(f"{info['name']}'s ({info['username']}) Word Frequency\n({info['earliest']} to {info['latest']})")
                
                ax[0].barh(list(dataset1.keys()), list(dataset1.values()))
                ax[0].set_xlabel("Frequency")
                ax[0].set_ylabel("Words")
                ax[0].set_title("No Stopwords")
                ax[0].legend(["count"])

                ax[1].barh(list(dataset2.keys()), list(dataset2.values()), color="purple")
                ax[1].set_xlabel("Frequency")
                ax[1].set_title("With Stopwords")
                ax[1].legend(["count"])
                        
                plt.show()
## add more white space between the two charts
## optimize stopwords.words()


def graphFrequency(user):
        username, allTweets = getAllTweets(user)
        latestTweet = allTweets[0].created_at.strftime("%b. %Y")
        earliestTweet = allTweets[-1].created_at.strftime("%b. %Y")
        countedWords = countWords(allTweets)
        
        mostCommonWithStopwords = dict(countedWords.most_common(15))
        # remove stopwords from original
        removeStopwords(countedWords)
        mostCommon = dict(countedWords.most_common(15))
        
        # reverse dictionaries into ascending order
        mostCommon = {k: v for k, v in sorted(mostCommon.items(), key=lambda item: item[1])}
        mostCommonWithStopwords = {k: v for k, v in sorted(mostCommonWithStopwords.items(), key=lambda item: item[1])}

        info = {"name": username, "username": user, "latest": latestTweet, "earliest": earliestTweet}
        barChart(mostCommon, mostCommonWithStopwords, info)
        

def graphTweetLengths(user):
        with plt.style.context('ggplot'):
                fig, ax = plt.subplots(2, figsize=(10, 6))    
                
                # List comprehension to return a list of only the "likes" average value
                ax[0].bar(averageLength.keys(), [value["characters"] for value in list(averageLength.values())],\
                        width=25, edgecolor="white")
                ax[0].set_ylabel("Monthly Length/Tweet")
                ax[0].set_title(f"{displayName}'s Average Tweet Length")

                # List comprehension to return a list of only the "retweets" average value
                ax[1].bar(averageLength.keys(), [value["words"] for value in list(averageLength.values())],\
                        width=25, edgecolor="white", color=(0, 0.247, 0.361))
                ax[1].set_xlabel(f"Date ({earliestTweet} - {latestTweet})")
                ax[1].set_ylabel("Monthly Words/Tweet")
                ax[1].set_title(f"{displayName}'s Average Word Count")

                # Title & rotate and align the tick labels
                fig.canvas.set_window_title(f"{displayName}'s ({user}) Tweet Lengths")
                fig.autofmt_xdate()
                
                # Formats x-axis points to be (Jan. 2021)
                fmt = mdates.DateFormatter('%b. %Y') 
                plt.gca().xaxis.set_major_formatter(fmt)

                plt.show()

asd = graphFrequency(input("Twitter username word frequency to chart: "))
