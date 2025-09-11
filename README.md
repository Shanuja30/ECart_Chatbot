# EcoCart Online Chatbot

## Project Overview
**EcoCart Online** is a sustainable e-commerce platform offering eco-friendly products with a focus on convenience, customer trust, and environmental responsibility.  
This project features an **AI-powered chatbot** that provides instant customer support, helping users with queries related to orders, shipping, refunds, exchanges, warranties, and sustainability practices, enhancing the overall shopping experience.

## Features
- AI-powered chatbot for instant customer support
- Handles queries on orders, shipping, refunds, exchanges, warranties, and sustainability
- Fast, accurate, and interactive responses
- Can be integrated with EcoCart Online website

## Technologies Used
- **Backend:** Python, FastAPI
- **Frontend:** React.js / Streamlit
- **AI/ML:** NLP-based chatbot responses
- **Database:** SQLite / PostgreSQL (if applicable)
- **Other:** Git, GitHub, `.env` for environment variables

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/EcoCart_Chatbot.git
2. Navigate to the project folder:
   cd EcoCart_Chatbot
3. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
4. Install dependencies:
   pip install -r requirements.txt
5. Add your API keys or environment variables in a .env file.
   Usage
   Run the backend server:
   python -m uvicorn app:app --reload
   Run the frontend (React.js):
   npm install
   npm start
   Interact with the chatbot through the website interface or Streamlit app.