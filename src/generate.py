import openai
from retrieval import get_all_related_data, classify, directClassify
from dotenv import load_dotenv
import os


load_dotenv()

api_key = os.getenv("emailWriterAI")


# Domain: Email
# Range: Email Draft
def createEmailDraft(email):
    catagory = directClassify(email)  # Pass email as a dictionary
    print(catagory)

    background = str(get_all_related_data(catagory))

    openai.api_key = api_key

    prompt = """
        1.	Read the email that needs a response.
        2.	Look at the example cases provided.
                These are examples of how others have replied in similar situations.
                Figure out how you will respond, will you accept the offer or decline it using past history?
        3.	Use those examples to understand:
                What kind of information to include.
                The tone and style of the response.
        4.	Write a clear and polite reply based on what you learned. 
        5.	Keep your response helpful and relevant.
        6.  Make sure all the information is accurate and only comes from the original email. rather than the examples.
        7.  The output should be a draft of the email response in a list format , it should be targetEmail,subject,body
        8.  If the email seems like junk, too good to be true eg: "you won a $ dollars", or a scam, do not respond and just type "Ignore".
        9. If the category is spam, the draft should be "Ignore".

        Focus on keeping your response helpful and relevant. """

    try:
        # Chat Completion request
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt + "\n\n" + background},
                {"role": "user", "content": email},
            ],
        )

        draft = completion.choices[0].message["content"].strip()

        return draft

    except Exception as e:
        print(f"Error categorizing email: {e}")


# test_email = """
#     From: contact@company.com
#     Subject: New Volunteering Opportunity
#     Body: We would like to discuss you volunteering with us.
# """


# draft = createEmailDraft(test_email)
