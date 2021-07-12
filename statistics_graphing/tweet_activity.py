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

def graphTweetActivity(user):
        displayName, allTweets = getAllTweets(user)
        earliestTweet = allTweets[-1].created_at.strftime("%b. %Y")
        latestTweet = allTweets[0].created_at.strftime("%b. %Y")
        
        tweetCount = {}
        for tweet in allTweets:
                # change all to day 1 for monthly graphing
                tweetYearMonth = tweet.created_at.date().replace(day=1)
                if (tweetYearMonth not in tweetCount):
                        tweetCount[tweetYearMonth] = 1
                else:
                        tweetCount[tweetYearMonth] += 1
                        
        with plt.style.context('ggplot'):
                fig, ax = plt.subplots(figsize=(9, 5))
                ax.set_xlabel(f"Date ({earliestTweet} - {latestTweet})")
                ax.set_ylabel("Tweets Per Month")
                ax.set_title(f"{displayName}'s ({user}) Tweet Activity")
                
                plt.bar(tweetCount.keys(), tweetCount.values(), width=25, edgecolor="white")

                # Title & rotate and align the tick labels
                fig.canvas.set_window_title(f"{displayName}'s Tweet Activity")
                fig.autofmt_xdate()
                # Formats x-axis points to be (Jan. 2021)
                fmt = mdates.DateFormatter('%b. %Y') 
                plt.gca().xaxis.set_major_formatter(fmt)

                plt.show()

graphTweetActivity(input("Twitter username activity to graph: "))
