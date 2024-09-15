
#1.Importing

from openai import OpenAI
import streamlit as st
import dotenv

dotenv.load_dotenv()

client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

def story_gen(prompt):
  response = client.chat.completions.create(
      model = 'gpt-4o-mini',
      messages = [
          {'role':'system', 'content':'''You are a story teller.
          You have accomplished young adult short stories for 5 years.
          Given a topic, write a plot twist, heart breaking love stories with a closed ending. Do not involve moving out as a way to heartbreak.
          The story must be 150-200 words long.
          '''},
          {'role':'user', 'content':prompt}
      ],
      temperature = 1.0,
      max_tokens = 1000,
  )

  return response.choices[0].message.content

def cover_art(prompt):
  response = client.images.generate(
      model = 'dall-e-3',
      prompt = prompt,
      size = '1024x1024',
      quality = 'standard',
      n = 1,
      style = 'natural'
  )

  return response.data[0].url

def cover_prompt(prompt):
  response = client.chat.completions.create(
      model = 'gpt-4o-mini',
      messages = [
          {'role':'system', 'content':'''
          You are tasked with generating a prompt for a cover art.
          A story will be given and you have to analyse and digest the contents
          and extract the main elements or essence of the story. Write a short prompt to produce
          relevant cover art.
          '''},
          {'role':'user', 'content':prompt}
      ],
      temperature = 1.0,
      max_tokens = 1000,
  )

  return response.choices[0].message.content

def storybook(prompt):
  
  story = story_gen(prompt)
  cover = cover_prompt(story)
  image = cover_art(cover)
  st.image(image)
  st.caption(cover)
  st.divider()
  st.write(story)

prompt = st.text_input("Give me a topic for a storybook")
if st.button("Create Story"):
    storybook(prompt)

