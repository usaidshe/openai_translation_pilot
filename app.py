import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI
import os

# Streamlit app title
st.title("PDF Translator")

# User password for page protection
def check_password():
    """Function to check user password to protect the page"""
    password = st.text_input("Enter Password", type="password")
    if password == st.secrets["password"]:
        return True
    else:
        st.error("Incorrect password")
        return False

if check_password():
    # File uploader to allow users to upload a PDF file
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    # Dropdown to select the language for translation
    language = st.text_input("Select language for translation", "Spanish")

    time_warning = "Please note: each page may take 5-10 seconds to translate"

    st.write(time_warning)

    # Button to start the translation process
    if uploaded_file and language:
        if st.button("Start"):
            # Open the uploaded PDF file using fitz (PyMuPDF)
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            num_pages = doc.page_count

            # Initialize OpenAI API
            OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
            client = OpenAI(api_key=OPENAI_API_KEY)

            # Loop through each page in the PDF
            total_pages = max(range(num_pages)) + 1 
            for page_num in range(num_pages):
                page = doc.load_page(page_num)  # Load the page using the page index
                text = page.get_text("text")  # Extract the text from the page

                # Display original text
                st.subheader(f"Page {page_num + 1} of {total_pages}")
                # st.text(text)

                # Call OpenAI API to translate the text using the provided format
                system_text = "You are an expert at translating languages. A user will provide a language and text. You will translate that text into the language provided."
                user_text = f"""
                # Instructions
                
                Translate the below text to: {language}
                
                # Text: 
                
                {text}
                """
                response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                    "role": "system",
                    "content": [
                        {
                        "type": "text",
                        "text": system_text
                        }
                    ]
                    },
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": user_text 
                        }
                    ]
                    },
                ],                
                max_tokens=4095,
                # stream=True,
                response_format={
                    "type": "text"
                }
                )
                # for chunk in response: 
                #     st.write(chunk.choices[0].delta.content)
                translated_text = response.choices[0].message.content
                st.text(translated_text)