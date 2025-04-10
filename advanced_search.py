import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import re
import google.generativeai as genai

# --- Advanced Search Tool ---
# This tool provides advanced search capabilities for legal research

def advanced_search_tab():
    """Render the advanced search tab in the Streamlit app."""
    st.header("🔍 Advanced Legal Search")
    st.info("Search for legal information with advanced filters by jurisdiction, date range, and legal domain.", icon="💡")
    
    # Create columns for search parameters
    col1, col2 = st.columns(2)
    
    with col1:
        search_query = st.text_input(
            "Search Query",
            help="Enter keywords or phrases to search for."
        )
        
        # Jurisdiction filter
        jurisdiction = st.multiselect(
            "Jurisdiction",
            options=[
                "Supreme Court", "High Courts", "District Courts",
                "Income Tax Appellate Tribunal", "GST Authority",
                "Company Law Board", "National Company Law Tribunal",
                "Consumer Forums", "All"
            ],
            default=["All"],
            help="Select jurisdictions to include in search results."
        )
    
    with col2:
        # Date range filter
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input(
                "From Date",
                value=datetime(2000, 1, 1),
                help="Select the start date for filtering results."
            )
        with col_date2:
            end_date = st.date_input(
                "To Date",
                value=datetime.now(),
                help="Select the end date for filtering results."
            )
        
        # Legal domain filter
        legal_domain = st.multiselect(
            "Legal Domain",
            options=[
                "Constitutional Law", "Criminal Law", "Civil Law",
                "Corporate Law", "Tax Law", "Intellectual Property",
                "Banking & Finance", "Environmental Law", "Labor Law",
                "Family Law", "All"
            ],
            default=["All"],
            help="Select legal domains to include in search results."
        )
    
    # Advanced filters in an expander
    with st.expander("Advanced Filters", expanded=False):
        col_adv1, col_adv2, col_adv3 = st.columns(3)
        
        with col_adv1:
            # Document type filter
            document_type = st.multiselect(
                "Document Type",
                options=[
                    "Judgments", "Orders", "Notifications",
                    "Circulars", "Acts", "Rules", "Regulations",
                    "All"
                ],
                default=["All"],
                help="Select document types to include in search results."
            )
        
        with col_adv2:
            # Citation filter
            citation = st.text_input(
                "Citation",
                help="Enter a specific citation to search for (e.g., AIR 2019 SC 1234)."
            )
            
            # Judge/Bench filter
            judge = st.text_input(
                "Judge/Bench",
                help="Enter the name of a judge or bench to filter results."
            )
        
        with col_adv3:
            # Sort options
            sort_by = st.selectbox(
                "Sort Results By",
                options=[
                    "Relevance", "Date (Newest First)", "Date (Oldest First)",
                    "Citation Frequency", "Court Hierarchy"
                ],
                index=0,
                help="Select how to sort the search results."
            )
            
            # Results per page
            results_per_page = st.slider(
                "Results Per Page",
                min_value=10,
                max_value=100,
                value=20,
                step=10,
                help="Select the number of results to display per page."
            )
    
    # Search button
    search_button = st.button(
        "🔍 Search",
        use_container_width=True,
        disabled=(not search_query)
    )
    
    # Display search results
    if search_button and search_query:
        with st.spinner("Searching..."):
            # In a real implementation, this would call the Gemini API with the search parameters
            # For now, we'll simulate results
            
            # Call the function to get AI-powered search results
            results = get_search_results(search_query, jurisdiction, start_date, end_date, legal_domain)
            
            # Display results count and search parameters
            st.divider()
            st.subheader(f"Search Results: {len(results)} matches found")
            
            # Display search parameters
            st.markdown(f"**Query:** {search_query}")
            jurisdiction_str = ", ".join(jurisdiction) if "All" not in jurisdiction else "All Jurisdictions"
            domain_str = ", ".join(legal_domain) if "All" not in legal_domain else "All Legal Domains"
            st.markdown(f"**Filters:** {jurisdiction_str} | {domain_str} | {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}")
            
            # Display results
            if results:
                # Create tabs for different result views
                result_tabs = st.tabs(["List View", "Analytics", "Citation Network"])
                
                # Tab 1: List View
                with result_tabs[0]:
                    for i, result in enumerate(results):
                        with st.container(border=True):
                            col1, col2 = st.columns([0.8, 0.2])
                            
                            with col1:
                                st.markdown(f"**{i+1}. {result['title']}**")
                                st.markdown(f"*{result['citation']}*")
                                st.markdown(result['snippet'])
                            
                            with col2:
                                st.markdown(f"**Court:** {result['court']}")
                                st.markdown(f"**Date:** {result['date']}")
                                st.markdown(f"**Domain:** {result['domain']}")
                            
                            # View button
                            if st.button(f"View Full Document", key=f"view_{i}", use_container_width=True):
                                # In a real implementation, this would open the document
                                st.info(f"Viewing document: {result['title']}")
                                
                                # Simulate document content
                                st.markdown(f"### {result['title']}")
                                st.markdown(f"**Citation:** {result['citation']}")
                                st.markdown(f"**Court:** {result['court']}")
                                st.markdown(f"**Date:** {result['date']}")
                                st.markdown(f"**Judges:** {result['judges']}")
                                st.markdown("### Judgment")
                                st.markdown(result['content'])
                
                # Tab 2: Analytics
                with result_tabs[1]:
                    st.subheader("Search Results Analytics")
                    
                    # Convert results to DataFrame for analysis
                    df = pd.DataFrame(results)
                    
                    # Create visualizations
                    col_viz1, col_viz2 = st.columns(2)
                    
                    with col_viz1:
                        # Court distribution
                        court_counts = df['court'].value_counts().reset_index()
                        court_counts.columns = ['Court', 'Count']
                        
                        fig1 = px.pie(
                            court_counts,
                            values='Count',
                            names='Court',
                            title='Distribution by Court',
                            hole=0.4
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col_viz2:
                        # Domain distribution
                        domain_counts = df['domain'].value_counts().reset_index()
                        domain_counts.columns = ['Domain', 'Count']
                        
                        fig2 = px.bar(
                            domain_counts,
                            x='Domain',
                            y='Count',
                            title='Distribution by Legal Domain',
                            color='Domain'
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    # Timeline of results
                    df['date_obj'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
                    df = df.sort_values('date_obj')
                    
                    fig3 = px.line(
                        df,
                        x='date_obj',
                        y=df.groupby('date_obj').size(),
                        title='Timeline of Results',
                        labels={'date_obj': 'Date', 'y': 'Number of Results'}
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                
                # Tab 3: Citation Network
                with result_tabs[2]:
                    st.subheader("Citation Network")
                    st.info("This visualization shows how the cases in your search results cite each other.")
                    
                    # In a real implementation, this would show a network graph of citations
                    # For now, we'll display a placeholder message
                    st.markdown("*Citation network visualization would be displayed here.*")
                    
                    # Display most cited cases
                    st.subheader("Most Cited Cases in Results")
                    
                    # Simulate citation counts
                    citation_data = {
                        'Case': [result['title'] for result in results[:5]],
                        'Citations': [95, 78, 63, 42, 36]
                    }
                    citation_df = pd.DataFrame(citation_data)
                    
                    fig4 = px.bar(
                        citation_df,
                        x='Case',
                        y='Citations',
                        title='Most Cited Cases',
                        color='Citations'
                    )
                    st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No results found. Try modifying your search query or filters.", icon="ℹ️")

def get_search_results(query, jurisdiction, start_date, end_date, legal_domain, document_type=None, citation=None, judge=None, sort_by="Relevance"):
    """Get search results from the Gemini API based on search parameters."""
    # Simulate search results for demonstration purposes
    results = [
        {
            'title': 'Kesavananda Bharati v. State of Kerala',
            'citation': 'AIR 1973 SC 1461',
            'court': 'Supreme Court',
            'date': '24-04-1973',
            'domain': 'Constitutional Law',
            'judges': 'S.M. Sikri, C.J., A.N. Ray, D.G. Palekar, H.R. Khanna, K.K. Mathew, M.H. Beg, S.N. Dwivedi, A.N. Grover, J.M. Shelat, P. Jaganmohan Reddy, K.S. Hegde, A.K. Mukherjea, B.K. Mukherjea, JJ.',
            'snippet': 'The case established the basic structure doctrine, which holds that the Constitution possesses a basic structure of constitutional principles and values that cannot be destroyed by amendments...',
            'content': 'The case established the basic structure doctrine, which holds that the Constitution possesses a basic structure of constitutional principles and values that cannot be destroyed by amendments. The Supreme Court held that while Parliament has the power to amend the Constitution under Article 368, it cannot use this power to alter the "basic structure" or "basic features" of the Constitution.'
        },
        {
            'title': 'Maneka Gandhi v. Union of India',
            'citation': 'AIR 1978 SC 597',
            'court': 'Supreme Court',
            'date': '25-01-1978',
            'domain': 'Constitutional Law',
            'judges': 'M. Hameedullah Beg, C.J., P.N. Bhagwati, Y.V. Chandrachud, V.R. Krishna Iyer, N.L. Untwalia, S. Murtaza Fazal Ali, P.S. Kailasam, JJ.',
            'snippet': 'This case expanded the interpretation of Article 21 of the Constitution, holding that the right to life and personal liberty includes a bundle of rights that makes life meaningful...',
            'content': 'This case expanded the interpretation of Article 21 of the Constitution, holding that the right to life and personal liberty includes a bundle of rights that makes life meaningful. The Court held that the procedure established by law for depriving a person of their life and personal liberty must be fair, just, and reasonable.'
        },
        {
            'title': 'Union Carbide Corporation v. Union of India',
            'citation': 'AIR 1990 SC 273',
            'court': 'Supreme Court',
            'date': '14-02-1989',
            'domain': 'Environmental Law',
            'judges': 'R.S. Pathak, C.J., E.S. Venkataramiah, Ranganath Misra, M.N. Venkatachaliah, N.D. Ojha, JJ.',
            'snippet': 'This case dealt with the settlement of claims arising from the Bhopal Gas Tragedy. The Supreme Court upheld the constitutional validity of the Bhopal Gas Leak Disaster Act...',
            'content': 'This case dealt with the settlement of claims arising from the Bhopal Gas Tragedy. The Supreme Court upheld the constitutional validity of the Bhopal Gas Leak Disaster Act and approved a settlement of $470 million between Union Carbide and the Government of India.'
        },
        {
            'title': 'Vishaka v. State of Rajasthan',
            'citation': 'AIR 1997 SC 3011',
            'court': 'Supreme Court',
            'date': '13-08-1997',
            'domain': 'Labor Law',
            'judges': 'J.S. Verma, C.J., Sujata V. Manohar, B.N. Kirpal, JJ.',
            'snippet': 'In this landmark case, the Supreme Court laid down guidelines for prevention of sexual harassment of women at workplaces, which came to be known as the Vishaka Guidelines...',
            'content': 'In this landmark case, the Supreme Court laid down guidelines for prevention of sexual harassment of women at workplaces, which came to be known as the Vishaka Guidelines. The Court held that sexual harassment at the workplace is a violation of the fundamental rights of women under Articles 14, 15, and 21 of the Constitution.'
        },
        {
            'title': 'Navtej Singh Johar v. Union of India',
            'citation': '(2018) 10 SCC 1',
            'court': 'Supreme Court',
            'date': '06-09-2018',
            'domain': 'Constitutional Law',
            'judges': 'Dipak Misra, C.J., R.F. Nariman, A.M. Khanwilkar, D.Y. Chandrachud, Indu Malhotra, JJ.',
            'snippet': 'In this landmark judgment, the Supreme Court decriminalized consensual homosexual acts by declaring Section 377 of the Indian Penal Code unconstitutional insofar as it criminalized consensual sexual conduct between adults of the same sex...',
            'content': 'In this landmark judgment, the Supreme Court decriminalized consensual homosexual acts by declaring Section 377 of the Indian Penal Code unconstitutional insofar as it criminalized consensual sexual conduct between adults of the same sex. The Court held that Section 377 violated the constitutional rights to dignity, privacy, equality, and freedom of expression.'
        }
    ]
    
    # Filter results based on search parameters
    filtered_results = results
    
    # Filter by jurisdiction if not "All"
    if "All" not in jurisdiction:
        filtered_results = [r for r in filtered_results if any(j.lower() in r['court'].lower() for j in jurisdiction)]
    
    # Filter by date range
    date_filtered = []
    for r in filtered_results:
        try:
            result_date = datetime.strptime(r['date'], '%d-%m-%Y').date()
            if start_date <= result_date <= end_date:
                date_filtered.append(r)
        except ValueError:
            # Keep results with invalid date format
            date_filtered.append(r)
    filtered_results = date_filtered
    
    # Filter by legal domain if not "All"
    if "All" not in legal_domain:
        filtered_results = [r for r in filtered_results if any(d.lower() in r['domain'].lower() for d in legal_domain)]
    
    # Filter by query (simple substring match for demonstration)
    if query:
        query_lower = query.lower()
        filtered_results = [r for r in filtered_results if 
                           query_lower in r['title'].lower() or 
                           query_lower in r['content'].lower() or 
                           query_lower in r['snippet'].lower()]
    
    return filtered_results

# This function can be imported and used in the main application
if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Advanced Legal Search")
    advanced_search_tab()