import os
import io
import shutil

import numpy as np

import pytesseract
from PIL import Image, ImageOps
import cv2
from pdf2image import convert_from_path
import re

import streamlit as st


# CSS Styling
css = """
<style>
[data-testid="stToolbar"] {
    visibility: hidden;
}
</style>
"""

st.markdown(
    css,
    unsafe_allow_html=True
)


# Instantiate Streamlit app
st.title("Image to Text Converter")
st.title("Created by Yue Hang")
uploaded_files = st.file_uploader("Upload an image that contains text", type=("png", "jpg", "jpeg", "pdf"), accept_multiple_files=True)

# Path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

# # Find the Tesseract executable
# tesseract_path = shutil.which("tesseract")
# if tesseract_path is not None:
#     pytesseract.pytesseract.tesseract_cmd = tesseract_path
# else:
#     raise EnvironmentError("Tesseract not found. Please ensure it is installed and in your PATH.")


# Preprocess the input image
def image_preprocessor(loaded_image):
    """ 
    Process the input image by converting it into gray scale.
    1. Input image file name
    """
    try:
        # Convert the image into grey scale
        gray_image = ImageOps.grayscale(loaded_image)
    
        # Convert the the image into Numpy array so that we can process it with cv2 median blur later
        gray_image_np = np.array(gray_image)
    
        # # Remove noise
        # denoised = cv2.medianBlur(gray_image_np, 3)
    
        # # Convert the grayscale image to black and white
        # bw_image = gray_image.point(lambda x: 0 if x < 128 else 255, '1')
    
        return gray_image
    except Exception as e:
        st.error(f"Error in image preprocessing: {e}")
        return None


def convert_png_to_jpg(loaded_image):
    jpg_image = loaded_image.convert("RGB")
    return jpg_image


for file in uploaded_files:
    try:
        file_extension = re.findall(r"\.([a-z]+)$", file.name)[0]
    
        if file_extension == "pdf":
            # Save the uploaded PDF to a temporary file
            with open("temp.pdf", "wb") as f:
                f.write(file.getbuffer())
    
            # Convert PDF to images
            images = convert_from_path("temp.pdf")
    
            for i, image in enumerate(images):
                # Preprocess the input image
                processed_image = image_preprocessor(image)
    
                # Perform image to text conversion
                text = pytesseract.image_to_string(processed_image)
    
                # Display the extracted text
                st.write(f"Extracted Text from Page {i + 1}:")
                st.write(text)
                
                # Save the extracted text to a file
                text_file = io.BytesIO(text.encode('utf-8'))
                text_file_name = f"{file.name}_extracted_text.txt"
    
                # Provide a download link for the text file
                st.download_button(
                    label=f"Download Extracted Text from Page {i + 1}",
                    data=text_file.getvalue(),
                    file_name=text_file_name,
                    mime="text/plain"
                )
        
        elif file_extension == "png":
            # Load the uploaded image
            image = Image.open(file)

            # Convert the image from PNG to JPG
            jpg_image = convert_png_to_jpg(image)
    
            # Preprocess the input image
            processed_image = image_preprocessor(jpg_image)
    
            # Perform image to text conversion
            text = pytesseract.image_to_string(processed_image)
    
            # Display the extracted text
            st.write("Extracted Text:")
            st.write(text)
            
            # Save the extracted text to a file
            text_file = io.BytesIO(text.encode('utf-8'))
            text_file_name = f"{file.name}_extracted_text.txt"
    
            # Provide a download link for the text file
            st.download_button(
                label="Download Extracted Text",
                data=text_file.getvalue(),
                file_name=text_file_name,
                mime="text/plain"
            )
        
        elif file_extension in ["jpg", "jpeg"]:
            # Load the uploaded image
            image = Image.open(file)
    
            # Preprocess the input image
            processed_image = image_preprocessor(image)
    
            # Perform image to text conversion
            text = pytesseract.image_to_string(processed_image)
    
            # Display the extracted text
            st.write("Extracted Text:")
            st.write(text)
            
            # Save the extracted text to a file
            text_file = io.BytesIO(text.encode('utf-8'))
            text_file_name = f"{file.name}_extracted_text.txt"
    
            # Provide a download link for the text file
            st.download_button(
                label="Download Extracted Text",
                data=text_file.getvalue(),
                file_name=text_file_name,
                mime="text/plain"
            )
    
        else:
            st.error("The input file format is invalid. It should be in PDF, PNG, JPG, or JPEG instead!")
    
    except Exception as e:
        st.error(f"Error processing file {file.name}: {e}")

# Clean up temporary files
if os.path.exists("temp.pdf"):
    os.remove("temp.pdf")
