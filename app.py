import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import fitz  # PyMuPDF
import base64

load_dotenv()
if os.getenv("GOOGLE_API_KEY") is None:
    st.error("API Key not set in deployment environment.")
else:
    st.success("API Key is set.")


# Configure Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_prompt, job_description):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_prompt, job_description])
        return response.text
    except Exception as e:
        return f"Error fetching Gemini response: {e}"

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        images = []
        for page in pdf_doc:
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            images.append(img_data)
        first_page = images[0]
        pdf_parts = [
            {
                "mime_type": "image/png",
                "data": base64.b64encode(first_page).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

def main():
    st.set_page_config(page_title="ATS Resume Expert")
    st.header("ATS Tracking System")
    
    st.write("App loaded successfully. Please input job description and upload resume to proceed.")
    
    input_text = st.text_area("Job Description: ", key="input")
    uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])
    
    if uploaded_file is not None:
        st.write("PDF Uploaded Successfully")
    
    submit1 = st.button("Tell Me About the Resume")
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
            with st.spinner("Processing evaluation..."):
                # pdf_content = input_pdf_setup(uploaded_file)  # Temporarily commented to test text-only input
                response = get_gemini_response(input_prompt1, input_text)
            st.subheader("The Response is")
            st.write(response)
        else:
            st.write("Please upload the resume")
    
    elif submit3:
        if uploaded_file is not None:
            with st.spinner("Processing match analysis..."):
                # pdf_content = input_pdf_setup(uploaded_file)  # Temporarily commented to test text-only input
                response = get_gemini_response(input_prompt3, input_text)
            st.subheader("The Response is")
            st.write(response)
        else:
            st.write("Please upload the resume")

if __name__ == "__main__":
    main()
