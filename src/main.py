# ----- Imports -----
import email_utils
import llm_utils
import config
import json
import datetime
from zoneinfo import ZoneInfo

# ----- Configuration -----

# Define variables from static config
user_email = config.email
email_app_password = config.email_app_password
model_name = config.model_name
state_json_file = config.state_json_file
imap_host = config.imap_host
smtp_host = config.smtp_host
smtp_port = config.smtp_port

# Read in the JSON state file and grab relevant objects
with open(config.state_json_file, "r") as f:
    state_json = json.load(f)
    last_checked_datetime = state_json.get("last_checked_datetime")
    latest_email_subject = state_json.get("latest_email_subject")
    latest_meal_history = state_json.get("latest_meal_history")

# Instantiate the latest user prompt -> inject latest meal history as well
user_prompt = f"""
Can you help me plan my meals for the week? The conversation history is enclosed in
"###". Also, the meals I recently had are as follows and should NOT be one of the
meal suggestions: {latest_meal_history}.
Here is the conversation history: ###
"""

# ----- Main Flow -----
    
# First, check to see if there has been a reply on the last email subject sent since the last checked datetime
reply_search = email_utils.build_search_query(subject=latest_email_subject, from_email=user_email)
reply = email_utils.get_reply_history(imap_host, user_email, email_app_password, reply_search, last_checked_datetime)
latest_conversation_body = reply.get("latest_conversation_body", "N/A")

# If no reply found ("N/A"), check for any new emails with a subject date greater than the last checked datetime and not containing "Re:" (a reply)
if latest_conversation_body == "N/A" or latest_conversation_body == "":
    print("Checking for any new emails...")
    new_subject_date_search = datetime.datetime.now(tz=ZoneInfo("America/Chicago")).strftime("%d-%b-%Y")
    new_email_search = email_utils.build_search_query(subject="Meal Planning -", since=new_subject_date_search, from_email=user_email)
    new_subject = email_utils.get_new_email(imap_host, user_email, email_app_password, last_checked_datetime, new_email_search)
    # If a new email is found that does not have "Re:", reply to it
    if new_subject is not None and not new_subject.lower().startswith("re:"):
        print("New email found! Replying to it...")
        # Update the latest email subject JSON
        state_json["latest_email_subject"] = new_subject
        # Update the latest email subject
        latest_email_subject = new_subject
    else:
        print("No new emails found. Exiting...")
        exit()
# Categorize email
category = llm_utils.agent_categorize_reply(model_name, latest_conversation_body, latest_email_subject)
if category == "new":
    # Get first meal suggestions from agent
    first_suggestions = llm_utils.agent_generate_meals(model_name, user_prompt + "N/A###")
    # Send reply email with meal suggestions
    new_subject_search = email_utils.build_search_query(subject=new_subject, from_email=user_email)
    email_utils.reply_to_subject(imap_host, smtp_host, smtp_port, user_email, email_app_password, new_subject_search, first_suggestions)
elif category == "confirm":
    # Call agent to confirm meals and organize grocery list
    llm_meals_text = llm_utils.agent_extract_meals(model_name, latest_conversation_body)
    llm_ingredients_text = llm_utils.agent_extract_organize_ingredients_list(model_name, latest_conversation_body)
    meals_json = json.loads(llm_meals_text)
    latest_meal_history = meals_json.get("meal_list")
    # Update state JSON with confirmed meals
    state_json["latest_meal_history"] = latest_meal_history
    # Format lists to bullet points
    meal_list_text = email_utils.format_list_to_bullets(latest_meal_history)
    # Send reply email with confirmed meals and organized grocery list
    reply_text = f"Confirmed Meals:\n{meal_list_text}\n\nOrganized Grocery List:\n{llm_ingredients_text}"
    email_utils.reply_to_subject(imap_host, smtp_host, smtp_port, user_email, email_app_password, reply_search, reply_text)
elif category == "reply":
    # Get reply from agent based on latest conversation body
    conversation_reply = llm_utils.agent_generate_meals(model_name, latest_conversation_body)
    # Send reply email
    email_utils.reply_to_subject(imap_host, smtp_host, smtp_port, user_email, email_app_password, reply_search, conversation_reply)

# Update last checked datetime in state JSON
current_checked_datetime = datetime.datetime.now(tz=ZoneInfo("America/Chicago"))
current_iso = current_checked_datetime.isoformat()
state_json["last_checked_datetime"] = current_iso

# Dump reply to JSON state file
with open(config.state_json_file, "w") as f:
    json.dump(state_json, f)