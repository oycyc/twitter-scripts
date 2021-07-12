import tweepy

def twitterAuthentication():
    apiKey = ""
    apiSecretKey = ""
    accessToken = ""
    accessTokenSecret = ""
    auth = tweepy.OAuthHandler(apiKey, apiSecretKey)
    auth.set_access_token(accessToken, accessTokenSecret)
    return auth
