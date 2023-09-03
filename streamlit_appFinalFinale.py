import streamlit as st
import os
import replicate
from docx import Document
from docx.shared import Inches
import requests
from io import BytesIO

# Set the page config
st.set_page_config(
    page_title="AI Article Generator",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# This function will not be cached and retrieves the API token
def get_replicate_api():
    if 'REPLICATE_API_TOKEN' in st.secrets:
        return st.secrets['REPLICATE_API_TOKEN']
    else:
        return st.text_input('Enter Replicate API token:', type='password')

# This function will be cached and loads the LLM model
@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_llm(replicate_api):
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'

    return llm

# In the main function
def main():
    replicate_api = get_replicate_api()  # Get the API token
    llm_model = load_llm(replicate_api)  # Load the model with the token

    # ... rest of the code


# Function to generate the article
def generate_article(prompt_input, llm_model):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    string_dialogue += f"User: Write an article about {prompt_input}\n\n"
    response = replicate.run(llm_model, input={"prompt": f"{string_dialogue} Assistant: "})
    
    return response.get('content', "")

# Main function of the app
def main():
    st.title("AI Article Generator 🤖✍️")
    
    # Load the LLM model
    llm_model = load_llm()

    # Text input for the article topic
    topic = st.text_input("Enter the topic for the article:")

    # Generate article button
    if st.button("Generate Article"):
        with st.spinner("Generating article..."):
            article = generate_article(topic, llm_model)
            if article:
                st.subheader(f"Article on {topic}")
                st.write(article)
            else:
                st.error("An error occurred while generating the article.")
    
    # Download article as a Word document with an image
    if st.button("Download Article as Word Document"):
        try:
            # Create a new Word document
            doc = Document()
            doc.add_heading(f'Article on {topic}', level=1)

            # Add the generated article to the document
            doc.add_paragraph(article)

            # Add an image to the document
            image_url = "https://source.unsplash.com/1600x900/?nature,water"
            response = requests.get(image_url)
            image_stream = BytesIO(response.content)
            doc.add_picture(image_stream, width=Inches(6.0))

            # Save the document
            doc_path = "/mnt/data/article.docx"
            doc.save(doc_path)

            # Provide the document for download
            st.success(f"Article successfully saved as Word document!")
            st.markdown(f"[Click here to download](/mnt/data/article.docx)")

        except Exception as e:
            st.error(f"Couldn't generate the Word document. Error: {e}")

if __name__ == "__main__":
    main()
