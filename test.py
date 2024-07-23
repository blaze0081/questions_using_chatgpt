import streamlit as st
from openai import OpenAI
import fitz 
import toml
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

api_key=st.secrets["openai"]["api_key"]

client = OpenAI(api_key=api_key)

# Expected password (for simplicity, it's hardcoded here)
expected_password = st.secrets["login"]["password"]
querry_context = ""

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

def create_pdf(text):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    lines = text.split("\n")
    y = height - 40
    for line in lines:
        p.drawString(40, y, line)
        y -= 15
        if y < 40:
            p.showPage()
            y = height - 40

    p.save()
    buffer.seek(0)
    return buffer

def main():
    st.set_page_config(page_title="Chat PDF")
    st.header("Generate Questions")

    toughness = st.selectbox(
        "Toughness of questions",
        ("Medium", "Hard")
    )

    language = st.selectbox(
        "Language to generate in",
        ("English", "Hindi")
    )
    number = st.number_input("Insert a number of questions", 1, 50)

    question_type = st.selectbox(
        "Type of questions",
        ("Multiple Choice Questions", "Fill in the Blanks", "Short Answer Type", "True and False")
    )

    user_question = f"Generate {number} questions to ask students in examinations in {language} of {question_type} with difficulty {toughness} from the content of this document and list their answers after listing all the questions."
    # Password input in the sidebar
    password = st.sidebar.text_input("Enter password", type="password")

    if password == expected_password:
        uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])
        topic = st.sidebar.text_input("Enter the topic for questions instead.")
        user_question_new = f"Generate {number} questions to ask students in examinations in {language} of {question_type} with difficulty {toughness} from the topic {topic} and list their answers after listing all the questions."

        if uploaded_file is not None:
            st.sidebar.write("Document uploaded successfully!")
            
            if st.button("Process"):
                with st.spinner("Extracting text from PDF..."):
                    document_text = extract_text_from_pdf(uploaded_file)

                with st.spinner("Querying the document..."):
                    answer = query_document(user_question, document_text)
                    st.subheader("Generated Questions and Answers")
                    st.write(answer)

                    pdf = create_pdf(answer)
                    st.download_button(
                        label="Download PDF",
                        data=pdf,
                        file_name="questions_and_answers.pdf",
                        mime="application/pdf"
                    )
        else:
            if topic:
                if st.button("Process"):
                    with st.spinner("Querying the document..."):
                        answer = query_document(user_question_new, querry_context)
                        st.subheader("Generated Questions and Answers")
                        st.write(answer)

                        pdf = create_pdf(answer)
                        st.download_button(
                            label="Download PDF",
                            data=pdf,
                            file_name="questions_and_answers.pdf",
                            mime="application/pdf"
                        )

    else:
        st.sidebar.write("Please enter the correct password.")

if __name__ == "__main__":
    main()
