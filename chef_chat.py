import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

st.title("Chef Chat (2 ⭐ Michelin Experience)")

def generate_content(prompt):
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                'role':'system',
                'content':'''
                You are a 2 michelin star chef who wants to help home cooks improve their cooking skills.
                You may only answer home cooking related questions.
                If they ask about any nonsense outside of cooking, SCOLD AND CURSE THEM!
                '''
            },
            {
                'role':'user',
                'content':prompt
            }
        ],
        n= 1,
        max_tokens= 1000,
    )
    
    return response.choices[0].message.content

#Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role":"system",
            "content":"How may I help you?"

        }
    ]

#Display chat message from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#Process and store prompt and response
def ai_function(prompt):
    response = generate_content(prompt)

    #Display the Assistant Message
    with st.chat_message("Assistant"):
        st.markdown(response)

    #Storing User Message
    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        }
    )

    #Storing Assistant Message
    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":response
        }
    )

#Accept user input
prompt = st.chat_input("Ask me anything!")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    ai_function(prompt)