import streamlit as st

st.title("My First Streamlit App")
st.write("Hello, world! This is a simple data app.")

if st.button('Say hello'):
    st.write('Hello there!')