import os
import shutil
from crewai import Crew, Agent, Task
from crewai_tools import YoutubeVideoSearchTool
from textwrap import dedent
from tools.image_tool import Image_Tool
from tools.twitter_tool import Twitter_Tool

'''
The YouTube scraper was haivng a hard time realizing I wasn't passing in the same URL over and over for some reason. The fix was to remove the db
directory to flush it's memory prior to starting a new request. Otherwise it would think it already had the data locally and would just repeat the
content of the first target video after I last cleared the cache.
'''

if os.path.exists('db'): 
  shutil.rmtree('db')

os.environ["OPENAI_API_KEY"] = "########################################"
image_tool = Image_Tool().generate_image
twitter_tool = Twitter_Tool().post_tweet

# Define your agents with roles and goals
class TranscriptionCrew:
  def __init__(self, targetURL):
    self.targetURL=targetURL

  def run(self):
    youtube_tool = YoutubeVideoSearchTool(youtube_video_url=self.targetURL)
    transcriber = Agent(
      role='Video Transcriber',
      goal=f'Transcribe spoken words from provided YouTube video into text. You are allowed to listen to the audio multiple times to make sure every \
            word is correct and there are no words missing from the translation. Getting the text 100 percent correct is your most important goal. \
            after transcribing, pass the transcript to the Social Media Coordinator.',
      backstory="You are an expert transcriptionist hired to provide transcription of audio in YouTube videos. You know that the name 'Ashley Van Dijk' \
                is actually 'Ashli Van Dyke', and wouldn't spell it the wrong way.",
      verbose=True,
      allow_delegation=False,
      tools=[youtube_tool]
    )

    social_media_guru = Agent(
      role='Social Media Coordinator',
      goal=f"Recieve transcription from transcriber agent, and create a Twitter/X post limited to 280 characters summarizing the transcript and \
            highlighting key aspects from it. Make the post engaging and fun. After creating the post text \
            hand the post to the ChatGPT Graphic Prompt Designer to create art for the post. \
            The post should not contain the speakers name of 'Ashli Van Dyke'.",
      backstory='You are an English major with a knack for creating witty and informative social media posts for advertising.',
      verbose=True,
      allow_delegation=False,
    )

    graphic_designer = Agent(
      role='ChatGPT Graphic Prompt Designer',
      goal='Create Twitter post images to go along with the post text provided by the Social Media Coordinator. Then, forward the Twitter post text \
            and the URL from the OpenAI api to the Twitter Account Manager',
      backstory='You are a GPT prompt creator with an expertise in creating prompts to generate clever and colorful social media digit \
                 vector-styleart via the OpenAI API',
      verbose=True,
      allow_delegation=False,
      tools=[image_tool]
    )

    twitter_poster = Agent(
      role='Twitter Account Manager',
      goal='To take the compiled data from the rest of the team and post the final product on Twitter/X using the twitter_tool. The ChatGPT Graphic \
            Prompt Designer will provide you with the post text and the image URL to feed into the twitter_tool.',
      backstory='You are someone who knows how to upload to Twitter and can follow directions without modifying any of the provided data.',
      verbose=True,
      allow_delegation=False,
      tools=[twitter_tool]
    )

    # Create tasks for the agents
    transcription_task = Task(
        description=f'Transcribe Video from provided URL without missing any words The url is {self.targetURL}',
        expected_output='Transcription in text form of the speech from within the YouTube video link provided',
        agent=transcriber
    )

    social_media_task = Task(
        description=f'Create social media post summarizing video transcript. Include the URL, which is {self.targetURL}',
        expected_output='280 character twitter post text summarizing the provided video transcript that is fun and informative',
        agent=social_media_guru
    )

    graphic_design_task = Task(
        description='Create a ChatGPT prompt which will generate graphics to be posted along with the social media text provided by the Social Media Coordinator. \
                     Pass the prompt into the image_tool which will then return a URL to the image. The created art should be simple and suitable for Twitter, \
                     that would look at home in a tutorial or informative setting, that is not too messy and is easily understandable. \
                     The generated prompt can not contain specifics about the Eclipse software, as OpenAI does not know what it is, so terms will have \
                     to be general, capturing the basic theme of the details without including specifics about the software. Also, do not include any \
                     reference to the 24/7 technical support, as that is a general concept that will appear in every video.',
        expected_output='URL returned from image_tool to be posted alongside the Twitter post text',
        agent=graphic_designer
    )

    posting_task = Task(
      description='Take the post text and the generated image URL and upload them to Twitter using the twitter_tool.',
      expected_output='The final result from this task should be a post on Twitter/X that contains the post text and graphic provided by the rest of the team.',
      agent=twitter_poster
    )

    # Instantiate your crew with a sequential process
    TranscriptionCrew = Crew(
      agents=[transcriber, social_media_guru, graphic_designer, twitter_poster],
      tasks=[transcription_task, social_media_task, graphic_design_task, posting_task],
      verbose=2, # You can set it to 1 or 2 to different logging levels
    )

    TranscriptionCrew.kickoff()

if __name__ == "__main__":
  print("## Welcome to Twitter Post Generator")
  print('-------------------------------')

  targetURL = input(
    dedent("""
      What is the URL you want to summarize?
    """))
  
  transcription_crew = TranscriptionCrew(targetURL)
  result = transcription_crew.run()
  print("\n\n########################")
  print("## Here is the Result")
  print("########################\n")
  print(result)