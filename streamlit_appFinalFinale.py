import streamlit as st
import os
from docx import Document
from docx.shared import Inches
import io
from PIL import Image
import requests
import replicate

def generate_llama2_response(prompt_input):
    # Setting up parameters for the model
    temperature = 0.7
    top_p = 0.95
    max_length = 800
    repetition_penalty = 1
    
    # Detailed prompt for the model
    string_dialogue = ("You are a digital marketing and SEO expert. Your task is to write an article on the topic: "
                       f"'{prompt_input}'. The article must be under 800 words and should be lengthy.")
    
    output = replicate.run(
        'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
        input={"prompt": string_dialogue, "temperature": temperature, "top_p": top_p, 
               "max_length": max_length, "repetition_penalty": repetition_penalty}
    )
    
    # Extracting the content from the output
    return output.get('content', "") if isinstance(output, dict) else output

# Remaining functions (get_src_original_url, save_image_from_url, create_word_docx) remain unchanged

def main():
    # ... (main function remains largely unchanged)

    with col1:
        st.subheader("Generated Content by Llama 2")
        result = ""  # Initialize the result variable
        
        try:
            result = generate_llama2_response(user_input)
            if result:
                st.info("Your article has been been generated successfully!")
                st.write(result)
            else:
                st.error("Your article couldn't be generated or is empty!")
        except Exception as e:
            st.error(f"An error occurred while generating the article: {e}")

    # ... (rest of the main function)

if __name__ == "__main__":
    main()
