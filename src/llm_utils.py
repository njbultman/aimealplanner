# Import packages
from openai import OpenAI
import config

# Define agent that generates meal suggestions
def agent_generate_meals(model_name, user_prompt, meal_favorites_list=config.meal_favorites_list):
    client = OpenAI()
    messages = [
        {"role": "system", "content": f"""
        You are a meal-planner assistant that helps generate dinner suggestions based on
        (1) a list of favorite meals, (2) recent meal history, and (3) the conversation history (if the conversation history is present).

        Follow these rules:
        1. Do NOT list the ingredients or recipes. Only list the meal names.
        2. List a total of seven dinner suggestions, which include a main course and at least one side dish. A dish should not be repeated within the seven suggestions.
        3. No dinner suggestions should be "N/A" - they should each be a legitimate meal suggestion.
        4. If the user provides meals that they do not want, do not suggest those meals.
        5. Use meals from the favorite meals list as inspiration, but there MUST BE TWO meals that are NOT in the favorite meals list.
        6. If there is only "N/A" in conversation history, just provide seven dinner suggestions and ignore the conversation history.
        7. If there is conversation history, incorporate that into your reply.
        8. Do not say that you do not know what to suggest - always suggest meals.

        Here is the favorite meals list. Use this as meals to pick from or inspiration for similar meals but there MUST BE TWO meals that are NOT in this list:
        {meal_favorites_list}

        The format should be like below, with each meal suggestion on its own line:
        Day 1: <Meal Suggestion 1> 
        Day 2: <Meal Suggestion 2>
        ... 
        Day 7:  <Meal Suggestion 7>
        """
        },
        {"role": "user", "content": user_prompt}
    ]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return response.choices[0].message.content

# Define agent that categorizes an email
def agent_categorize_reply(model_name, latest_conversation_body, email_subject):
    client = OpenAI()
    messages = [
        {"role": "system", "content": """
        You are an email assistant that categorizes emails as follows based on the email subject and latest conversation body:
        
        (1) "new" = the conversation body is blank or "N/A".
        (2) "confirm" = the conversation body is from the user confirming the meals and ingredient list.
        (3) "reply" = a question is asked.
        
        Only return the category as a string without the double quotes (so "new" should just say new).
        
        """
        },
        {"role": "user", "content": f"Categorize the email with subject (enclosed in ###): ###{email_subject}### and conversation body (enclosed in ###): ###{latest_conversation_body}### and follow the appropriate steps."}
    ]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return response.choices[0].message.content

# Define agent taht extracts/organizes ingredients list
def agent_extract_organize_ingredients_list(model_name, latest_conversation_body):
    client = OpenAI()
    messages = [
        {"role": "system", "content": """
        You are an email assistant that categorizes an ingredients list from an email conversation and organizes it according to the following store sections.
        
        Your task is to:
        1. Extract the ingredients from the email
        2. Categorize and organize the ingredients from the first step according to these store sections (in this exact order):
            1. Produce (fruits, vegetables, salad greens) and protein shakes
            2. Dessert (desserts, pastries, sweets)
            3. Meat (beef, chicken, pork, fish, sausage, ground meat)
            4. Bakery (bread, rolls, bagels, tortillas)
            5. Pasta (pasta, noodles, rice)
            6. Ethnic (specialty ethnic foods, sauces, spices)
            7. Coffee/Canned Goods (coffee, tea, canned vegetables, canned beans, canned soups)
            8. Dairy (milk, butter, creamer, cheese, yogurt, sour cream)
            9. Snacks (chips, crackers, cookies, granola)
            10. Cleaners and Toilet Paper (cleaning supplies, toilet paper, paper towels)
            11. Frozen (frozen vegetables, frozen meals, ice cream)

        Return a bulleted list with category names as headers followed by the items in that category. Format it like this:
        - Produce
          - item1
          - item2
        - Dessert
          - item3
        - Meat
          - item4

        IMPORTANT GROCERY ITEMS INSTRUCTIONS:
        - Ensure that ALL items from the original list are included. DO NOT omit any items.
        - Only include categories that have items in them (do not list empty categories)
        - List items in the order of the sections above
        - Extract item names exactly as provided by the user
        - Use bullet points with dashes (-) for both categories and items
        - Indent items under their respective categories with two spaces

        Example grocery items organization:
        Input items: "ice cream, chicken breast, apples, milk, pasta"
        Output:
        - Produce
          - apples
        - Meat
          - chicken breast
        - Pasta
          - pasta
        - Dairy
          - milk
        - Frozen
          - ice cream
        
        """
        },
        {"role": "user", "content": f"Find and categorize/order the ingredients list from the content here: {latest_conversation_body}"}
    ]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return response.choices[0].message.content

# Define agent that extracts confirmed meals
def agent_extract_meals(model_name, latest_conversation_body):
    client = OpenAI()
    messages = [
        {"role": "system", "content": """
        You are an email assistant that extracts the confirmed meals from an email conversation and puts them in JSON format. The JSON object should have the following structure:
        
        Your task is to:
        1. Extract the confirmed meals from the email.
        2. Return a valid JSON object with this exact structure, and DO NOT include any text outside the JSON object:
            {
            "meal_list": ["meal1", "meal2", "meal3", ...]
            }
        
        """
        },
        {"role": "user", "content": f"Extract the meal list from the content here: {latest_conversation_body}"}
    ]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return response.choices[0].message.content
