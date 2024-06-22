import streamlit as st
from openai import OpenAI
import fitz 

api_key=st.secrets["openai"]["api_key"]

client = OpenAI(api_key=api_key)


def extract_text_from_pdf(pdf_file):
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")    
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def query_document(question, document_text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an intelligent assistant."},
            {"role": "user", "content": f"The following is a document: {document_text}"},
            {"role": "user", "content": f"Question: {question}"}
        ]
    )
    return response.choices[0].message.content

def main():
    st.set_page_config(page_title="Chat PDF")
    st.header("Generate Questions with PDF")

    toughness = st.selectbox(
        "Toughness of questions",
        ("Medium", "Hard")
    )

    language = st.selectbox(
        "Language to generate in",
        ("English", "Hindi")
    )

    number = st.select_slider(
        "Select number of questions",
        options=["5", "10", "15", "20", "25", "30", "40"]
    )

    question_type = st.selectbox(
        "Type of questions",
        ("Multiple Choice Questions", "Fill in the Blanks", "Short Answer Type")
    )

    user_question = f"Generate {number} questions to ask students in examinations in {language} of {question_type} with difficulty {toughness} from the content of this document and their answers as well."

    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        st.sidebar.write("Document uploaded successfully!")
        
        if st.button("Process"):
            with st.spinner("Extracting text from PDF..."):
                document_text = extract_text_from_pdf(uploaded_file)

            with st.spinner("Querying the document..."):
                answer = query_document(user_question, document_text)
                st.subheader("Generated Questions and Answers")
                st.write(answer)
    else:
        st.sidebar.write("Please upload a PDF document.")

if __name__ == "__main__":
    main()
