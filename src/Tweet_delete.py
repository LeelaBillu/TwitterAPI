from requests_oauthlib import OAuth1Session
import json
import sys
from settings import Settings
class DeleteTweet:
    def __init__(self):
        self.settings=Settings()
        self.api_key = self.settings.api_key  # Directly access the attribute
        self.api_secret_key = self.settings.api_secret_key
        self.oauth = None
    def fetching_request_token(self):
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        self.oauth = OAuth1Session(self.api_key, client_secret=self.api_secret_key)
        try:
            fetch_response = self.oauth.fetch_request_token(request_token_url)
        except ValueError:
            print("There may have been an issue with the API key or API secret key you entered.")
            sys.exit()
        return fetch_response.get("oauth_token"),fetch_response.get("oauth_token_secret")
    def authorize_users(self,resource_owner_key,resource_owner_secret):
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = self.oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize: %s" % authorization_url)

        # Get verification PIN from user
        verifier = input("Paste the PIN here: ")

        # Access token URL
        access_token_url = "https://api.twitter.com/oauth/access_token"
        self.oauth = OAuth1Session(
                                self.api_key,
                                client_secret=self.api_secret_key,
                                resource_owner_key=resource_owner_key,
                                resource_owner_secret=resource_owner_secret,
                                verifier=verifier,
                            )

        # Fetch access token
        return self.oauth.fetch_access_token(access_token_url)
    def delete_tweeet(self,tweet_id,access_token,access_token_secret):
        delete_url = f"https://api.twitter.com/2/tweets/{tweet_id}"
        self.oauth = OAuth1Session(
                                    self.api_key,
                                    client_secret=self.api_secret_key,
                                    resource_owner_key=access_token,
                                    resource_owner_secret=access_token_secret,
                                   )
        response = self.oauth.delete(delete_url)

        # Error handling
        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
                )
        return response.json().get("data")

def main():
    delete_tweet=DeleteTweet()
    tweet_id=input("Enter Tweet id to delete")
    resource_owner_key, resource_owner_secret = delete_tweet.fetching_request_token()
    print(f"Got OAuth token: {resource_owner_key}")
    oauth_tokens=delete_tweet.authorize_users(resource_owner_key, resource_owner_secret)
    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]
    json_response=delete_tweet.delete_tweeet(tweet_id,access_token,access_token_secret)
    print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__=="__main__":
    main()

