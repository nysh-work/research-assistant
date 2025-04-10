import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# --- Legal Deadline Tracker Tool ---
# This tool helps legal professionals track important deadlines and dates

def deadline_tracker_tab():
    """Render the deadline tracker tab in the Streamlit app."""
    st.header("📅 Legal Deadline Tracker")
    st.info("Track important legal deadlines, court dates, and compliance timelines.", icon="💡")
    
    # Initialize session state for deadlines if not already done
    if 'deadlines' not in st.session_state:
        st.session_state.deadlines = load_deadlines()
    
    # Create tabs for different deadline tracker features
    tracker_tabs = st.tabs(["Calendar View", "Add/Edit Deadlines", "Deadline List"])
    
    # Tab 1: Calendar View
    with tracker_tabs[0]:
        st.subheader("Calendar View")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.datetime.now().date(),
                help="Select the start date for the calendar view."
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=(datetime.datetime.now() + datetime.timedelta(days=30)).date(),
                help="Select the end date for the calendar view."
            )
        
        # Filter deadlines by date range
        filtered_deadlines = []
        for deadline in st.session_state.deadlines:
            deadline_date = datetime.datetime.strptime(deadline['date'], '%Y-%m-%d').date()
            if start_date <= deadline_date <= end_date:
                filtered_deadlines.append(deadline)
        
        if filtered_deadlines:
            # Create a timeline chart
            df = pd.DataFrame(filtered_deadlines)
            df['date'] = pd.to_datetime(df['date'])
            df['days_remaining'] = (df['date'] - pd.Timestamp.now()).dt.days
            
            # Color based on priority and days remaining
            df['color'] = 'blue'  # Default color
            df.loc[df['priority'] == 'High', 'color'] = 'red'
            df.loc[df['priority'] == 'Medium', 'color'] = 'orange'
            df.loc[df['priority'] == 'Low', 'color'] = 'green'
            
            # Create a Gantt chart
            fig = px.timeline(
                df,
                x_start='date',
                y='title',
                color='priority',
                hover_data=['description', 'days_remaining'],
                labels={'title': 'Deadline', 'date': 'Date', 'priority': 'Priority'},
                color_discrete_map={'High': 'red', 'Medium': 'orange', 'Low': 'green'}
            )
            
            # Add a vertical line for today
            fig.add_vline(
                x=datetime.datetime.now(),
                line_width=2,
                line_dash="dash",
                line_color="black",
                annotation_text="Today"
            )
            
            # Update layout
            fig.update_layout(
                title="Upcoming Deadlines",
                xaxis_title="Date",
                yaxis_title="Deadline",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show upcoming deadlines in the next 7 days
            upcoming_deadlines = [d for d in filtered_deadlines if (datetime.datetime.strptime(d['date'], '%Y-%m-%d').date() - datetime.datetime.now().date()).days <= 7 and (datetime.datetime.strptime(d['date'], '%Y-%m-%d').date() - datetime.datetime.now().date()).days >= 0]
            
            if upcoming_deadlines:
                st.subheader("⚠️ Upcoming Deadlines (Next 7 Days)")
                for deadline in upcoming_deadlines:
                    days_remaining = (datetime.datetime.strptime(deadline['date'], '%Y-%m-%d').date() - datetime.datetime.now().date()).days
                    
                    # Determine color based on priority
                    color = "green"
                    if deadline['priority'] == "High":
                        color = "red"
                    elif deadline['priority'] == "Medium":
                        color = "orange"
                    
                    with st.container(border=True):
                        col1, col2 = st.columns([0.7, 0.3])
                        with col1:
                            st.markdown(f"**{deadline['title']}**")
                            st.markdown(f"*{deadline['description']}*")
                        with col2:
                            st.markdown(f"**Date:** {deadline['date']}")
                            st.markdown(f"**Days Left:** {days_remaining}")
                            st.markdown(f"**Priority:** <span style='color:{color};'>{deadline['priority']}</span>", unsafe_allow_html=True)
        else:
            st.info("No deadlines found in the selected date range.", icon="ℹ️")
    
    # Tab 2: Add/Edit Deadlines
    with tracker_tabs[1]:
        st.subheader("Add New Deadline")
        
        with st.container(border=True):
            # Form for adding a new deadline
            deadline_title = st.text_input("Title", help="Enter a title for the deadline.")
            deadline_description = st.text_area("Description", help="Enter a description for the deadline.")
            deadline_date = st.date_input("Date", help="Select the deadline date.")
            deadline_priority = st.selectbox(
                "Priority",
                options=["High", "Medium", "Low"],
                index=1,
                help="Select the priority level for this deadline."
            )
            deadline_category = st.selectbox(
                "Category",
                options=["Court Filing", "Client Meeting", "Document Submission", "Hearing", "Compliance", "Other"],
                index=0,
                help="Select a category for this deadline."
            )
            deadline_notes = st.text_area("Additional Notes", help="Enter any additional notes or reminders.")
            
            # Add deadline button
            add_button = st.button(
                "Add Deadline",
                use_container_width=True,
                disabled=(not deadline_title or not deadline_date)
            )
            
            if add_button and deadline_title and deadline_date:
                new_deadline = {
                    "id": len(st.session_state.deadlines) + 1,
                    "title": deadline_title,
                    "description": deadline_description,
                    "date": deadline_date.strftime("%Y-%m-%d"),
                    "priority": deadline_priority,
                    "category": deadline_category,
                    "notes": deadline_notes
                }
                
                st.session_state.deadlines.append(new_deadline)
                save_deadlines(st.session_state.deadlines)
                
                st.success(f"✅ Deadline '{deadline_title}' added successfully!", icon="✅")
                st.rerun()
        
        st.divider()
        
        st.subheader("Edit or Delete Deadlines")
        
        if st.session_state.deadlines:
            # Select a deadline to edit
            deadline_options = [f"{d['title']} ({d['date']})" for d in st.session_state.deadlines]
            selected_deadline_index = st.selectbox(
                "Select a deadline to edit or delete",
                options=range(len(deadline_options)),
                format_func=lambda x: deadline_options[x],
                help="Select a deadline to edit or delete."
            )
            
            selected_deadline = st.session_state.deadlines[selected_deadline_index]
            
            with st.container(border=True):
                # Form for editing the selected deadline
                edit_title = st.text_input("Title", value=selected_deadline['title'], key="edit_title")
                edit_description = st.text_area("Description", value=selected_deadline['description'], key="edit_description")
                edit_date = st.date_input(
                    "Date",
                    value=datetime.datetime.strptime(selected_deadline['date'], '%Y-%m-%d').date(),
                    key="edit_date"
                )
                edit_priority = st.selectbox(
                    "Priority",
                    options=["High", "Medium", "Low"],
                    index=["High", "Medium", "Low"].index(selected_deadline['priority']),
                    key="edit_priority"
                )
                edit_category = st.selectbox(
                    "Category",
                    options=["Court Filing", "Client Meeting", "Document Submission", "Hearing", "Compliance", "Other"],
                    index=["Court Filing", "Client Meeting", "Document Submission", "Hearing", "Compliance", "Other"].index(selected_deadline['category']) if selected_deadline.get('category') in ["Court Filing", "Client Meeting", "Document Submission", "Hearing", "Compliance", "Other"] else 0,
                    key="edit_category"
                )
                edit_notes = st.text_area("Additional Notes", value=selected_deadline.get('notes', ''), key="edit_notes")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Update deadline button
                    update_button = st.button(
                        "Update Deadline",
                        use_container_width=True,
                        disabled=(not edit_title or not edit_date)
                    )
                
                with col2:
                    # Delete deadline button
                    delete_button = st.button(
                        "Delete Deadline",
                        use_container_width=True,
                        type="primary",
                        help="Delete this deadline permanently."
                    )
            
            if update_button and edit_title and edit_date:
                # Update the deadline
                st.session_state.deadlines[selected_deadline_index] = {
                    "id": selected_deadline['id'],
                    "title": edit_title,
                    "description": edit_description,
                    "date": edit_date.strftime("%Y-%m-%d"),
                    "priority": edit_priority,
                    "category": edit_category,
                    "notes": edit_notes
                }
                
                save_deadlines(st.session_state.deadlines)
                st.success(f"✅ Deadline '{edit_title}' updated successfully!", icon="✅")
                st.rerun()
            
            if delete_button:
                # Delete the deadline
                del st.session_state.deadlines[selected_deadline_index]
                save_deadlines(st.session_state.deadlines)
                st.success(f"🗑️ Deadline deleted successfully!", icon="🗑️")
                st.rerun()
        else:
            st.info("No deadlines available to edit. Add a deadline first.", icon="ℹ️")
    
    # Tab 3: Deadline List
    with tracker_tabs[2]:
        st.subheader("All Deadlines")
        
        if st.session_state.deadlines:
            # Filter options
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                filter_priority = st.multiselect(
                    "Filter by Priority",
                    options=["High", "Medium", "Low"],
                    default=[],
                    help="Select priorities to filter by."
                )
            
            with filter_col2:
                filter_category = st.multiselect(
                    "Filter by Category",
                    options=["Court Filing", "Client Meeting", "Document Submission", "Hearing", "Compliance", "Other"],
                    default=[],
                    help="Select categories to filter by."
                )
            
            # Apply filters
            filtered_deadlines = st.session_state.deadlines
            if filter_priority:
                filtered_deadlines = [d for d in filtered_deadlines if d['priority'] in filter_priority]
            if filter_category:
                filtered_deadlines = [d for d in filtered_deadlines if d.get('category', 'Other') in filter_category]
            
            # Sort options
            sort_by = st.selectbox(
                "Sort by",
                options=["Date (Ascending)", "Date (Descending)", "Priority (High to Low)", "Priority (Low to High)"],
                index=0,
                help="Select how to sort the deadlines."
            )
            
            # Sort deadlines
            if sort_by == "Date (Ascending)":
                filtered_deadlines = sorted(filtered_deadlines, key=lambda x: x['date'])
            elif sort_by == "Date (Descending)":
                filtered_deadlines = sorted(filtered_deadlines, key=lambda x: x['date'], reverse=True)
            elif sort_by == "Priority (High to Low)":
                priority_order = {"High": 0, "Medium": 1, "Low": 2}
                filtered_deadlines = sorted(filtered_deadlines, key=lambda x: priority_order[x['priority']])
            elif sort_by == "Priority (Low to High)":
                priority_order = {"High": 2, "Medium": 1, "Low": 0}
                filtered_deadlines = sorted(filtered_deadlines, key=lambda x: priority_order[x['priority']])
            
            # Display deadlines as a table
            if filtered_deadlines:
                # Convert to DataFrame for display
                df_display = pd.DataFrame(filtered_deadlines)
                df_display['date'] = pd.to_datetime(df_display['date']).dt.strftime('%Y-%m-%d')
                
                # Calculate days remaining
                today = datetime.datetime.now().date()
                df_display['days_remaining'] = df_display['date'].apply(
                    lambda x: (datetime.datetime.strptime(x, '%Y-%m-%d').date() - today).days
                )
                
                # Select columns to display
                display_cols = ['title', 'description', 'date', 'days_remaining', 'priority', 'category']
                if 'notes' in df_display.columns:
                    display_cols.append('notes')
                
                # Rename columns for display
                df_display = df_display[display_cols].rename(columns={
                    'title': 'Title',
                    'description': 'Description',
                    'date': 'Date',
                    'days_remaining': 'Days Remaining',
                    'priority': 'Priority',
                    'category': 'Category',
                    'notes': 'Notes'
                })
                
                # Display the table
                st.dataframe(df_display, use_container_width=True)
                
                # Export options
                export_format = st.selectbox(
                    "Export Format",
                    options=["CSV", "Excel", "JSON"],
                    index=0,
                    help="Select the format to export deadlines."
                )
                
                export_button = st.button(
                    "Export Deadlines",
                    use_container_width=True
                )
                
                if export_button:
                    if export_format == "CSV":
                        csv = df_display.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="legal_deadlines.csv",
                            mime="text/csv"
                        )
                    elif export_format == "Excel":
                        # Create Excel file in memory
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_display.to_excel(writer, sheet_name='Deadlines', index=False)
                        excel_data = output.getvalue()
                        st.download_button(
                            label="Download Excel",
                            data=excel_data,
                            file_name="legal_deadlines.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    elif export_format == "JSON":
                        json_str = json.dumps(filtered_deadlines, indent=4)
                        st.download_button(
                            label="Download JSON",
                            data=json_str,
                            file_name="legal_deadlines.json",
                            mime="application/json"
                        )
            else:
                st.info("No deadlines match the selected filters.", icon="ℹ️")
        else:
            st.info("No deadlines available. Add a deadline in the 'Add/Edit Deadlines' tab.", icon="ℹ️")

def load_deadlines():
    """Load deadlines from a JSON file."""
    try:
        # Check if the deadlines file exists
        if os.path.exists("legal_deadlines.json"):
            with open("legal_deadlines.json", "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading deadlines: {e}", icon="❗")
        return []

def save_deadlines(deadlines):
    """Save deadlines to a JSON file."""
    try:
        with open("legal_deadlines.json", "w") as f:
            json.dump(deadlines, f, indent=4)
    except Exception as e:
        st.error(f"Error saving deadlines: {e}", icon="❗")

# This function can be imported and used in the main application
if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Legal Deadline Tracker")
    deadline_tracker_tab()