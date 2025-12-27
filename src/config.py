import os
imap_host = os.getenv("IMAP_HOST")
smtp_host = os.getenv("SMTP_HOST")
smtp_port = int(os.getenv("SMTP_PORT"))
email = os.getenv("EMAIL")
email_app_password = os.getenv("EMAIL_APP_PASSWORD")
state_json_file = "../data/state.json"
model_name = "gpt-4o-mini"
meal_favorites_list = [
    "Meatball subs",
    "Pasta with red sauce and sausage",
    "Chicken caesar salad",
    "Thai peanut pasta",
    "Steak with mashed potatoes and brussel sprouts",
    "Sheet pan sausage",
    "Chicken Patties",
    "Buttered Noodles",
    "Smash Burgers",
    "BLT Sandwiches",
    "Taco bowls",
    "Huevos Rotos",
    "Pork chops with sides",
    "Bang bang chicken with rice",
    "Slow Cooker BBQ pulled pork sandwiches with coleslaw",
    "Chicken pot pie",
    "Meatloaf with mashed potatoes",
    "Teryiaki chicken with crash hots",
    "Breakfast burritos"
]