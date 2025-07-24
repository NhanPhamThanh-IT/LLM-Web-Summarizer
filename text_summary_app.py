import requests
from bs4 import BeautifulSoup
import ollama

MODEL = 'llama3.2'

class Website:
    url: str
    title: str
    text: str

    def __init__(self, url: str):
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else 'No title found'
        for irrelevant in soup(['script', 'style', 'img', 'input']):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator='\n', strip=True)

system_prompt = "You are an assistant that analyzes the content of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

def user_prompt_for(website: Website) -> str:
    user_prompt = f"You are looking at a website titled '{website.title}'."
    user_prompt += "The contents of the website is as follows; \
    please provide a short summary of this website in markdown. \
    If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

def messages_for(website: Website) -> list:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

def summarize(url: str) -> str:
    website = Website(url)
    messages = messages_for(website)
    response = ollama.chat(model=MODEL, messages=messages)
    return response['message']['content']

# Streamlit app
import streamlit as st

st.title("Website Summary App")
st.markdown(
    "Enter a URL to summarize the content of the website."
)

url = st.text_input("Enter a URL:", "")

if st.button("Summarize"):
    if url:
        with st.spinner("Summarizing..."):
            summary = summarize(url)
        st.markdown(summary)
    else:
        st.error("Please enter a valid URL.")