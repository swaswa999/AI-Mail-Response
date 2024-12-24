from polish import createEmailFinal


# This is a example case for testing and to view the output of the program

test_email1 = """
    From: volunteer@nonprofit.org
    Subject: Interested in Volunteering
    Body: I recently came across your organization Swayam and am interested in learning more about how I can get involved as a volunteer. Could you please provide more information about the available opportunities and the process for signing up?
"""
test_email2 = """
    From: clientservices@business.com
    Subject: Schedule a Call to Discuss Services
    Body: We are interested in your consulting services swayam and would like to schedule a call to discuss our needs in detail. Are you available for a 30-minute meeting next week? Please let me know your availability.
"""

test_email3 = """
    From: applicant@jobsearch.com
    Subject: Follow-up on Job Application
    Body: I hope this email finds you well. I applied for the Software Developer role on November 20th and wanted to follow up to see if there is any update on the hiring process. Please let me know if additional information is required swayam.
"""

test_email_junk = """
    From: winner@luckydrawpromo.com
    Subject: You Won $1 Million!
    Body: Congratulations! You’ve been selected as the winner of our $1 million jackpot. To claim your prize, reply with your name, address, and bank details. Act fast – this offer expires in 24 hours!
"""

email4 = createEmailFinal(test_email_junk)
email1 = createEmailFinal(test_email1)
email2 = createEmailFinal(test_email2)
email3 = createEmailFinal(test_email3)
