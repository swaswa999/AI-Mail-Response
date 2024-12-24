# AI Mail Response

A project to retrieve emails from the inbox and respond using past examples

**Setup**

1. setup Virtual Environment
   python3 -m venv venv
   source venv/bin/activate
2. Install Dependencies
   pip install -r requirements.txt

3. Setup google auth

4. Run mailSorter

5. Open scripts and run
   python tester.py //this is just as an example

**Structure**
AI-Mail-Response/
│
├── src/  
│ ├── **init**.py  
│ ├── generate.py # Generate mail
│ ├── mailSorter.py # Sort previous mail
│ └── polish.py # Check output is ready to send
│ └── retrieval.py # Retrieve relevant mail from database and give to create mail
│ └── tester.py # Used to test application
├── .gitignore  
├── .env  
├── README.md  
├── .gitignore
└──requirements.txt
