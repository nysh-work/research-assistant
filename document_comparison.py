import streamlit as st
import difflib
import re
from io import BytesIO

# --- Document Comparison Tool ---
# This tool allows users to compare two legal documents and see the differences

def extract_text_from_uploaded_file(uploaded_file):
    """Extract text from an uploaded file based on its type."""
    try:
        file_content = uploaded_file.getvalue()
        file_type = uploaded_file.type
        
        # Text files
        if file_type == "text/plain":
            return file_content.decode('utf-8', errors='replace')
            
        # PDF files
        elif file_type == "application/pdf":
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text: 
                        text += page_text + "\n"
                return text if text else "Could not extract text from PDF."
            except ImportError:
                return "PDF extraction requires PyPDF2 library."
                
        # DOCX files
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                import docx
                document = docx.Document(BytesIO(file_content))
                text = "\n".join([para.text for para in document.paragraphs])
                return text
            except ImportError:
                return "DOCX extraction requires python-docx library."
        else:
            return f"Unsupported file type: {file_type}"
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def compare_documents(text1, text2, comparison_type="line"):
    """Compare two text documents and return HTML with differences highlighted."""
    if comparison_type == "line":
        # Line by line comparison
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        differ = difflib.HtmlDiff(wrapcolumn=80)
        diff_html = differ.make_file(lines1, lines2, "Document 1", "Document 2")
        
        # Improve the styling of the HTML output
        diff_html = diff_html.replace('<table class="diff" id="difflib_chg_to0__top"', 
                                     '<table class="diff table" style="width:100%;"')
        return diff_html
    
    elif comparison_type == "word":
        # Word by word comparison
        words1 = re.findall(r'\w+|[^\w\s]', text1)
        words2 = re.findall(r'\w+|[^\w\s]', text2)
        
        matcher = difflib.SequenceMatcher(None, words1, words2)
        
        # Generate HTML with word differences
        html = ['<div style="font-family: monospace; white-space: pre-wrap;">']
        
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == 'equal':
                html.append('<span>' + ' '.join(words1[i1:i2]) + '</span>')
            elif op == 'insert':
                html.append('<span style="background-color: #aaffaa;">' + ' '.join(words2[j1:j2]) + '</span>')
            elif op == 'delete':
                html.append('<span style="background-color: #ffaaaa;">' + ' '.join(words1[i1:i2]) + '</span>')
            elif op == 'replace':
                html.append('<span style="background-color: #ffaaaa;">' + ' '.join(words1[i1:i2]) + '</span>')
                html.append('<span style="background-color: #aaffaa;">' + ' '.join(words2[j1:j2]) + '</span>')
        
        html.append('</div>')
        return ''.join(html)
    
    return "<p>Invalid comparison type selected.</p>"

def document_comparison_tab():
    """Render the document comparison tab in the Streamlit app."""
    st.header("📄 Document Comparison Tool")
    st.info("Upload two legal documents to compare them and see the differences highlighted.", icon="💡")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Document 1")
            doc1 = st.file_uploader(
                "Upload first document",
                type=['pdf', 'docx', 'txt'],
                key="doc1_uploader",
                help="Select the first document for comparison."
            )
        
        with col2:
            st.subheader("Document 2")
            doc2 = st.file_uploader(
                "Upload second document",
                type=['pdf', 'docx', 'txt'],
                key="doc2_uploader",
                help="Select the second document for comparison."
            )
    
    comparison_type = st.radio(
        "Comparison Method",
        options=["Line by Line", "Word by Word"],
        index=0,
        horizontal=True,
        help="Choose how to compare the documents."
    )
    
    compare_button = st.button(
        "🔍 Compare Documents",
        use_container_width=True,
        disabled=(not doc1 or not doc2)
    )
    
    if compare_button and doc1 and doc2:
        with st.spinner("⏳ Comparing documents..."):
            # Extract text from both documents
            text1 = extract_text_from_uploaded_file(doc1)
            text2 = extract_text_from_uploaded_file(doc2)
            
            # Check if text extraction was successful
            if text1.startswith("Error") or text2.startswith("Error"):
                if text1.startswith("Error"):
                    st.error(f"Error with document 1: {text1}", icon="❗")
                if text2.startswith("Error"):
                    st.error(f"Error with document 2: {text2}", icon="❗")
            else:
                # Perform comparison based on selected method
                comp_type = "line" if comparison_type == "Line by Line" else "word"
                diff_html = compare_documents(text1, text2, comp_type)
                
                st.subheader("Comparison Results")
                st.markdown("""<style>
                    .diff {border-collapse: collapse; font-family: monospace; width: 100%;}
                    .diff td {padding: 5px; vertical-align: top; white-space: pre-wrap;}
                    .diff_header {background-color: #e0e0e0; text-align: right;}
                    .diff_next {background-color: #c0c0c0;}
                    .diff_add {background-color: #aaffaa;}
                    .diff_chg {background-color: #ffff77;}
                    .diff_sub {background-color: #ffaaaa;}
                </style>""", unsafe_allow_html=True)
                st.components.v1.html(diff_html, height=600, scrolling=True)

# This function can be imported and used in the main application
if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Document Comparison Tool")
    document_comparison_tab()