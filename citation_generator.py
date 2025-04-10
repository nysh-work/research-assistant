import streamlit as st
import re
from datetime import datetime

# --- Legal Citation Generator Tool ---
# This tool helps users generate properly formatted legal citations

def citation_generator_tab():
    """Render the citation generator tab in the Streamlit app."""
    st.header("📚 Legal Citation Generator")
    st.info("Generate properly formatted citations for legal references in various citation styles.", icon="💡")
    
    # Citation type selection
    citation_type = st.selectbox(
        "Citation Type",
        options=[
            "Case Law",
            "Statute/Act",
            "Journal Article",
            "Book",
            "Online Resource"
        ],
        index=0,
        help="Select the type of legal reference you want to cite."
    )
    
    # Citation style selection
    citation_style = st.selectbox(
        "Citation Style",
        options=[
            "Bluebook (India)",
            "OSCOLA (Oxford)",
            "Harvard",
            "APA"
        ],
        index=0,
        help="Select the citation style to use."
    )
    
    with st.container(border=True):
        # Different form fields based on citation type
        if citation_type == "Case Law":
            case_name = st.text_input("Case Name", help="E.g., Kesavananda Bharati v. State of Kerala")
            citation = st.text_input("Citation", help="E.g., AIR 1973 SC 1461")
            court = st.text_input("Court", help="E.g., Supreme Court of India")
            year = st.text_input("Year", help="E.g., 1973")
            judges = st.text_input("Judges (Optional)", help="E.g., Sikri, C.J., Shelat, Grover, JJ.")
            
            generate_button = st.button(
                "Generate Citation",
                use_container_width=True,
                disabled=(not case_name or not citation or not court or not year)
            )
            
            if generate_button:
                formatted_citation = format_case_citation(
                    case_name, citation, court, year, judges, citation_style
                )
                display_citation_result(formatted_citation)
        
        elif citation_type == "Statute/Act":
            act_name = st.text_input("Act Name", help="E.g., Income Tax Act")
            year = st.text_input("Year", help="E.g., 1961")
            section = st.text_input("Section (Optional)", help="E.g., Section 80C")
            country = st.text_input("Country", value="India", help="E.g., India")
            
            generate_button = st.button(
                "Generate Citation",
                use_container_width=True,
                disabled=(not act_name or not year)
            )
            
            if generate_button:
                formatted_citation = format_statute_citation(
                    act_name, year, section, country, citation_style
                )
                display_citation_result(formatted_citation)
        
        elif citation_type == "Journal Article":
            author = st.text_input("Author(s)", help="E.g., Sharma, A.K.")
            title = st.text_input("Article Title", help="E.g., Judicial Review in India")
            journal = st.text_input("Journal Name", help="E.g., Indian Law Review")
            volume = st.text_input("Volume", help="E.g., 45")
            issue = st.text_input("Issue (Optional)", help="E.g., 3")
            year = st.text_input("Year", help="E.g., 2020")
            pages = st.text_input("Pages", help="E.g., 123-145")
            
            generate_button = st.button(
                "Generate Citation",
                use_container_width=True,
                disabled=(not author or not title or not journal or not volume or not year or not pages)
            )
            
            if generate_button:
                formatted_citation = format_journal_citation(
                    author, title, journal, volume, issue, year, pages, citation_style
                )
                display_citation_result(formatted_citation)
        
        elif citation_type == "Book":
            author = st.text_input("Author(s)", help="E.g., Basu, D.D.")
            title = st.text_input("Book Title", help="E.g., Introduction to the Constitution of India")
            edition = st.text_input("Edition (Optional)", help="E.g., 23rd")
            publisher = st.text_input("Publisher", help="E.g., LexisNexis")
            year = st.text_input("Year", help="E.g., 2019")
            
            generate_button = st.button(
                "Generate Citation",
                use_container_width=True,
                disabled=(not author or not title or not publisher or not year)
            )
            
            if generate_button:
                formatted_citation = format_book_citation(
                    author, title, edition, publisher, year, citation_style
                )
                display_citation_result(formatted_citation)
        
        elif citation_type == "Online Resource":
            author = st.text_input("Author/Organization (Optional)", help="E.g., Supreme Court of India")
            title = st.text_input("Title", help="E.g., Judgment Information System")
            website = st.text_input("Website", help="E.g., supremecourtofindia.nic.in")
            url = st.text_input("URL", help="E.g., https://main.sci.gov.in/judgments")
            accessed_date = st.date_input("Date Accessed", value=datetime.now(), help="Date when you accessed the resource")
            
            generate_button = st.button(
                "Generate Citation",
                use_container_width=True,
                disabled=(not title or not website or not url)
            )
            
            if generate_button:
                formatted_citation = format_online_citation(
                    author, title, website, url, accessed_date, citation_style
                )
                display_citation_result(formatted_citation)

def display_citation_result(citation):
    """Display the generated citation with copy button."""
    st.divider()
    st.subheader("Generated Citation")
    
    with st.container(border=True):
        st.code(citation, language=None)
        
        # Add a button to copy the citation to clipboard
        # Use a raw f-string (rf) to handle backslashes properly
        js_safe_citation = citation.replace("'", "\\'") 
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; margin-top: 10px;">
                <button 
                    onclick="navigator.clipboard.writeText('{js_safe_citation}')" 
                    style="background-color: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                    Copy to Clipboard
                </button>
            </div>
            """,
            unsafe_allow_html=True
        )

def format_case_citation(case_name, citation, court, year, judges, style):
    """Format a case law citation based on the selected style."""
    if style == "Bluebook (India)":
        if judges:
            return f"{case_name}, {citation} ({court}, {year}) ({judges})"
        else:
            return f"{case_name}, {citation} ({court}, {year})"
    
    elif style == "OSCOLA (Oxford)":
        if judges:
            return f"{case_name} [{year}] {citation} ({judges})"
        else:
            return f"{case_name} [{year}] {citation}"
    
    elif style == "Harvard":
        return f"{case_name} ({year}) {citation}"
    
    elif style == "APA":
        return f"{case_name}, {citation} ({year})"

def format_statute_citation(act_name, year, section, country, style):
    """Format a statute citation based on the selected style."""
    if style == "Bluebook (India)":
        if section:
            return f"{section}, {act_name}, {year} ({country})"
        else:
            return f"{act_name}, {year} ({country})"
    
    elif style == "OSCOLA (Oxford)":
        if section:
            return f"{act_name} {year} ({country}), {section}"
        else:
            return f"{act_name} {year} ({country})"
    
    elif style == "Harvard" or style == "APA":
        if section:
            return f"{act_name} {year}, {section} ({country})"
        else:
            return f"{act_name} {year} ({country})"

def format_journal_citation(author, title, journal, volume, issue, year, pages, style):
    """Format a journal article citation based on the selected style."""
    if style == "Bluebook (India)":
        issue_text = f"({issue})" if issue else ""
        return f"{author}, '{title}', {volume}{issue_text} {journal} {pages} ({year})"
    
    elif style == "OSCOLA (Oxford)":
        issue_text = f"({issue})" if issue else ""
        return f"{author}, '{title}' [{year}] {volume}{issue_text} {journal} {pages}"
    
    elif style == "Harvard":
        issue_text = f"({issue})" if issue else ""
        return f"{author} ({year}) '{title}', {journal}, {volume}{issue_text}, pp. {pages}"
    
    elif style == "APA":
        issue_text = f"({issue})" if issue else ""
        return f"{author} ({year}). {title}. {journal}, {volume}{issue_text}, {pages}."

def format_book_citation(author, title, edition, publisher, year, style):
    """Format a book citation based on the selected style."""
    edition_text = f"{edition} edn, " if edition else ""
    
    if style == "Bluebook (India)":
        return f"{author}, {title} ({edition_text}{publisher}, {year})"
    
    elif style == "OSCOLA (Oxford)":
        return f"{author}, {title} ({edition_text}{publisher} {year})"
    
    elif style == "Harvard":
        return f"{author} ({year}) {title}. {edition_text}{publisher}."
    
    elif style == "APA":
        return f"{author} ({year}). {title} ({edition_text}). {publisher}."

def format_online_citation(author, title, website, url, accessed_date, style):
    """Format an online resource citation based on the selected style."""
    date_formatted = accessed_date.strftime("%d %B %Y")
    
    if style == "Bluebook (India)":
        author_text = f"{author}, " if author else ""
        return f"{author_text}'{title}', {website}, available at {url} (accessed on {date_formatted})"
    
    elif style == "OSCOLA (Oxford)":
        author_text = f"{author}, " if author else ""
        return f"{author_text}'{title}' ({website}) <{url}> accessed {date_formatted}"
    
    elif style == "Harvard":
        author_text = f"{author} " if author else "{website} "
        return f"{author_text}(n.d.). {title}. Available at: {url} [Accessed {date_formatted}]."
    
    elif style == "APA":
        author_text = f"{author}. " if author else ""
        return f"{author_text}({accessed_date.year}). {title}. {website}. Retrieved {date_formatted}, from {url}"

# This function can be imported and used in the main application
if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Legal Citation Generator")
    citation_generator_tab()