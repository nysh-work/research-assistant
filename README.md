# CA Research Assistant

A powerful AI-powered research assistant for chartered accountants and legal professionals, built with Streamlit and Google's Gemini AI.

![CA Research Assistant](https://img.shields.io/badge/CA%20Research%20Assistant-v1.0-blue)

## Overview

This application provides chartered accountants and legal professionals with an AI-powered tool to assist with legal research, case law searches, and legal provision lookups. It features a modern, user-friendly interface built with Streamlit and leverages Google's Gemini AI for intelligent responses.

The application includes several specialized tools to enhance legal research and practice management:

- **Document Comparison Tool**: Compare two legal documents and visualize the differences
- **Legal Citation Generator**: Create properly formatted citations for various legal references
- **Tax Calculator**: Calculate income tax liability and compare different tax scenarios
- **Legal Deadline Tracker**: Track important legal deadlines, court dates, and compliance timelines
- **Advanced Legal Search**: Search for legal information with filters by jurisdiction, date range, and legal domain

## Features

### 📄 Document Upload and Analysis
- Upload PDF, DOCX, and TXT files for context
- Automatic text extraction from documents
- Document management with ability to remove files

### 💬 General Legal Chat
- Ask general legal questions with AI-powered responses
- Context-aware responses based on uploaded documents
- Streaming responses for better user experience
- Persistent chat history during session

### 🔎 Case Law Search
- Search for Indian case laws by name and year
- AI-generated summaries of case details
- Key judgment points and legal interpretations

### 📜 Legal Provision Lookup
- Search for legal provisions by section number or keyword
- Structured responses with act details, notes, and key aspects
- Related case law references

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd research-assistant
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Gemini API key:
   - Create a `.streamlit/secrets.toml` file in the project directory
   - Add your Gemini API key to the file:
     ```
     GEMINI_API_KEY = "your-api-key-here"
     ```
   - You can obtain a Gemini API key from [Google AI Studio](https://ai.google.dev/)

## Usage

1. Start the application:
   ```
   streamlit run legal_chatbot.py
   ```

2. Access the application in your web browser at `http://localhost:8501`

3. Use the different tabs to access various features:
   - **Upload Files**: Add documents to provide context for your queries
   - **General Chat**: Ask general legal questions
   - **Case Law Search**: Find and summarize case laws
   - **Legal Provisions**: Look up specific legal provisions

## Application Structure

- `legal_chatbot.py`: Main application file
- `requirements.txt`: List of required Python packages
- `.streamlit/secrets.toml`: Configuration file for API keys (you need to create this)

## Dependencies

- `streamlit`: Web application framework
- `google-generativeai`: Google's Generative AI API client
- `PyPDF2`: PDF file processing
- `python-docx`: DOCX file processing

## Notes

- The application requires a valid Gemini API key to function properly
- Document processing capabilities depend on the installed libraries (PyPDF2, python-docx)
- The application is designed for Indian legal research but can be adapted for other jurisdictions

## License

This project is licensed under the terms of the license included with this software.

---

Built with ❤️ for chartered accountants and legal professionals