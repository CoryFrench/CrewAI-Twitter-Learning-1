import os
import requests
import tweepy
from langchain.tools import tool

# Authentication credentials
API_KEY = "########################################"
API_SECRET_KEY = "########################################"
ACCESS_TOKEN = "########################################"
ACCESS_TOKEN_SECRET = "########################################"


auth = tweepy.OAuth1UserHandler(
    API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)

client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

def download_file(source, target):
    if os.path.exists(target):
        os.remove(target)
    response = requests.get(source)
    if response.status_code == 200:
        with open(target, "wb") as file:
            file.write(response.content)
        print("Image downloaded successfully.")
        return True
    else:
        print("Failed to download image.")
        return False

class Twitter_Tool():
    @tool("Twitter Tool")
    def post_tweet(image_url, post_text):
        "Tool to upload provided image and text to a twitter post."
        TEMP_IMAGE_FILE_NAME = "tempfile.jpg"
        if download_file(image_url, TEMP_IMAGE_FILE_NAME):
            # Upload the image
            media = api.media_upload(TEMP_IMAGE_FILE_NAME)
            print(media)
            # Post Tweet with image
            tweet = client.create_tweet(text=post_text, media_ids=[media.media_id_string])
            print("Tweet successful.")