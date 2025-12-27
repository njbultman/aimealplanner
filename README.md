aimealplanner
=============

Overview
--------
aimealplanner is an agentic automation that uses OpenAI to generate weekly dinner suggestions and organize your grocery list. It monitors an email inbox for meal-planning conversations and handles three types of interactions:
- **New emails**: Generate initial meal suggestions for the week
- **Reply emails**: Answer follow-up questions about meals
- **Confirm emails**: Extract confirmed meals and organize ingredients by grocery store section

Key Files
---------
- `src/main.py` — main application logic and control flow
- `src/config.py` — static configuration, model settings, and favorite meals list
- `src/email_utils.py` — IMAP/SMTP helpers and email utilities
- `src/llm_utils.py` — LLM agent functions for meal generation, categorization, and ingredient organization
- `data/state.json` — runtime state (last-checked time, latest subject, meal history)

Environment & Setup
-------------------
1. Create and activate a Python virtual environment.
2. Install required packages: `openai` (and any other dependencies in `src/`)
3. Provide these environment variables:
   - `IMAP_HOST` — IMAP server host
   - `SMTP_HOST` — SMTP server host
   - `SMTP_PORT` — SMTP port (integer)
   - `EMAIL` — the sending/receiving email address
   - `EMAIL_APP_PASSWORD` — app-specific password for SMTP/IMAP authentication
   - `OPENAI_API_KEY` — OpenAI API key
4. Adjust `meal_favorites_list` in `config.py` to your preferences
5. Adjust the context for `agent_extract_organize_ingredients_list` in `llm_utils.py` to account for your grocery store setup.

Getting Started
-------
First, send an email to the same `EMAIL` defined in the environment variables with the subject "Meal Planning - YYYY-MM-DD" and substituting the date with the current date (or your date of choice).

Then, `cd` into the `src` folder and run the main script with the virtual environment activated:

```bash
source venv/bin/activate
cd src
python main.py
```

This will reply to your original email with seven meal suggestions. From here, you can reply to that email with additional questions ("can we swap out this meal?" or "can we add this meal?") and run the same script.

Once you are satisfied with the meals, reply to the email along the lines of "Confirming meals and grocery list" with two lists: (1) Meal list, which will have the meals chosen for the week and (2) the grocery list, which will have all the items needed from the grocery store for those meals (and more if necessary). Finally, run `main.py` again for the process to receive an email confirming meals and organizing your grocery list.

Once you feel comfortable with the process, you can schedule this to run periodically (for example, every five minutes via cron). The script will only call OpenAI when it detects a reply is needed (when a new email or reply is sent), which ensures that costs will remain low.

More specifics on the process are below (after the "Notes" section).

Notes
-----
- This has been tested with Gmail on a Raspberry Pi using the GPT 4o Mini model
- While environment variables can be overwritten in `config.py` and use hard-coded variables, this is strongly discouraged for security reasons
- While any model can be used from OpenAI by adjusting the `model_name` in `config.py`, to keep costs low it is recommended to use smaller models as the tasks are not extremely complex.
- Here is an example configuration for the process to run every five minutes Fri-Sun from 5AM - 10PM.
```bash
crontab -e
*/5 5-22 * * 5,6,0 . PATH/TO/PROJECT/aimealplanner/venv/bin/activate && cd PATH/TO/PROJECT/aimealplanner/src && PATH/TO/PROJECT/aimealplanner/venv/bin/python main.py > /dev/null 2>&1
```


Behavior & Email Flow
---------------------

### Email Categorization
The app checks for new or reply emails with the subject "Meal Planning -" and categorizes incoming messages as:
- **"new"**: No prior conversation (blank or "N/A" body) — generates initial meal suggestions
- **"confirm"**: User confirms meals and provides ingredients — extracts and organizes groceries
- **"reply"**: User asks a follow-up question — generates a response using meal planning agents

### New Email ("new")
When a new email is detected, the application:
1. Calls `agent_generate_meals()` to suggest seven dinners for the week
2. Uses the user's favorite meals list from `config.py` as inspiration (must include 2 meals not in the list)
3. Sends the suggestions back via email in the format:
   ```
   Day 1: <Meal Suggestion>
   Day 2: <Meal Suggestion>
   ...
   Day 7: <Meal Suggestion>
   ```

### Confirm Email ("confirm")
When the user confirms meals and provides an ingredient list, the application:
1. Calls `agent_extract_meals()` to extract the confirmed meal list
2. Calls `agent_extract_organize_ingredients_list()` to extract/organize ingredients by store section
3. Sends a reply with:
   - **Confirmed Meals**: A formatted bullet list of selected meals
   - **Organized Grocery List**: A nested bulleted list organized by store sections (which can be adjusted depending on needs):
     - Produce
     - Dessert
     - Meat
     - Bakery
     - Pasta
     - Ethnic
     - Coffee/Canned Goods
     - Dairy
     - Snacks
     - Cleaners and Toilet Paper
     - Frozen

### Reply Email ("reply")
When the user asks a follow-up question, the application:
1. Calls `agent_generate_meals()` with the user's message
2. Generates a contextual response
3. Sends the reply back via email

### State Management
After each execution, the app updates `state.json` with:
- `last_checked_datetime` — timestamp of the last run (used to avoid reprocessing and unnecessary OpenAI calls)
- `latest_email_subject` — the current meal planning thread subject
- `latest_meal_history` — confirmed meals from the most recent confirmation
