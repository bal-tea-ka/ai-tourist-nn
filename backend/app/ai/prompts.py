def build_categories_prompt(user_interests, category_names: dict, category_times: dict):
    prompt = "You are an AI assistant that helps to select categories based on user interests.\n"
    prompt += "Here are the available categories with time to visit it:\n"
    for cat_id, cat_name in category_names.items():
        visit_time = category_times.get(cat_id, 30)
        prompt += f"- {cat_id}: {cat_name} (average visit time: {visit_time} min)\n"
    prompt += f"User interests: {user_interests}\n"
    prompt += "Select the most relevant categories for the user."
    prompt +=  '\n# INSTRUCTIONS FOR FORMING A RESPONSE: \n' \
               f'1. Create a list of categories based on the {user_interests}. \n' \
               '2. Choose no more than 5 categories. \n' \
               '3. The response must be in the JSON format of a list of category IDs for example: [1, 2, 3] \n' \
               
    return prompt


def build_route_prompt(places, available_time_hours, user_location):
    prompt = "You are an AI assistant that creates personalized walking routes in Niznhy Novrogod, Russia.\n"
    prompt += "Here are the available places to include in the route:\n"
    for place in places:
        prompt += f"- {place['title']}, address: {place['address']}, average visit duration: {place['avg_visit_duration']} min\n"
    prompt += f"User location: {user_location}\n"
    prompt += f"Available time for the route: {available_time_hours} hours.\n"
    prompt += "Create a walking route including 3-4 places, considering visit durations and travel times between them."
    prompt +=  '\n# INSTRUCTIONS FOR FORMING A RESPONSE: \n' \
                '1. Create a walking route, logically moving from the starting point to other places. \n' \
                '2. Include 3-4 places in the route, combining categories. Mention possible coffee shops for stops along the way (coffee shops are not included in the dataset, you can suggest them generally based on the logic of the route). \n' \
                '3. Consider the average visit time from the dataset and realistic travel time between points (5-15 minutes). \n' \
                '4. The response structure should be clear:    \n' \
                '- **Place name and category.**    \n' \
                '- **Justification for the choice:** Why we are going here, linking to the user\'s interests. \n' \
                '- **Approximate timeline:** "10:00-10:20 - sightseeing of object X, 10:20-10:35 - transition to object Y". \n' \
                '5. The response must be in the JSON format of a list of route objects. Each object should contain the fields: title, address, category, visit_duration, notes.\n' \
                'Create a route and give a response in the required format.'

    return prompt
