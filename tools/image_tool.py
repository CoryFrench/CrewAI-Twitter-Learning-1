from openai import OpenAI
from langchain.tools import tool

client = OpenAI(api_key="########################################")

class Image_Tool():
    @tool("Image Tool")
    def generate_image(prompt):
        "Tool to create AI Generated Images from ChatGPT via a prompt passed into the tool."
        response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        )
        image_url = response.data[0].url
        return image_url