from secret import twitterAuthentication
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tweepy

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

def graphTweetMetrics(user):
        displayName, allTweets = getAllTweets(user)
        earliestTweet = allTweets[-1].created_at.strftime("%b. %Y")
        latestTweet = allTweets[0].created_at.strftime("%b. %Y")
        
        averageMetrics = {}
        
        for tweet in allTweets:
                # Filter out retweeted tweets -- it'll mess with the data
                # Ex: user with 20 avg. likes retweets a tweet that has 20k likes
                try:
                        tweet.retweeted_status # if this is valid, it means it's retweeted
                except AttributeError: # retweeted_status isn't an attribute, so it's not retweeted       
                        tweetYearMonth = tweet.created_at.date().replace(day=1)
                        if (tweetYearMonth not in averageMetrics):
                                # create dictionary to assign all metrics
                                averageMetrics[tweetYearMonth] = {"retweets" : tweet.retweet_count, \
                                                                  "likes" : tweet.favorite_count, \
                                                                  "tweets" : 1}
                        else:
                                averageMetrics[tweetYearMonth]["retweets"] += tweet.retweet_count
                                averageMetrics[tweetYearMonth]["likes"] += tweet.favorite_count
                                averageMetrics[tweetYearMonth]["tweets"] += 1

        # Average the metrics & delete tweet count (not needed anymore)
        for month in averageMetrics:
                averageMetrics[month]["retweets"] /= averageMetrics[month]["tweets"]
                averageMetrics[month]["likes"] /= averageMetrics[month]["tweets"]
                del averageMetrics[month]["tweets"]
        
        with plt.style.context('ggplot'):
                fig, ax = plt.subplots(2, figsize=(10, 6))    
                
                # List comprehension to return a list of only the "likes" average value
                ax[0].bar(averageMetrics.keys(), [value["likes"] for value in list(averageMetrics.values())],\
                        width=25, edgecolor="white")
                ax[0].set_ylabel("Average Monthly Likes")
                ax[0].set_title(f"{displayName}'s Average Likes")

                # List comprehension to return a list of only the "retweets" average value
                ax[1].bar(averageMetrics.keys(), [value["retweets"] for value in list(averageMetrics.values())],\
                        width=25, edgecolor="white", color=(0, 0.247, 0.361))
                ax[1].set_xlabel(f"Date ({earliestTweet} - {latestTweet})")
                ax[1].set_ylabel("Average Monthly Retweets")
                ax[1].set_title(f"{displayName}'s Average Retweets")

                # Title & rotate and align the tick labels
                fig.canvas.set_window_title(f"{displayName}'s ({user})Tweet Metrics")
                fig.autofmt_xdate()
                
                # Formats x-axis points to be (Jan. 2021)
                fmt = mdates.DateFormatter('%b. %Y') 
                plt.gca().xaxis.set_major_formatter(fmt)

                plt.show()

graphTweetMetrics(input("Twitter username metrics to graph: "))
