import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from bs4 import BeautifulSoup
import openai
import sqlite3
from dotenv import load_dotenv

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

catagories = []

load_dotenv()

api_key = os.getenv("lableAI")


# Domain: None
# Range : List of email threads
def getAllEmail():
    """Shows basic usage of the Gmail API.
    Lists the user's email threads and prints the full history of each conversation.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)

    # Call the Gmail API to list threads
    results = service.users().threads().list(userId="me").execute()
    threads = results.get("threads", [])

    if not threads:
        print("No threads found.")
    else:
        print("Threads:")
        email_list = []
        for thread in threads:
            thread_id = thread["id"]
            thread_details = (
                service.users().threads().get(userId="me", id=thread_id).execute()
            )
            messages = thread_details.get("messages", [])
            for message in messages:
                headers = message["payload"]["headers"]
                subject = next(
                    header["value"] for header in headers if header["name"] == "Subject"
                )
                from_ = next(
                    header["value"] for header in headers if header["name"] == "From"
                )
                date = next(
                    header["value"] for header in headers if header["name"] == "Date"
                )

                # Extract the message body
                parts = message["payload"].get("parts", [])
                body = ""
                if not parts:
                    body = message["payload"]["body"].get("data", "")
                else:
                    for part in parts:
                        if part["mimeType"] == "text/plain":
                            body = part["body"].get("data", "")
                            break
                        elif part["mimeType"] == "text/html":
                            body = part["body"].get("data", "")

                if body:
                    body = base64.urlsafe_b64decode(body).decode("utf-8")
                    soup = BeautifulSoup(body, "html.parser")
                    body_text = soup.get_text()
                else:
                    body_text = "No body found."

                email_list.append(
                    {
                        "Thread ID": thread_id,
                        "From": from_,
                        "Subject": subject,
                        "Date": date,
                        "Body": body_text,
                    }
                )
        return email_list


#  Domain: None
#  Range: creates DB if not exists
def create_db():
    conn = sqlite3.connect("emails.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS email_threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT NOT NULL,
            category TEXT NOT NULL,
            from_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            date TEXT NOT NULL,
            body TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


# Domain: List of email threads and category
# Range: Stores email threads in the database
def store_email_in_db(email_list, category):
    conn = sqlite3.connect("emails.db")
    c = conn.cursor()
    for email in email_list:
        c.execute(
            """
            INSERT INTO email_threads (thread_id, category, from_email, subject, date, body)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                email["Thread ID"],
                category,
                email["From"],
                email["Subject"],
                email["Date"],
                email["Body"],
            ),
        )
    conn.commit()
    conn.close()


def categorize_mail(email_list):
    for email in email_list:
        openai.api_key = api_key

        # Structured input for categorization
        email_summary = f"""
        From: {email['From']}
        Subject: {email['Subject']}
        Body: {email['Body']}
        """

        # Categorization prompt
        prompt = (
            "You have access to an email thread. Use the first email as context and "
            'categorize it. Examples: "Internship_request", "Potential_client", "Job_offer", '
            '"Meeting_request". If it is spam or unrelated, categorize as "SPAM". Only reply '
            "with the single-word category (e.g., Internship_request)."
        )

        try:
            # Chat Completion request
            completion = openai.ChatCompletion.create(
                model="gpt-4o-mini-2024-07-18:personal::AhqgNSul 12/23/2024, 7:36 PM",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": email_summary},
                ],
            )

            category = completion.choices[0].message["content"].strip()
            if category != "SPAM":
                catagories.append(category)
                # Store the categorized email in the database
                store_email_in_db([email], category)

        except Exception as e:
            print(f"Error categorizing email: {e}")
            continue

    print("Categories:", catagories)
    # Save categories to a text file
    with open("categories.txt", "w") as file:
        file.write("\n".join(catagories))


if __name__ == "__main__":
    create_db()
    email_list = getAllEmail()
    if email_list:
        categorize_mail(email_list)
    else:
        print("No emails to process.")
