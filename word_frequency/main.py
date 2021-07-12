from secret import twitterAuthentication
from collections import Counter
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tweepy
import re

twitterAPI = tweepy.API(twitterAuthentication())

def removeMentionAndURL(text):
        # Remove the mentions (@SpaceX, @Twitter, etc)
        # Match '@' & at least any one character except \s & ends with \s or symbols or end of string
        text = re.sub(r"\s*@[^\s]+(\s|\W|$)", "", text)
        # Remove any URLS (google.com, www.google.com, https://docs.github.com
        # Match optional http/https & any subdomain & any domain names with ending (ends w/ space or symbols or end of string)
        text = re.sub(r"\s*((http|https):\/\/)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)(\s|\W|$)",
                      "", text)
        # Replace any punctuation with space to help .split() better later
        text = re.sub(r"[^\w\s]", " ", text)
        return text 

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

def countWords(name, tweets):
        allWords = []
        for tweet in tweets:
                cleaned = removeMentionAndURL(tweet.full_text.lower())
                allWords.extend(cleaned.split())
        return Counter(allWords) # returns collections object

def removeStopwords(counterObj):
        wordList = list(counterObj.keys())
        for word in wordList:
                if word in stopwords.words():
                        counterObj.pop(word)
        # no need to return, object reference stays
        
def graphTweetLengths(user):
        displayName, allTweets = getAllTweets(user)
        earliestTweet = allTweets[-1].created_at.strftime("%b. %Y")
        latestTweet = allTweets[0].created_at.strftime("%b. %Y")
        
        averageLength = {}
        
        for tweet in allTweets:
                # Filter out retweeted tweets -- it'll mess with the data
                # Ex: user with 20 avg. words retweets a tweet that has 60 words
                try:
                        tweet.retweeted_status # if this is valid, it means it's retweeted
                except AttributeError: # retweeted_status isn't an attribute, so it's not retweeted       
                        tweetYearMonth = tweet.created_at.date().replace(day=1)
                        tweetText = removeMentionAndURL(tweet.full_text)
                        if (tweetYearMonth not in averageLength):
                                # create dictionary for assignment
                                averageLength[tweetYearMonth] = {"characters" : len(tweetText), \
                                                                  "words" : len(tweetText.split()), \
                                                                  "tweets" : 1}
                        else:
                                averageLength[tweetYearMonth]["characters"] += len(tweetText)
                                averageLength[tweetYearMonth]["words"] += len(tweetText.split())
                                averageLength[tweetYearMonth]["tweets"] += 1

        # Average the metrics & delete tweet count (not needed anymore)
        for month in averageLength:
                averageLength[month]["characters"] /= averageLength[month]["tweets"]
                averageLength[month]["words"] /= averageLength[month]["tweets"]
                del averageLength[month]["tweets"]
        
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

graphTweetLengths(input("Twitter username average lengths to graph: "))
