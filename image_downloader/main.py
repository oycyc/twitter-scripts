# https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/extended-entities
from secret import twitterAuthentication
import tweepy
import datetime
import wget # download files
import os
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
        return mediaTweets

def filterTweets(allTweets, starting=None, ending=None):
        if (starting is not None) and (ending is not None):
                previousLen = len(allTweets)
                allTweets = [tweet for tweet in allTweets \
                             if (tweet.created_at >= starting) and (tweet.created_at <= ending)]
                print(f"Removed {previousLen - len(allTweets)} tweets outside the timeframe.")
        
        filtered = []
        noMedia = 0
        for tweet in allTweets:
                try: # If there's an image, there's an "extended_entities" attribute,
                     # if there isn't, then it throws an error.
                        media = tweet.extended_entities
                        filtered.append(tweet)
                except:
                        noMedia += 1
                        
        print(f"Catched {len(filtered)} media tweets.")
        print(f"{str(noMedia)} tweets had no media attached.\n\n")
        return filtered

# Only downloads the images from the media tweet -- if there's a video/gif, it only downloads the thumbnail.
def downloadMediaThumbnails(mediaTweets, outputFolder=None):
        if outputFolder is None:
                outputFolder = username
        checkFolder(outputFolder) # If folder doesn't exist, create a new folder.

        downloadedCount = 0
        for mediaTweet in mediaTweets:
                media = mediaTweet.extended_entities["media"]     
                try:
                        # Use range() to write (i) in filename in case there are multiple media per tweet.
                        for i in range(len(media)):
                                outputFile = f"{outputFolder}/{mediaTweet.created_at.strftime('%Y-%m-%d--%H.%M')} {username}({i})({mediaTweet.id}).jpg"
                                if not os.path.exists(outputFile): # Make sure picture didn't already exist.
                                        wget.download(media[i]["media_url"], out=outputFile)
                                        downloadedCount += 1
                                printStatusFreq = int(len(mediaTweets) / 20 + 0.5) # Every 5% of the total mediaTweets, it will print the status. 0.5 for rounding.
                                if (downloadedCount % printStatusFreq == 0):
                                        print("Currently downloaded: " + str(downloadedCount))
                except Exception as e:
                        print("Error saving tweet, ID: " + mediaTweet.id_str)
                        print(e)
                        
        print(f"Total downloaded media: {str(downloadedCount)}.")

# Downloads all the medias in one folder, including videos and gifs.
def downloadMediaAll(mediaTweets, outputFolder=None):
        if outputFolder is None:
                outputFolder = username
        checkFolder(outputFolder)

        downloadedCount = {"photos": 0, "videos": 0, "gifs": 0}
        for mediaTweet in mediaTweets:
                media = mediaTweet.extended_entities["media"]
                try:
                        # Use range() to write (i) in filename in case there are multiple media per tweet.
                        for i in range(len(media)):
                                if (media[i]["type"] == "photo"):  
                                        outputFile = f"{outputFolder}/{mediaTweet.created_at.strftime('%Y-%m-%d--%H.%M')} {username}({i})({mediaTweet.id_str}).jpg"
                                        if not os.path.exists(outputFile): # Make sure media didn't already exist.
                                                wget.download(media[i]["media_url"], out=outputFile)
                                                downloadedCount["photos"] += 1
                                elif (media[i]["type"] == "video"):
                                        outputFile = f"{outputFolder}/{mediaTweet.created_at.strftime('%Y-%m-%d--%H.%M')} {username}({i})({mediaTweet.id_str}).mp4"
                                        if not os.path.exists(outputFile): # Make sure media didn't already exist.
                                                wget.download(media[i]["video_info"]["variants"][0]["url"], out=outputFile)
                                                downloadedCount["videos"] += 1
                                elif (media[i]["type"] == "animated_gif"):
                                        outputFile = f"{outputFolder}/{mediaTweet.created_at.strftime('%Y-%m-%d--%H.%M')} {username}(gif)({i})({mediaTweet.id_str}).mp4"
                                        if not os.path.exists(outputFile): # Make sure media didn't already exist.
                                                wget.download(media[i]["video_info"]["variants"][0]["url"], out=outputFile)
                                                downloadedCount["gifs"] += 1
                                else:
                                        print("Error with media type, ID: " + mediaTweet.id_str)
                                        
                                printStatusFreq = int(len(mediaTweets) / 10 + 0.5) # Every 10% of the total mediaTweets, it will print the status. 0.5 for rounding.
                                totalDownloads = sum(downloadedCount.values())
                                if (totalDownloads % printStatusFreq == 0):
                                        print("Currently downloaded: " + str(totalDownloads))
                except Exception as e:
                        print("Error saving tweet, ID: " + mediaTweet.id_str)
                        print(e)

        print(f"Total downloaded media: {str(totalDownloads)}\n{str(downloadedCount['photos'])} photos, {str(downloadedCount['videos'])} videos, and {str(downloadedCount['gifs'])} gifs.")

# Downloads all the media but saves them into three separate folders.
def downloadMediaSeparate(mediaTweets, outputFolder=None):
        if outputFolder is None:
                outputFolder = username
        checkFolder(outputFolder + "/photos")
        checkFolder(outputFolder + "/videos")
        checkFolder(outputFolder + "/gifs")

        downloadedCount = {"photos": 0, "videos": 0, "gifs": 0}
        for mediaTweet in mediaTweets:
                media = mediaTweet.extended_entities["media"]
                try:
                        # Use range() to write (i) in filename in case there are multiple media per tweet.
                        for i in range(len(media)):
                                if (media[i]["type"] == "photo"):  
                                        outputFile = f"{outputFolder}/photos/{mediaTweet.created_at.strftime('%Y-%m-%d--%H.%M')} {username}({i})({mediaTweet.id_str}).jpg"
                                        if not os.path.exists(outputFile): # Make sure media didn't already exist.
                                                wget.download(media[i]["media_url"], out=outputFile)
                                                downloadedCount["photos"] += 1
                                elif (media[i]["type"] == "video"):
                                        outputFile = f"{outputFolder}/videos/{mediaTweet.created_at.strftime('%Y-%m-%d--%H.%M')} {username}({i})({mediaTweet.id_str}).mp4"
                                        if not os.path.exists(outputFile): # Make sure media didn't already exist.
                                                wget.download(media[i]["video_info"]["variants"][0]["url"], out=outputFile)
                                                downloadedCount["videos"] += 1
                                elif (media[i]["type"] == "animated_gif"):
                                        outputFile = f"{outputFolder}/gifs/{mediaTweet.created_at.strftime('%Y-%m-%d--%H.%M')} {username}(gif)({i})({mediaTweet.id_str}).mp4"
                                        if not os.path.exists(outputFile): # Make sure media didn't already exist.
                                                wget.download(media[i]["video_info"]["variants"][0]["url"], out=outputFile)
                                                downloadedCount["gifs"] += 1
                                else:
                                        print("Error with media type, ID: " + mediaTweet.id_str)
                                        
                                printStatusFreq = int(len(mediaTweets) / 20 + 0.5) # Every 5% of the total mediaTweets, it will print the status. 0.5 for rounding.
                                totalDownloads = sum(downloadedCount.values())
                                if (totalDownloads % printStatusFreq == 0):
                                        print("Currently downloaded: " + str(totalDownloads))
                except Exception as e:
                        print("Error saving tweet, ID: " + mediaTweet.id_str)
                        print(e)

        print(f"Total downloaded media: {str(totalDownloads)}\n{str(downloadedCount['photos'])} photos, {str(downloadedCount['videos'])} videos, and {str(downloadedCount['gifs'])} gifs.")

def checkFolder(folderName):
        if not os.path.isdir(folderName):
                os.makedirs(folderName)

def datetimeInput():
        message = input("\nFilter by timeframe? ('yes' or 'no'): ")
        if message == "yes":
                startTime = input("Enter starting date in YYYY-MM-DD format: ")
                endTime = input("Enter ending date in YYYY-MM-DD format: ")
                startYear, startMonth, startDay = map(int, startTime.split("-"))
                endYear, endMonth, endDay = map(int, endTime.split("-"))
                return datetime.datetime(startYear, startMonth, startDay),\
                       datetime.datetime(endYear, endMonth, endDay)
        else:
                return None, None

def inputs():
        global username
        username = input("Twitter username to scrape: ")
        downloadFormat = int(input("""
1.) Only pictures (thumbnails for vids/gifs) all in one folder.
2.) All media files (gifs are downloaded as .mp4), all in one folder.
3.) All media files (gifs are downloaded as .mp4), organized in folders by media type.
Download media files in (enter #): """))
        startTimeframe, endTimeframe = datetimeInput()
        catchedTweets = getAllTweets(username)
        filteredTweets = filterTweets(catchedTweets, startTimeframe, endTimeframe)
        if (downloadFormat == 1):
                downloadMediaThumbnails(filteredTweets)
        elif (downloadFormat == 2):
                downloadMediaAll(filteredTweets)
        elif (downloadFormat == 3):
                downloadMediaSeparate(filteredTweets)

def run(twitterUsername, downloadFormat, startTime=None, endTime=None, outputFolder=None):
        global username
        username = twitterUsername
        catchedTweets = getAllTweets(username)
        filteredTweets = filterTweets(catchedTweets, startTime, endTime)
        if (downloadFormat == 1):
                downloadMediaThumbnails(filteredTweets, outputFolder)
        elif (downloadFormat == 2):
                downloadMediaAll(filteredTweets, outputFolder)
        elif (downloadFormat == 3):
                downloadMediaSeparate(filteredTweets, outputFolder)
inputs()

## Use program using inputs(). It will ask for the corresponding values OR:     
## Use program by using run(username, downloadFormat), with optional parameters of startTime, endTime, and outputFolder
## username is the Twitter username, downloadFormat options are 1, 2, 3: 1 downloads all media thumbnails (gifs/videos downloads picture), 2 downloads all media (including gifs as .mp4), and 3 downloads all media separated by folder indicating media type
## startTime and endTime has to be a datetime object, and it will only download tweets from the timeframe given
## outputFolder is the folder where all the media will be downloaded -- this is optional, if none specified, it will download to a folder with the username as the name
## Note: The Twitter API v1 (used in this program) only supports 3200 of the latest tweets of an account's timeline, so if a user tweeted more than 3200 times, it will only download the latest 3200 tweets.
                
## How it works:
## First it gets all of the tweets from an account's timeline using getAllTweets(username).
## Then it filters the tweet for only media tweets using filterTweets(allTweets), with optional parameters of start and end time (has to be in datetime object) if you want a timeframe to download the media.
## Lastly, it will download all the media using the filtered tweets by either downloadMediaThumbnails(mediaTweets), downloadMediaAll(mediaTweets), or downloadMediaSeparate(mediaTweets) with an optional parameter of outputFolder.
