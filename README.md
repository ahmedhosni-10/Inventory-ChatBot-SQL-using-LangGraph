# Inventory-ChatBot-SQL-using-LangGraph
![software engineering architectural diagram](software%20engineering%20architectural%20diagram.png)

## 1. Environment Variables
This project uses a .env file to manage sensitive API keys. To set it up:

* **Locate the .env.example file in the root directory.**

* **Create a copy of it and rename the copy to .env.**

* **Open .env and enter your credentials note i use Groq Api:**
## 2. Virtual Environment & Dependencies
To ensure all required libraries are installed correctly, run the following commands in your terminal:

* **Windows:**
Create a virtual environment
python -m venv venv
* **Activate the environment**
source venv/bin/activate
* **Install all project dependencies**
pip install -r requirements.txt

## 3.🚀 Running the Inventory Chatbot
Once your environment is set up and activated, you can start the SQL-based chatbot by running:

* **Bash**
python main.py
