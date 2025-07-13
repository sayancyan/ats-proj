from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
# import pdf2image
import fitz  # PyMuPDF imported for PDF processing
import google.generativeai as genai

# Configure Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_prompt, pdf_content, job_description):
    model = genai.GenerativeModel('gemini-1.5-flash')
    # response = model.generate_content([input, pdf_content[0], prompt])  # Old line with incorrect parameters
    response = model.generate_content([input_prompt, pdf_content[0], job_description])  # Corrected line
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        ## Convert the PDF to image -----(using poppler)
        # images = pdf2image.convert_from_bytes(uploaded_file.read())  # Old Poppler-based code commented

        ## Convert the PDF to image -----(using fitz)
        def convert_pdf_to_images(uploaded_file):
            pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            images = []
            for page in pdf_doc:
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                images.append(img_data)
            return images

        images = convert_pdf_to_images(uploaded_file)  # New line: calling the defined function

        # first_page = images[0]  # Old line storing image object directly

        first_page = images[0]  # Corrected: first_page is bytes data from PyMuPDF

        # Convert to bytes
        # img_byte_arr = io.BytesIO()
        # first_page.save(img_byte_arr, format='JPEG')
        # img_byte_arr = img_byte_arr.getvalue()
        # Above lines commented: not applicable as fitz output is already bytes

        pdf_parts = [
            {
                "mime_type": "image/png",  # Updated mime type to PNG from JPEG
                "data": base64.b64encode(first_page).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

## Streamlit App

st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume(PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")

# submit2 = st.button("How Can I Improvise my Skills")  # Commented out unused button

submit3 = st.button("Percentage match")

input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First the output should come as percentage, then keywords missing, and last final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")
