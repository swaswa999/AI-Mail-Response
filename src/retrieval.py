import openai
import sqlite3
from dotenv import load_dotenv
from mailSorter import store_email_in_db
import os

load_dotenv()

api_key = os.getenv("lableAI")


# Domain: Email
# Range: Category of the email
def classify(email):
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
        '"Meeting_request". If it is spam or unrelated, categorize as "SPAM" If you see that there is no response back, and it seems automated classify as SPAM. Only reply '
        "with the single-word category (e.g., Internship_request)."
    )

    try:
        # Chat Completion request
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": email_summary},
            ],
        )

        category = completion.choices[0].message["content"].strip()
        if category != "SPAM":
            store_email_in_db([email], category)

            with open("categories.txt", "a") as file:
                file.write(category + "\n")

            return category

    except Exception as e:
        print(f"Error categorizing email: {e}")


# Domain: Category of the email
# Range: List of emails in the category
def get_emails_by_category(category):
    conn = sqlite3.connect("emails.db")
    c = conn.cursor()

    try:
        # SQL query to retrieve emails matching the category
        c.execute(
            """
            SELECT thread_id, from_email, subject, date, body
            FROM email_threads
            WHERE category = ?
            """,
            (category,),
        )
        # Fetch all results and format them as a list of dictionaries
        email_list = [
            {
                "From": row[1],
                "Subject": row[2],
                "Body": row[4],
            }
            for row in c.fetchall()
        ]
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving emails: {e}")
        email_list = []

    conn.close()
    return email_list


# Domain: Category of the target email
# Range: List of similar categories
def get_similar_categories(original_category):
    with open("categories.txt", "r") as file:
        categories = file.readlines()

    categories = list(set(categories))
    categories_str = ", ".join(categories)

    openai.api_key = api_key

    # Categorization prompt
    prompt = (
        """You have access to different categories of emails. 
        Given an original category, your task is to select a list of categories that you feel would be useful in learning how to write about this category—focus on the writing style rather than the subject matter. 
        For example, if the original category is ‘Internship_Requests’, look for similar categories like ‘Job_Requests’ or other professional communication categories that can help in writing about internship requests. 
        You may select up to 2 categories, but if the original category is very similar or the same to one category in the provided list, you should choose just one. Here is the original category: """
        + original_category
        + "The output should be in a systematic list separated by commas."
    )

    try:
        # Chat Completion request
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": categories_str},
            ],
        )

        category = completion.choices[0].message["content"].strip()
        categories_list = category.split(", ")

        return categories_list

    except Exception as e:
        print(f"Error Finding List: {e}")


# Domain: Category of the target email
# Range: List of emails in similar categories
def get_all_related_data(original_category):
    similar_categories = get_similar_categories(original_category)

    fullData = []

    for category in similar_categories:
        email_list = get_emails_by_category(category)
        fullData.append(email_list)
    return fullData


# Domain: Email as str
# Range: Category of the email
def directClassify(email):
    openai.api_key = api_key

    # Categorization prompt
    prompt = (
        "You have access to an email thread. Use the first email as context and "
        'categorize it. Examples: "Internship_request", "Potential_client", "Job_offer", '
        '"Meeting_request". Only reply '
        "with the single-word category (e.g., Internship_request)."
    )

    try:
        # Chat Completion request
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": email},
            ],
        )

        category = completion.choices[0].message["content"].strip()
        if category != "SPAM":
            return category

    except Exception as e:
        print(f"Error categorizing email: {e}")
