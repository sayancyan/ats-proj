import base64
import streamlit as st
import fitz
import google.generativeai as genai

#  API key config (streamlit deployment)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])


# Getting Input
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:

        ## Convert the PDF to image -----(using fitz)
        def convert_pdf_to_images(uploaded_file):
            pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            images = []
            for page in pdf_doc:
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                images.append(img_data)
            return images
        
        ## main
        images = convert_pdf_to_images(uploaded_file)
        first_page = images[0]
        pdf_parts = [
            {
                "mime_type": "image/png",
                "data": base64.b64encode(first_page).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Giving Output
def get_gemini_response(input_prompt, pdf_content, job_description):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, pdf_content[0], job_description])
    return response.text

## Streamlit App Setup
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume(PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

# Buttons
submit1 = st.button("Resume Overview")
submit3 = st.button("Percentage match")

# Input Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager.
Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""
input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description.
Give me the percentage of match if the resume matches the job description.
First the output should come as percentage, then keywords missing, and last final thoughts.
"""

# Input Config
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
