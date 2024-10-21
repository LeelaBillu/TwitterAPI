"""
this code conatins twitter Api 
"""
import json
import sys
import os
import csv
import logging
from requests_oauthlib import OAuth1Session
from settings import Settings
from database import TweetDetails, Session

# Configure logging
logging.basicConfig(
    filename='twitter_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger()

class Authorization:
    """
    This class handles authorization for the Twitter API.
    """
    def __init__(self):
        self.settings = Settings()
        self.api_key = self.settings.api_key
        self.api_secret_key = self.settings.api_secret_key
        self.oauth = None

    def fetching_request_token(self):
        """
        Fetch the request token for OAuth authorization.
        """
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"  # pylint: disable=line-too-long
        self.oauth = OAuth1Session(self.api_key, client_secret=self.api_secret_key)
        try:
            fetch_response = self.oauth.fetch_request_token(request_token_url)
            logger.info("Successfully fetched request token.")
        except ValueError:
            logger.error("Failed to fetch request token. Check API keys.")
            print("There may have been an issue with the API key or API secret key you entered.")
            sys.exit()
        return fetch_response.get("oauth_token"), fetch_response.get("oauth_token_secret")

    def authorize_users(self, resource_owner_key, resource_owner_secret):
        """
        Authorize the user and fetch access tokens.
        """
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = self.oauth.authorization_url(base_authorization_url)
        print(f"Please go here and authorize: {authorization_url}")

        verifier = input("Paste the PIN here: ")
        access_token_url = "https://api.twitter.com/oauth/access_token"
        self.oauth = OAuth1Session(
            self.api_key,
            client_secret=self.api_secret_key,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = self.oauth.fetch_access_token(access_token_url)
        logger.info("Successfully authorized user and fetched access tokens.")
        return oauth_tokens


class PostTweet:
    """
    This class handles posting tweets.
    """
    def __init__(self):
        self.authorization = Authorization()
        self.resource_owner_key, self.resource_owner_secret = self.authorization.fetching_request_token()      # pylint: disable=line-too-long
        oauth_tokens = self.authorization.authorize_users(self.resource_owner_key, self.resource_owner_secret)  # pylint: disable=line-too-long

        self.oauth = OAuth1Session(
            self.authorization.api_key,
            client_secret=self.authorization.api_secret_key,
            resource_owner_key=oauth_tokens["oauth_token"],
            resource_owner_secret=oauth_tokens["oauth_token_secret"],
        )

    def posting_tweet(self, payload):
        """
        Post a tweet with the given payload.
        """
        response = self.oauth.post("https://api.twitter.com/2/tweets", json=payload)
        if response.status_code != 201:
            logger.error("Failed to post tweet: %d %s", response.status_code, response.text)
            raise ValueError(f"Request returned an error: {response.status_code} {response.text}")
        logger.info("Tweet posted successfully.")
        return response.json()

    def storing_to_db(self, json_response):
        """
        Store the tweet details in the database.
        """
        tweet_id = json_response['data']['id']
        tweet_text = json_response['data']['text']
        edit_history = json_response['data']['edit_history_tweet_ids']
        session = Session()
        tweet_data = TweetDetails(id=tweet_id, text=tweet_text, edit_history_tweet_ids=edit_history)
        session.add(tweet_data)
        session.commit()
        logger.info("Tweet details stored in database.")


class DeleteTweet:
    """
    This class handles deleting tweets.
    """
    def __init__(self):
        self.authorization = Authorization()
        self.resource_owner_key, self.resource_owner_secret = self.authorization.fetching_request_token()      # pylint: disable=line-too-long
        oauth_tokens = self.authorization.authorize_users(self.resource_owner_key, self.resource_owner_secret) # pylint: disable=line-too-long

        self.oauth = OAuth1Session(
            self.authorization.api_key,
            client_secret=self.authorization.api_secret_key,
            resource_owner_key=oauth_tokens["oauth_token"],
            resource_owner_secret=oauth_tokens["oauth_token_secret"],
        )

    def delete_tweet(self, tweet_id):
        """
        Delete a tweet by its ID.
        """
        delete_url = f"https://api.twitter.com/2/tweets/{tweet_id}"
        response = self.oauth.delete(delete_url)
        if response.status_code != 200:
            logger.error("Failed to delete tweet:%d %s",response.status_code,response.text)
            raise ValueError(f"Request returned an error: {response.status_code} {response.text}")
        logger.info("Tweet deleted successfully.")
        return response.json()


class GetUser:
    """
    This class handles fetching user details.
    """
    def __init__(self):
        self.authorization = Authorization()
        self.resource_owner_key, self.resource_owner_secret = self.authorization.fetching_request_token()      # pylint: disable=line-too-long
        oauth_tokens = self.authorization.authorize_users(self.resource_owner_key, self.resource_owner_secret) # pylint: disable=line-too-long

        self.oauth = OAuth1Session(
            self.authorization.api_key,
            client_secret=self.authorization.api_secret_key,
            resource_owner_key=oauth_tokens["oauth_token"],
            resource_owner_secret=oauth_tokens["oauth_token_secret"],
        )

    def get_user_details(self, username):
        """
        Get user details by username.
        """
        fields = "created_at,location,description,public_metrics"
        url = f"https://api.twitter.com/2/users/by/username/{username}?user.fields={fields}"  # pylint: disable=line-too-long
        response = self.oauth.get(url)
        if response.status_code != 200:
            logger.error("Failed to post tweet: %d %s", response.status_code, response.text)
            raise RuntimeError(f"Request returned an error: {response.status_code} {response.text}")
        logger.info("User details retrieved successfully.")
        return response.json().get("data")

    def write_to_csv(self, user_data, csv_file_path):
        """
        Write user data to a CSV file.
        """
        file_exists = os.path.isfile(csv_file_path)
        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = user_data.keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(user_data)
            logger.info("User details written to CSV.")


def main():
    """
    Main function to run the menu interface.
    """
    while True:
        print("\nMenu:")
        print("1. Post a Tweet")
        print("2. Delete a Tweet")
        print("3. Get User Details")
        print("4. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            post_tweet = PostTweet()
            payload = {"text": input("Enter your tweet: ")}
            json_response = post_tweet.posting_tweet(payload)
            print("\nTweet posted successfully!")
            print(json.dumps(json_response, indent=4, sort_keys=True))
            post_tweet.storing_to_db(json_response)

        elif choice == '2':
            delete_tweet = DeleteTweet()
            tweet_id = input("Enter Tweet ID to delete: ")
            json_response = delete_tweet.delete_tweet(tweet_id)
            print("\nTweet deleted successfully!")
            print(json.dumps(json_response, indent=4, sort_keys=True))

        elif choice == '3':
            get_user = GetUser()
            username = input("Enter username: ")
            user_data = get_user.get_user_details(username)
            print(json.dumps(user_data, indent=4, sort_keys=True))
            get_user.write_to_csv(user_data, "Get_User_details.csv")
            print("User details written to Get_User_details.csv")

        elif choice == '4':
            print("Exiting...")
            logger.info("Exiting the application.")
            break

        else:
            print("Invalid choice, please try again.")
            logger.warning("Invalid menu choice made.")


if __name__ == "__main__":
    main()
