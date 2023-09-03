import streamlit as st
import os
from docx import Document
from docx.shared import Inches
import io
import requests
import replicate
from io import BytesIO

# This function will not be cached and retrieves the API token
def get_replicate_api():
    if 'REPLICATE_API_TOKEN' in st.secrets:
        return st.secrets['REPLICATE_API_TOKEN']
    else:
        return st.text_input('Enter Replicate API token:', type='password')

# This function will be cached and loads the LLM model
#@st.cache(allow_output_mutation=True, suppress_st_warning=True)
@st.cache_data
def load_llm(replicate_api, selected_model):
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'

    return llm


# Fetch image from Pexels based on user input
def get_image_url(query):
    url = 'https://api.pexels.com/v1/search'
    headers = {
        'Authorization': st.secrets["PEXELS_API_KEY"],
    }
    params = {
        'query': query,
        'per_page': 1,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        photos = data.get('photos', [])
        if photos:
            return photos[0]['src']['original']
    return None

# Function to generate the article
def generate_article(prompt_input, llm_model):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    string_dialogue += f"User: Write an article about {prompt_input}\n\n"
    generator_output = replicate.run(llm_model, input={"prompt": f"{string_dialogue} Assistant: "})
    response = next(generator_output, {})
    return response.get('content', "") if isinstance(response, dict) else response




# Main function of the app
def main():
    replicate_api = get_replicate_api()  # Get the API token

    # Get the selected model using st.selectbox
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    
    llm_model = load_llm(replicate_api, selected_model)  # Load the model with the token and selected model
    article = ""

    # Text input for the article topic and image
    topic = st.text_input("Enter the topic for the article:")
    image_topic = st.text_input("Enter the topic for the image:")

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
            image_url = get_image_url(image_topic)
            if image_url:
                response = requests.get(image_url)
                image_stream = BytesIO(response.content)

                # Create a new Word document
                doc = Document()
                doc.add_heading(f'Article on {topic}', level=1)

                # Add the generated article to the document
                doc.add_paragraph(article)

                # Add the fetched image to the document
                doc.add_picture(image_stream, width=Inches(6.0))

                # Save the document
                doc_path = "/mnt/data/article.docx"
                doc.save(doc_path)

                # Provide the document for download
                st.success(f"Article successfully saved as Word document!")
                st.markdown(f"[Click here to download](sandbox:/mnt/data/article.docx)")

            else:
                st.error("Couldn't fetch the image for the given topic.")

        except Exception as e:
            st.error(f"Couldn't generate the Word document. Error: {e}")

if __name__ == "__main__":
    main()
