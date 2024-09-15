import streamlit as st

#set the app title
st.title("A Card For You")

#add text
st.write("Today is your day")

#adding a button
st.button("Reset", type="primary")  #primary state, default button
if st.button("HAPPY BIRTHDAY!"):
    st.write("Hope you have a great day")
    st.balloons()
    st.image("https://stordfkenticomedia.blob.core.windows.net/df-us/rms/media/recipesmedia/recipes/retail/x17/2003/sep/16714-birthday-cake-600x600.jpg?ext=.jpg")
else:
    st.write("Goodbye")

    