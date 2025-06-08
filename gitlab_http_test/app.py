import os
import requests
import json
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key' # Replace with a strong secret key for flash messages

# This function call will load the environment variables from the .env file
load_dotenv()

def manage_member_role(username: str, entity_name: str, role: str, entity_type: str = "project"):
    """
    Manages a user's role in a GitLab project or group.

    Args:
        username (str): The username of the user whose role is to be managed.
        entity_name (str): The name of the project or group.
        role (str): The role to assign to the user (e.g., 'Guest', 'Developer').
        entity_type (str, optional): The type of the entity. Defaults to "project".

    Returns:
        tuple: A tuple containing (success_boolean, message_string).
    """
    gitlab_private_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    
    # Check if the GitLab private token is available
    if not gitlab_private_token:
        return False, "Error: GitLab private token not found. Please set GITLAB_PRIVATE_TOKEN in your .env file."

    gitlab_base_url = "https://gitlab.com"
    headers = {'PRIVATE-TOKEN': gitlab_private_token}

    role_mapping = {
        'Guest': 10,
        'Reporter': 20,
        'Developer': 30,
        'Maintainer': 40,
        'Owner': 50
    }

    if role not in role_mapping:
        return False, f"Error: Invalid role '{role}'. Valid roles are: {', '.join(role_mapping.keys())}"

    role_id = role_mapping[role]

    try:
        # First, try to get the user ID
        user_search_url = f"{gitlab_base_url}/api/v4/users?username={username}"
        user_response = requests.get(user_search_url, headers=headers)
        user_response.raise_for_status() # Raise an exception for bad status codes
        users = user_response.json()

        if not users:
            return False, f"Error: User '{username}' not found."

        user_id = users[0]['id']

        entity_id = None
        member_url = None
        add_member_url = None

        if entity_type == "project":
            # Get the project ID
            project_search_url = f"{gitlab_base_url}/api/v4/projects?search={entity_name}"
            project_response = requests.get(project_search_url, headers=headers)
            project_response.raise_for_status()
            projects = project_response.json()
            
            # Find the exact project by name or ID
            project = next((p for p in projects if p['name'] == entity_name or str(p['id']) == entity_name), None)

            if not project:
                return False, f"Error: Project '{entity_name}' not found."
            entity_id = project['id']
            member_url = f"{gitlab_base_url}/api/v4/projects/{entity_id}/members/{user_id}"
            add_member_url = f"{gitlab_base_url}/api/v4/projects/{entity_id}/members"

        elif entity_type == "group":
            # Get the group ID
            group_search_url = f"{gitlab_base_url}/api/v4/groups?search={entity_name}"
            group_response = requests.get(group_search_url, headers=headers)
            group_response.raise_for_status()
            groups = group_response.json()
            
            # Find the exact group by name or ID
            group = next((g for g in groups if g['name'] == entity_name or str(g['id']) == entity_name), None)
            if not group:
                return False, f"Error: Group '{entity_name}' not found."
            entity_id = group['id']
            member_url = f"{gitlab_base_url}/api/v4/groups/{entity_id}/members/{user_id}"
            add_member_url = f"{gitlab_base_url}/api/v4/groups/{entity_id}/members"

        else:
            return False, "Error: Invalid entity_type. Must be 'project' or 'group'."

        # Check if the user is already a member
        get_member_response = requests.get(member_url, headers=headers)

        if get_member_response.status_code == 200:
            # User is a member, update their role
            put_payload = {'access_level': role_id}
            put_response = requests.put(member_url, headers=headers, json=put_payload)
            put_response.raise_for_status()
            return True, f"Successfully updated role of user '{username}' in {entity_type} '{entity_name}' to '{role}'."
        elif get_member_response.status_code == 404:
            # User is not a member, add them
            post_payload = {'user_id': user_id, 'access_level': role_id}
            post_response = requests.post(add_member_url, headers=headers, json=post_payload)
            post_response.raise_for_status()
            return True, f"Successfully added user '{username}' to {entity_type} '{entity_name}' with role '{role}'."
        else:
            # Handle other unexpected status codes
            return False, f"Error managing member: {get_member_response.status_code} - {get_member_response.text}"

    except requests.exceptions.RequestException as e:
        # Catch any request-related errors
        return False, f"An API request error occurred: {e}"
    except Exception as e:
        # Catch any other unexpected errors
        return False, f"An unexpected error occurred: {e}"



##### start of the get_items_by_year func #####
def get_items_by_year(item_type: str, year: int):
    """
    Fetches GitLab issues or merge requests created in a given year.

    Args:
        item_type (str): The type of items to fetch ('mr' for merge requests, 'issues' for issues).
        year (int): The year to filter items by.
    Returns:
        tuple: A tuple containing (list_of_items, message_string).
    """

    # upload my token from .env file located on the
    gitlab_private_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    
    # Check if the GitLab private token is available and uploaded
    if not gitlab_private_token:
        return [], "Error: GitLab private token not found. Please set GITLAB_PRIVATE_TOKEN in your .env file."

    # this is hardcoded GITLAB url
    gitlab_base_url = "https://gitlab.com"

    # use to be the url using hardcode for example:
    # ### "PRIVATE-TOKEN: glpat-CjWZz8kf3r2GJLxiyUEx"
    headers = {'PRIVATE-TOKEN': gitlab_private_token}

    # create an empty list to hold the data
    items = []
    page = 1
    per_page = 100  # Max allowed per page by GitLab API

    # input use validation of list
    # containing two strings mr and issues and
    # if not its enter the while year already validate in main!!
    if item_type not in ['mr', 'issues']:
        return [], "Error: Invalid item_type. Must be 'mr' or 'issues'."
    
    # Validate year input (already done in Flask route, but good for standalone function)
    if not isinstance(year, int) or not (1999 <= year <= 2100): # Reasonable year range
        return [], "Error: Invalid year. Please provide a valid integer year."

    ## f-string allows to embed url expressions inside string url parameter and build the URL
    while True:
        if item_type == 'issues':
            url = f"{gitlab_base_url}/api/v4/issues?created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z&per_page={per_page}&page={page}"
        elif item_type == 'mr':
            url = f"{gitlab_base_url}/api/v4/merge_requests?created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z&per_page={per_page}&page={page}"
        
        try:
            # function to send an HTTP GET request to the GitLab API,
            # using the constructed url and the authentication headers (which contain the private token).
            response = requests.get(url, headers=headers)

            # Checking for Errors using try...except block catches
            # It checks the HTTP status code of the response.
            # If the status code indicates an error (e.g., 400 Bad Request, 404 Not Found, 500 Internal Server Error)
            #  this method will raise a requests.exceptions.RequestException.
            #  If the request is successful (200 OK), it does nothing
            response.raise_for_status()

            # if the request was successful,
            #  this line parses the JSON data from the response body into a Python list
            #  and assigns it to the current_items variable.
            #  This is the data from the current page of results.
            current_items = response.json()

            if not current_items:
                break  # No more items on this page

            # This line adds all the items from the current_items list
            # (the results from the current page) to the main 'items' list defind at the start of the func.
            # The extend() method is used because current_items is a list itself,
            # and I need to add all its elements to the 'items' list.
            items.extend(current_items)
            
            # Check for pagination headers
            total_pages_header = response.headers.get('X-Total-Pages')
            if total_pages_header:
                total_pages = int(total_pages_header)
                if page >= total_pages:
                    break # No more pages

            page += 1
        
        except requests.exceptions.RequestException as e:
            error_message = f"An API request error occurred while fetching {item_type} (page {page}): {e}"
            if response is not None: 
               error_message += f"\nResponse status code: {response.status_code}\nResponse text: {response.text}"
            return [], error_message
        except Exception as e:
            return [], f"An unexpected error occurred: {e}"

    # the function returns the items list, which contains all the fetched issues or merge requests.
    # And a message
    return items, f"Found {len(items)} {item_type} created in {year}."




# My Flask Routes decorator func When you initialize Flask,
# such as app = Flask(__name__).
# the app object is where register my routes.
# the .route(): Flask method used to bind a function to a URL.
# this is a decorator function that live in 'app' object that declared  in Flask class
@app.route('/')
def index():
    """
    Renders the main menu page index.html located in templates.
    """
    return render_template('index.html')


# @: a decorator function.
# app: This refers to the Flask application instance.
# When  initialize Flask  app = Flask(__name__).
# This app object is where the code register my page routes.
#.route():  method provided by the Flask app object used to associate a URL path with a
# specific Python function (which is grant_access in this case).
#'/grant_access': This is the URL rule or path.
# When a user's web browser makes a request in my case its locally 127.0.0.1/get_items,
# Flask will look for a function associated with this path.methods=['GET', 'POST']:
# telling Flask that the grant_access() function can handle both initial requests
# to load the page (GET) and subsequent requests to submit data from the form (POST).
@app.route('/grant_access', methods=['GET', 'POST'])
def grant_access():
    """
    Handles displaying and processing the 'Grant Access' form.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        entity_name = request.form.get('entity_name')
        role = request.form.get('role')
        entity_type = request.form.get('entity_type')

        # Basic validation for form inputs from user in case of missing data error message will be
        # display on screen and redirect it back to page to fix the user input
        if not all([username, entity_name, role, entity_type]):
            flash("All fields are required.", 'error')
            return redirect(url_for('grant_access'))

        #  Call to function manage_member_role
        # success -  boolean True for success, False for failure).
        # message - string, containing either a success message or a detailed error message).
        # for example "Successfully updated role of user 'ssabag76' in project 'Test3' to 'Maintainer'."
        # or          "Error: User 'ssabag7644' not found."

        success, message = manage_member_role(username, entity_name, role, entity_type)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        return redirect(url_for('grant_access')) # Redirect to clear form on refresh
    return render_template('grant_access.html')


@app.route('/get_items', methods=['GET', 'POST'])
def get_items():
    """
    Handles displaying and processing the 'Get Issues/Merge Requests' form.
    """
    if request.method == 'POST':
        item_type = request.form.get('item_type')
        year_str = request.form.get('year')
        
        # Validate year input
        if not year_str or not year_str.isdigit() or len(year_str) != 4:
            flash("Invalid year. Please enter a 4-digit number.", 'error')
            return redirect(url_for('get_items'))
        
        year = int(year_str)

        # I have included this line to the code to check that year > than 2000
        if year < 2000:
            flash("Year must be 2000 or later.", 'error')
            # below code redirects the user back to the form or page where they entered the year,
            # allowing  to correct the year input
            return redirect(url_for('get_items'))

        # the get_items_by_year function is expected to return a tuple or a sequence with exactly two elements.
        # The first element returned by the function will be assigned to items.
        # The second element returned by the function will be assigned to message.
        items, message = get_items_by_year(item_type, year)
        
        # Check if the message indicates an error
        if "Error" in message:
            flash(message, 'error')
            # If there's an error, redirect back to the form
            return redirect(url_for('get_items'))
        else:
            # If successful, flash a success message and render the results page
            flash(message, 'success')
            return render_template('result.html', items=items, item_type=item_type, year=year)

    return render_template('get_items.html')

# run when the script is executed directly
if __name__ == "__main__":
    # Ensure this is set to False in a production environment
    # method that starts the Flask development server http://127.0.0.1:5000
    # debug mode activate the automatic server reloader when I do changes to the code
    app.run(debug=True)
