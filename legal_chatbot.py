import streamlit as st
import google.generativeai as genai
import os
from io import BytesIO
import time # For simulating streaming delay if needed, and for UI updates

# --- Potentially needed libraries for file extraction (install them) ---
# You might need: pip install PyPDF2 python-docx
try:
    import PyPDF2
except ImportError:
    # Don't use st.warning here before set_page_config
    PyPDF2 = None
try:
    import docx
except ImportError:
    # Don't use st.warning here before set_page_config
    docx = None

# --- Page Config (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    layout="wide",
    page_title="Chatbot Assistant",
    page_icon=":robot_face:",
    initial_sidebar_state="collapsed" # Keep sidebar open initially
)

# --- Gemini API Configuration ---
# Attempt to configure Gemini, store status in session state
if 'gemini_api_configured' not in st.session_state:
    st.session_state.gemini_api_configured = False
    st.session_state.gemini_error_message = None
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-pro-preview-03-25')
        # Perform a quick test if possible, or assume configured if no exception
        st.session_state.gemini_api_configured = True
        st.session_state.model = model # Store model in session state
    except KeyError:
        st.session_state.gemini_error_message = "Gemini API Key not found in Streamlit secrets (`.streamlit/secrets.toml`)."
    except Exception as e:
        st.session_state.gemini_error_message = f"Error configuring Gemini API: {e}"

# --- Custom CSS for Styling ---
# (CSS remains the same as before)
st.markdown("""
<style>
    /* General body styling */
    body {
        font-family: 'Inter', sans-serif;
    }

    /* Make headers slightly bolder/more distinct */
    h1, h2, h3 {
        font-weight: 600; /* Semi-bold */
    }

    /* Style Streamlit buttons */
    .stButton>button {
        border-radius: 10px;
        border: 1px solid #007bff;
        color: #007bff;
        padding: 0.5em 1em;
        background-color: #ffffff;
        transition: all 0.3s ease;
        margin-top: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* Subtle shadow */
    }
    .stButton>button:hover {
        background-color: #007bff;
        color: #ffffff;
        border-color: #0056b3;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Slightly larger shadow on hover */
    }
    .stButton>button:active {
        background-color: #0056b3;
        color: #ffffff;
    }
    .stButton>button:disabled {
        border-color: #cccccc;
        color: #cccccc;
        background-color: #f1f1f1;
        box-shadow: none;
    }


    /* Style chat messages */
    [data-testid="chat-message-container"] {
        border-radius: 15px;
        padding: 1em 1.2em; /* Increased padding */
        margin-bottom: 0.75em; /* Increased margin */
        max-width: 85%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08); /* Add shadow to chat bubbles */
        border: 1px solid transparent; /* Base border */
    }
    /* User message styling */
    [data-testid="stChatMessage"] [data-testid="chat-message-container"]:has(div[data-testid="stMarkdownContainer"] p) {
         background-color: #e7f0ff;
         border-color: #d0e0ff; /* Subtle border */
    }
    /* Model message styling */
     [data-testid="stChatMessage"]:has(span[title="model"]) [data-testid="chat-message-container"] {
         background-color: #f8f9fa; /* Lighter grey */
         border-color: #e9ecef; /* Subtle border */
     }

    /* Style file uploader */
    [data-testid="stFileUploader"] {
        border: 1px dashed #ced4da;
        border-radius: 10px;
        background-color: #f8f9fa; /* Light background */
        padding: 1.5em; /* More padding */
    }

    /* Style text inputs */
    .stTextInput input {
        border-radius: 10px;
        border: 1px solid #ced4da;
        padding: 0.75em 1em; /* Increased padding */
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.075); /* Inner shadow */
    }
    .stTextInput label {
        font-weight: 500; /* Medium weight */
        margin-bottom: 0.3em;
        display: block;
    }

    /* Style containers with border=True */
    [data-testid="stVerticalBlock"]:has(>[data-testid="stVerticalBlockBorderWrapper"]) {
        border: 1px solid #e9ecef !important; /* Ensure border is visible */
        border-radius: 10px !important;
        padding: 1.5em !important; /* Add padding inside bordered containers */
        background-color: #ffffff; /* White background for contrast */
        box-shadow: 0 3px 6px rgba(0,0,0,0.05); /* Add shadow to containers */
    }

    /* Style expanders */
    .streamlit-expanderHeader {
        border-radius: 10px;
        border: 1px solid #e9ecef;
        background-color: #f8f9fa; /* Light background for expander header */
    }
    .streamlit-expanderHeader:hover {
        background-color: #e9ecef; /* Darker on hover */
    }

    /* Style info boxes */
    [data-testid="stInfo"] {
        border-radius: 10px;
        border-left: 5px solid #0dcaf0; /* Info blue color */
        background-color: #f0fcff;
        padding: 1em;
    }
     /* Style warning boxes */
    [data-testid="stWarning"] {
        border-radius: 10px;
        border-left: 5px solid #ffc107; /* Warning yellow color */
        background-color: #fff9e6;
        padding: 1em;
    }
     /* Style error boxes */
    [data-testid="stError"] {
        border-radius: 10px;
        border-left: 5px solid #dc3545; /* Error red color */
        background-color: #ffebee;
        padding: 1em;
    }
</style>
""", unsafe_allow_html=True)

# --- Display Global Errors/Warnings Early ---
# (Error/Warning display remains the same)
if not PyPDF2:
    st.warning("PyPDF2 library not found (`pip install PyPDF2`). PDF file processing will be disabled.", icon="⚠️")
if not docx:
    st.warning("python-docx library not found (`pip install python-docx`). DOCX file processing will be disabled.", icon="⚠️")
if not st.session_state.gemini_api_configured:
    st.error(f"**Gemini API Configuration Failed:** {st.session_state.gemini_error_message} AI features requiring Gemini will be disabled.", icon="🚨")


# --- Text Extraction Functions ---
# (Functions remain the same)
def extract_text_from_pdf(file_content):
    """Extracts text from a PDF file stream."""
    if not PyPDF2: return None
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text: text += page_text + "\n"
        return text if text else "Could not extract text (check PDF content)."
    except Exception as e: return f"Error reading PDF: {e}"

def extract_text_from_docx(file_content):
    """Extracts text from a DOCX file stream."""
    if not docx: return None
    try:
        document = docx.Document(BytesIO(file_content))
        text = "\n".join([para.text for para in document.paragraphs])
        return text
    except Exception as e: return f"Error reading DOCX: {e}"

def extract_text_from_txt(file_content):
    """Extracts text from a TXT file stream."""
    try: return file_content.decode('utf-8', errors='replace')
    except Exception as e: return f"Error reading TXT file: {e}"

# --- Gemini Interaction Function (Streaming) ---
# (Function remains the same)
def get_gemini_response_stream(prompt, context=""):
    """Gets a streaming response generator from the Gemini API."""
    if not st.session_state.get('gemini_api_configured', False) or 'model' not in st.session_state:
        yield "⚠️ AI features disabled: Gemini model not initialized or API key missing."
        return

    model = st.session_state.model
    full_prompt = prompt
    if context:
        full_prompt = f"Use the following context if relevant:\n--- CONTEXT START ---\n{context}\n--- CONTEXT END ---\n\nBased on the context (if relevant) and your general knowledge, answer the following question:\n{prompt}"

    try:
        response_stream = model.generate_content(full_prompt, stream=True)
        for chunk in response_stream:
            if chunk.parts:
                yield chunk.text
    except Exception as e:
        yield f"\n\n[An error occurred while contacting the AI: {e}]"


# --- Streamlit App UI ---
st.title("🏛️ Chatbot Assistant")
st.caption("Your AI-powered research companion")

# --- Initialize Session State (if not already done) ---
# (Initialization remains the same)
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'uploaded_file_text' not in st.session_state: st.session_state.uploaded_file_text = {}
if 'case_search_result_stream' not in st.session_state: st.session_state.case_search_result_stream = None
if 'provision_search_result_stream' not in st.session_state: st.session_state.provision_search_result_stream = None


# --- Sidebar ---
# (Sidebar remains the same)
with st.sidebar:
    st.header("⚙️ Settings & Status")
    st.divider()
    st.subheader("API Status")
    if st.session_state.gemini_api_configured:
        st.success("✅ Gemini API Connected", icon="🔗")
    else:
        st.error("❌ Gemini API Disconnected", icon="🔌")
        st.caption(st.session_state.gemini_error_message)
    st.divider()
    st.subheader("Manage Session")
    if st.button("⚠️ Clear All Session Data", use_container_width=True, help="Clears chat history, uploaded files, and search results."):
        keys_to_clear = ['chat_history', 'uploaded_file_text', 'case_search_result_stream', 'provision_search_result_stream']
        for key in keys_to_clear:
            if key in st.session_state:
                if key == 'chat_history': st.session_state[key] = []
                elif key == 'uploaded_file_text': st.session_state[key] = {}
                else: st.session_state[key] = None
        st.success("Session data cleared!", icon="🧹")
        time.sleep(1)
        st.rerun()

# --- Build Combined Context ---
# (Function remains the same)
def get_combined_context():
    """Combines text from uploaded files."""
    context = ""
    if st.session_state.uploaded_file_text:
        context += "Context from Uploaded Files:\n"
        total_len = 0
        max_len = 2000000
        for filename, text in st.session_state.uploaded_file_text.items():
            preview_len = min(len(text), max_len - total_len)
            if preview_len <= 0: break
            context += f"--- Start {filename} ---\n{text[:preview_len]}...\n--- End {filename} ---\n\n"
            total_len += preview_len + len(f"--- Start {filename} ---\n...\n--- End {filename} ---\n\n")
        context += "---\n"
    return context.strip()


# --- Import Tab Modules ---
from document_comparison import compare_documents, extract_text_from_uploaded_file
from citation_generator import citation_generator_tab
from deadline_tracker import deadline_tracker_tab
from advanced_search import advanced_search_tab

# --- Create Tabs (Reordered) ---
tab_titles = [
    "📄 Upload Files",      # Stays 1st
    "💬 General Chat",      # Was 4th, now 2nd
    "🔎 Case Law Search",  # Was 2nd, now 3rd
    "📜 Legal Provisions",  # Was 3rd, now 4th
    "📊 Document Comparison", # New feature
    "📚 Citation Generator", # New feature
    "📅 Deadline Tracker", # New feature
    "🔍 Advanced Search"   # New feature
]
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(tab_titles) # Variables now map to the new order

# --- Tab 1: Upload Files (Content remains the same) ---
with tab1:
    st.header("📄 Upload Documents for Context")
    st.info("Upload PDF, DOCX, or TXT files. Extracted text provides context for the 'General Chat' tab.", icon="💡")

    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt'],
            key="file_uploader",
            help="Select one or more documents."
        )

        if uploaded_files:
            with st.spinner("⏳ Processing uploaded files..."):
                newly_uploaded_text = {}
                errors = []
                success_count = 0
                for uploaded_file in uploaded_files:
                    filename = uploaded_file.name
                    if filename not in st.session_state.uploaded_file_text:
                        file_content = uploaded_file.getvalue()
                        text_or_error = None
                        file_type = uploaded_file.type

                        if file_type == "application/pdf":
                            if PyPDF2: text_or_error = extract_text_from_pdf(file_content)
                            else: errors.append(f"{filename} (PDF library missing)")
                        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                            if docx: text_or_error = extract_text_from_docx(file_content)
                            else: errors.append(f"{filename} (DOCX library missing)")
                        elif file_type == "text/plain":
                            text_or_error = extract_text_from_txt(file_content)
                        else:
                            errors.append(f"{filename} (unsupported type: {file_type})")

                        if isinstance(text_or_error, str) and not text_or_error.startswith("Error"):
                            newly_uploaded_text[filename] = text_or_error
                            success_count += 1
                        elif isinstance(text_or_error, str):
                             errors.append(f"{filename} ({text_or_error})")

                st.session_state.uploaded_file_text.update(newly_uploaded_text)

            if success_count > 0:
                 st.success(f"✅ Successfully processed {success_count} new file(s).", icon="👍")
            if errors:
                 st.error(f"⚠️ Could not fully process some files: {'; '.join(errors)}", icon="❗")

    st.divider()
    st.subheader("📚 Currently Loaded Files for Context")
    if st.session_state.uploaded_file_text:
        loaded_files = list(st.session_state.uploaded_file_text.keys())
        for filename in loaded_files:
             if filename in st.session_state.uploaded_file_text:
                with st.container(border=True):
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(f"**📄 {filename}**")
                    with col2:
                        if st.button(f"🗑️ Remove", key=f"remove_{filename}", help=f"Remove {filename} from context", use_container_width=True):
                            if filename in st.session_state.uploaded_file_text:
                                del st.session_state.uploaded_file_text[filename]
                            st.rerun()
    else:
        st.info("No files loaded yet. Upload documents above to add context.", icon="📁")


# --- Tab 2: General Chat (Moved from original Tab 4) ---
with tab2: # This now holds the General Chat content
    st.header("💬 General Legal Chat")
    st.info("Ask general legal questions. Uploaded file content will be used as context. Responses stream in.", icon="💡")

    # Display current context summary
    active_context = get_combined_context()
    if active_context:
        with st.expander("View Active File Context Being Sent to AI", expanded=False):
            context_display = (active_context[:2000000] + '...') if len(active_context) > 2000000 else active_context
            st.text_area("Context Preview:", value=context_display, height=200, disabled=True, key="context_display_chat_v4_tab2") # Unique key

    st.divider()

    # Chat History Area
    st.subheader("Conversation History")
    chat_container = st.container(height=500)
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    st.divider()

    # Chat input area
    prompt = st.chat_input(
        "Ask your question...",
        key="chat_input_v4_tab2", # Unique key
        disabled=(not st.session_state.gemini_api_configured)
    )

    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        context_for_prompt = get_combined_context()
        response_generator = get_gemini_response_stream(prompt, context=context_for_prompt)

        # Display stream and collect chunks within the chat container
        with chat_container:
             with st.chat_message("user"):
                 st.markdown(prompt)
             with st.chat_message("model"):
                 full_response = st.write_stream(response_generator)

        if full_response:
             st.session_state.chat_history.append({"role": "model", "content": full_response})
             st.rerun() # Rerun to update history display
        else:
             st.warning("The AI did not provide a response.", icon="⚠️")


# --- Tab 3: Case Law Search (Moved from original Tab 2) ---
with tab3: # This now holds the Case Law Search content
    st.header("🔎 AI Case Law Search")
    st.info("Enter case details. The AI will attempt to find and summarize the case (results stream below).", icon="💡")

    with st.container(border=True):
        col1_case, col2_case = st.columns(2)
        with col1_case:
            search_name = st.text_input(
                "Case Name",
                key="case_name_input_v4_tab3", # Unique key
                help="E.g., Kesavananda Bharati vs State of Kerala"
            )
        with col2_case:
            search_year = st.text_input(
                "Year (Optional)",
                key="case_year_input_v4_tab3", # Unique key
                help="E.g., 1973"
            )

        can_search_case = st.session_state.gemini_api_configured and (search_name or search_year)
        search_button_clicked = st.button(
            "🔍 Search Cases with AI",
            key="search_case_ai_btn_stream_v4_tab3", # Unique key
            disabled=not can_search_case,
            use_container_width=True
        )

    st.divider()

    if search_button_clicked:
        prompt = f"Please provide information on the Indian case law titled '{search_name}'"
        if search_year: prompt += f" from the year {search_year}"
        else: prompt += " (if year is unknown, provide the most relevant match)"
        prompt += ". Include a summary, key judgment points, related case with relevant citations and legal interpretations if available."

        with st.spinner("⏳ Asking AI to search for case law..."):
            st.session_state.case_search_result_stream = get_gemini_response_stream(prompt)

    if st.session_state.case_search_result_stream:
        st.subheader("💬 AI Search Result:")
        with st.container(border=True):
             st.write_stream(st.session_state.case_search_result_stream)
        st.session_state.case_search_result_stream = None


# --- Tab 4: Legal Provision Lookup (Moved from original Tab 3) ---
with tab4: # This now holds the Legal Provision Lookup content
    st.header("📜Legal Provision Lookup")
    st.info("Enter a section number or keyword (e.g., 'Section 80C Income Tax Act'). The AI will try to explain it.", icon="💡")

    with st.container(border=True):
        search_term = st.text_input(
            "Section Number or Keyword",
            key="provision_input_v4_tab4", # Unique key
            help="E.g., 'agricultural income exemption' or 'Section 10(1) IT Act'"
            )

        can_search_prov = st.session_state.gemini_api_configured and search_term
        search_prov_button_clicked = st.button(
            "📜 Search Provisions with AI",
            key="search_prov_ai_btn_stream_v4_tab4", # Unique key
            disabled=not can_search_prov,
            use_container_width=True
            )

    st.divider()

    if search_prov_button_clicked:
        prompt = f"""Regarding the legal provision for '{search_term}' under Indian law:

    Provide the following information formatted clearly using Markdown, suitable for direct use in Notion notes. Do *not* include any conversational text, introductory phrases, or concluding remarks. Output *only* the structured information requested below:

    ### **Act and Section:**
    [Specify the full Act name and relevant Section number(s) here]

    ### **Detailed Notes:**
    [Provide a detailed notes of the legal provision.]

    ### **Key Aspects:**
    * [Explain the first key aspect or element]
    * [Explain the second key aspect or element]
    * [Add more bullet points as necessary for other key aspects]

    ### **Relevant Case Laws:**
    * [Relevant case law number 1 with a brief summary note]
    * [Relevant case law number 2 with a brief summary note]
    * [Add more bullet points as necessary for other relevant case laws]
    """

        with st.spinner("⏳ Asking AI to search for provision..."):
            st.session_state.provision_search_result_stream = get_gemini_response_stream(prompt)

    if st.session_state.provision_search_result_stream:
        st.subheader("💬 AI Search Result:")
        with st.container(border=True):
            st.write_stream(st.session_state.provision_search_result_stream)
        st.session_state.provision_search_result_stream = None


# --- Tab 5: Document Comparison ---
with tab5:
    st.header("📊 Document Comparison")
    st.info("Compare two legal documents and see the differences highlighted.", icon="💡")
    
    # File upload section
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Document 1")
        file1 = st.file_uploader("Upload first document", key="doc_compare_file1", 
                               type=["txt", "pdf", "docx"], help="Upload the first document for comparison")
    
    with col2:
        st.subheader("Document 2")
        file2 = st.file_uploader("Upload second document", key="doc_compare_file2", 
                               type=["txt", "pdf", "docx"], help="Upload the second document for comparison")
    
    # Comparison options
    comparison_type = st.radio(
        "Comparison Type",
        options=["Line by Line", "Word by Word"],
        index=0,
        horizontal=True,
        help="Select how to compare the documents"
    )
    
    compare_button = st.button(
        "Compare Documents", 
        key="compare_docs_button",
        use_container_width=True,
        disabled=(file1 is None or file2 is None)
    )
    
    # Perform comparison when button is clicked
    if compare_button and file1 and file2:
        with st.spinner("Comparing documents..."):
            # Extract text from uploaded files
            text1 = extract_text_from_uploaded_file(file1)
            text2 = extract_text_from_uploaded_file(file2)
            
            # Determine comparison type
            comp_type = "line" if comparison_type == "Line by Line" else "word"
            
            # Compare documents
            comparison_result = compare_documents(text1, text2, comp_type)
            
            # Display results
            st.subheader("Comparison Results")
            st.markdown(comparison_result, unsafe_allow_html=True)


# --- Tab 6: Citation Generator ---
with tab6:
    citation_generator_tab()


# --- Tab 7: Deadline Tracker ---
with tab7:
    deadline_tracker_tab()


# --- Tab 8: Advanced Search ---
with tab8:
    advanced_search_tab()