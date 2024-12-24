import openai
from retrieval import get_all_related_data, classify, directClassify
from dotenv import load_dotenv
import os
from generate import createEmailDraft


load_dotenv()

api_key = os.getenv("emailPolishAI")


# Domain: Email needing response
# Range: Email Final Product
def createEmailFinal(email):
    emailDraft = createEmailDraft(email)
    print(emailDraft)

    openai.api_key = api_key

    prompt = """
    Read the email sent to you and the corresponding draft response. 
    Ensure the draft strictly aligns with and reflects only the information provided in the email. 
    If any part of the draft includes details not mentioned in the email, revise it to accurately mirror the email content.
    If the email seems like junk, or the draft says Ignore, too good to be true, or a scam, do not respond and just type "Ignore"."""
    try:
        # Chat Completion request
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt + "\n\n" + email},
                {"role": "user", "content": emailDraft},
            ],
        )

        final = completion.choices[0].message["content"].strip()

        return final

    except Exception as e:
        print(f"Error categorizing email: {e}")
