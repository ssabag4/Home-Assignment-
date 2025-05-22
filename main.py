# python programming when you need to interact with the web
# Interact with APIs service like GitLab
# provide APIs that allow programs to communicate with them. 
# Send data to web servers (POST, PUT, DELETE requests)
import os
import requests

# when  working with data that needs to be structured and easily exchanged over the internet.
# It brings in Python's built-in json module.
import json

# This line is use for reteive the token from local
from dotenv import load_dotenv 
 


# This function call will load the environment variables from the .env file
load_dotenv()


def manage_member_role(username: str, entity_name: str, role: str, entity_type: str = "project"):
    #   - 'username' (str): The username of the user whose role is to be managed.
    #   - 'entity_name' (str): The name of the project or group.
    #   - 'role' (str): The role to assign to the user (e.g., 'Guest', 'Developer').
    #   - 'entity_type' (str, optional):  The type of the entity.  Defaults to "project".


    #  Retrieves the token 
    gitlab_private_token = os.getenv("GITLAB_PRIVATE_TOKEN") 
   
    # This line defines a variable 'gitlab_private_token' and assigns it a string value.
    #  This string is a GitLab Personal Access Token.  It's crucial for authenticating
  
    gitlab_base_url = "https://gitlab.com"
    # This line defines the base URL for the GitLab API.
    headers = {'PRIVATE-TOKEN': gitlab_private_token}

    # This line creates a dictionary called 'headers'.  This dictionary will be used
    #  as the 'headers' argument in the 'requests.get', 'requests.put', and
    #  'requests.post' calls.  It includes the 'PRIVATE-TOKEN' header, which is
    #  how the requests to the GitLab API are authenticated.

    role_mapping = {
        'Guest': 10,
        'Reporter': 20,
        'Developer': 30,
        'Maintainer': 40,
        'Owner': 50
    }
    # This dictionary maps human-readable role names (keys) to their corresponding
    #  numerical IDs in the GitLab API (values). GitLab uses these IDs to represent
    #  access levels.



    if role not in role_mapping:
        print(f"Error: Invalid role '{role}'. Valid roles are: {', '.join(role_mapping.keys())}")
        return
    # This 'if' statement checks if the provided 'role' is a valid role.
    # -  If the role is invalid:  An error message is printed to the console, listing the valid roles.
    # -  The function returns (exits) without doing anything for example: 'Owner' map to --> 50

    role_id = role_mapping[role]
    # If the role is valid, this line retrieves the corresponding role ID from the
    #  'role_mapping' dictionary using the provided 'role' as the key. 
    #  The retrieved ID is then stored in the 'role_id' variable.



    try:
        # This 'try' block begins a block of code where exceptions (errors) might occur
        #  during the API calls.

        # First, try to get the user ID
        user_search_url = f"{gitlab_base_url}/api/v4/users?username={username}"
        # This line constructs the URL to search for the user by their username
        #  using the GitLab API.
        #  -  'f"{gitlab_base_url}/api/v4/users?username={username}"':  An f-string
        #     is used to embed the 'username' variable directly into the URL.

        user_response = requests.get(user_search_url, headers=headers)
        # This line makes an HTTP GET request to the GitLab API to search for the user.
        #  -  'requests.get()':  The function from the 'requests' library used to make the GET request.
        #  -  'user_search_url':  The URL to send the request to.
        #  -  'headers':  The HTTP headers, including the 'PRIVATE-TOKEN' for authentication.


        user_response.raise_for_status()
        # This line checks if the API request was successful.
        #  -  'response.raise_for_status()':  This method raises an exception
        #     (requests.exceptions.RequestException) if the HTTP status code of the response indicates an error 
        #     (e.g., 404, 500).  If the request was successful (e.g., 200 OK), it does nothing.

        users = user_response.json()
        # If the request was successful, this line parses the JSON data from the
        #  response.
        #  -  'response.json()':  This method converts the JSON response into a Python list or dictionary.  
        #  In this case, it's expected to be a list of user


        if not users:
            print(f"Error: User '{username}' not found.")
            return
        # This 'if' statement checks if the 'users' list is empty.
        # - If it is, it means no user with the given username was found in GitLab.
        # -  An error message is printed.
        # -  The function returns.

        user_id = users[0]['id']
        # This line extracts the user ID from the first element of the 'users' list.
        #  It assumes that the first element is the correct user (which is generally
        #  true for a search by username in GitLab).  The user ID is then stored
        #  in the 'user_id' variable.

        if entity_type == "project":
            # This 'if' statement checks the 'entity_type'.  If it's "project", the
            #  code within this block will handle managing roles for a project.

            # First, try to get the project ID
            project_search_url = f"{gitlab_base_url}/api/v4/projects?search={entity_name}"
            # This line constructs the URL to search for the project by its name using the GitLab API.

            project_response = requests.get(project_search_url, headers=headers)
            # This line makes an HTTP GET request to the GitLab API to search for the project.

            project_response.raise_for_status()
            # This line checks if the project search request was successful.

            projects = project_response.json()
            # This line parses the JSON response, which is expected to be a list of project objects.

            
            
            
            
            project = next((p for p in projects if p['name'] == entity_name or str(p['id']) == entity_name), None)
            # This line finds the project in the list of projects.
            #  -  'next((p for p in projects if p['name'] == entity_name or str(p['id']) == entity_name), None)':
            #     This uses a generator expression and the 'next()' function to find the
            #     first project in the 'projects' list whose 'name' matches the
            #     'entity_name' or whose 'id' (converted to a string) matches the
            #     'entity_name'.  The 'None' is the default value, returned if no matching
            #     project is found.

            if not project:
                print(f"Error: Project '{entity_name}' not found.")
                return
            # This 'if' statement checks if a matching project was found.
            # - If not, an error message is printed, and the function returns.

            entity_id = project['id']
            # This line extracts the project ID from the found project object.

            member_url = f"{gitlab_base_url}/api/v4/projects/{entity_id}/members/{user_id}"
            # This line constructs the URL to get a specific member of the project.

            add_member_url = f"{gitlab_base_url}/api/v4/projects/{entity_id}/members"
            # This line constructs the URL to add a member to the project.




        elif entity_type == "group":
            # This 'elif' block handles the case where 'entity_type' is "group".
            #  The logic is very similar to the "project" case, but it uses the
            #  GitLab API endpoints for groups.

            # First, try to get the group ID
            group_search_url = f"{gitlab_base_url}/api/v4/groups?search={entity_name}"
            group_response = requests.get(group_search_url, headers=headers)
            group_response.raise_for_status()
            groups = group_response.json()
            group = next((g for g in groups if g['name'] == entity_name or str(g['id']) == entity_name), None)
            if not group:
                print(f"Error: Group '{entity_name}' not found.")
                return
            entity_id = group['id']
            member_url = f"{gitlab_base_url}/api/v4/groups/{entity_id}/members/{user_id}"
            add_member_url = f"{gitlab_base_url}/api/v4/groups/{entity_id}/members"

        else:
            print("Error: Invalid entity_type. Must be 'project' or 'group'.")
            return
        # This 'else' block handles the case where 'entity_type' is neither
        #  "project" nor "group".  It prints an error message and returns.

        # Check if the user is already a member
        get_member_response = requests.get(member_url, headers=headers)
        # This line makes a GET request to check if the user is already a member
        #  of the project or group.

        if get_member_response.status_code == 200:
            # User is a member, update their role
            # This 'if' statement checks the status code of the response.  A status
            #  code of 200 indicates that the user is already a member.

            put_payload = {'access_level': role_id}
            # This line creates the payload for updating the user's role.  It's a
            #  dictionary with the 'access_level' key set to the numerical 'role_id'.

            put_response = requests.put(member_url, headers=headers, json=put_payload)
            # This line makes a PUT request to update the user's role.
            #  -  'requests.put()':  Used for updating an existing resource.
            #  -  'member_url':  The URL to update the member.
            #  -  'headers':  The authentication headers.
            #  -  'json=put_payload':  Sends the payload as JSON data in the request body.

            put_response.raise_for_status()
            # This line checks if the role update was successful.

            print(f"Successfully updated role of user '{username}' in {entity_type} '{entity_name}' to '{role}'.")
            # This line prints a success message.

        elif get_member_response.status_code == 404:
            # User is not a member, add them!!
            # This 'elif' block handles the case where the user is not a member (status code 404 Not Found).

            post_payload = {'user_id': user_id, 'access_level': role_id}
            # This line creates the payload for adding the user as a member.

            post_response = requests.post(add_member_url, headers=headers, json=post_payload)
            # This line makes a POST request to add the user as a member.
            #  -  'requests.post()':  Used for creating a new resource.
            #  -  'add_member_url': The URL to add a member.
            #  -  'headers':  The authentication headers.
            #  -  'json=post_payload':  Sends the payload as JSON data.

            post_response.raise_for_status()
            # This line checks if adding the member was successful.

            print(f"Successfully added user '{username}' to {entity_type} '{entity_name}' with role '{role}'.")
            # This line prints a success message.

        else:
            print(f"Error managing member: {get_member_response.status_code} - {get_member_response.text}")
            # This 'else' block handles any other unexpected status codes.
            #  It prints an error message including the status code and the response text.

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        # This 'except' block catches any 'requests.exceptions.RequestException'
        #  that might have occurred during the API calls within the 'try' block. It prints a general error message.





# the second function the get three values
def get_items_by_year(item_type: str, year: int):
    # this is hardcoded value that I have use in the testing script to be part of the end URL
   
    GITLAB_PRIVATE_TOKEN = os.getenv("GITLAB_PRIVATE_TOKEN")

    # this is hardcoded GITLAB url
    gitlab_base_url = "https://gitlab.com"  
   
    # use to be the url using hardcode for exmaple "PRIVATE-TOKEN: glpat-CjWZz8kf3r2GJLxiyUEx" 
    headers = {'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN}

    # create an empty list
    items = []
    page = 1
    per_page = 20  # Maximum allowed per page

    # input use validation of list containing two strings mr and issues and if not its enter the while year already validate in main!!
    if item_type not in ['mr', 'issues']:
        print("Error: Invalid item_type. Must be 'mr' or 'issues'.")
        return items
    
    while True:
        if item_type == 'issues':
               ## f-string allows to embed url expressions inside string url paramter
            # Test just getting issues without date filters
            url = f"{gitlab_base_url}/api/v4/issues?created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z"
            # debug urls
            #url = f"{gitlab_base_url}/api/v4/issues?created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z&per_page={per_page}&page={page}"
            #url = f"{gitlab_base_url}/api/v4/issues?scope=all&created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z&per_page={per_page}&page={page}"       
            #url = f"{gitlab_base_url}/api/v4/issues?scope=all&created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z&per_page={per_page}&page={page}"
        
        elif item_type == 'mr':
            ## f-string allows to embed url expressions inside string url paramter
            #url = f"{gitlab_base_url}/api/v4/merge_requests?scope=all&created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z&per_page={per_page}&page={page}"
            url = f"{gitlab_base_url}/api/v4/merge_requests?created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z"
        
        try:
            # function to send an HTTP GET request to the GitLab API,
            #  using the constructed url and the authentication headers (which contain the private token).
            response = requests.get(url, headers=headers)
            
            # Checking for Errors using try...except block catches
            # It checks the HTTP status code of the response.
            # If the status code indicates an error (e.g., 400 Bad Request, 404 Not Found, 500 Internal Server Error)
            #  this method will raise a requests.exceptions.RequestException. 
            #  If the request is successful (200 OK), it does nothing
            response.raise_for_status()

            #if the request was successful,
            #  this line parses the JSON data from the response body into a Python list
            #  and assigns it to the current_items variable.  This is the data from the current page of results.

            current_items = response.json()
            #print(current_items)
            print(json.dumps(current_items, indent=4))
            # This checks if the current_items list is empty. 
            # If it empty,This means that the API returned no data on this page
            #  which could indicate that there are no more results to fetch.
            if not current_items:
                break  # No more items on this page


            # This line adds all the items from the current_items list 
            # (the results from the current page) to the main 'items' list defind at the start of the func.  
            # The extend() method is used because current_items is a list itself, 
            # and I need to add all its elements to the 'items' list.
            items.extend(current_items)
            
            #  This is the key part of the pagination handling
            # X-Total-Pages' in response.headers:  
            # It checks if the X-Total-Pages header is present in the API response. 
            # GitLab  use this header to indicate the total number of pages of results.
            # If the header is present,it retrieves the value from the header (which is a string) and converts it to an integer 'page' defind in the stat of the func.
            # If the current page number is greater than or equal to the total number of pages, 
            # it means we've fetched all the data and break! 


            if 'X-Total-Pages' in response.headers and int(response.headers['X-Total-Pages']) <= page:
                break # No more pages

            # If there are more pages to fetch, this line increments the page variable,
            #  so the next iteration of the loop will request the next page of results.
            page += 1
        
        
        #if any error occurs during the API request or response processing this except block will catch the exception.
        # and print an informative error message, including the item_type (issues or mr) 
        # and the page number where the error occurred, which is importent for debugging.
        
        #except requests.exceptions.RequestException as e:
        #    print(f"An error occurred while fetching {item_type} (page {page}): {e}")
        #    break
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching {item_type} (page {page}): {e}")
            if response is not None: # Check if response object exists
               print(f"Response status code: {response.status_code}")
               print(f"Response text: {response.text}") # Print the raw response content
            break

    # this line prints the total number of items found created in the input year
    print(f"Found {len(items)} {item_type} created in {year}.")

    # the function returns the items list, which contains all the fetched issues or merge requests.
    return items


def main_menu():

    """
    Displays the main menu and handles user input.
    """
    while True:
        print("\n--- Main Menu ---")
        print("1. Grant Access")
        print("2. return all issues/merge requests) created on the given year.")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            username = input("Enter username: ")
            resource = input("Enter repository or group name: ")
            role = input("Enter role (Reporter, Developer, Maintainer, Owner): ")

            manage_member_role(username, resource, role)

            
        elif choice == '2':
            item = input("Enter mr or issues: ")
            while True:
                # This part check that checks if all characters in a string are digits and user write 4 number
                identifier_year = input("Enter a 4-digit year number: ")
                if identifier_year.isdigit() and len(identifier_year) == 4:
                    # convert a value to an integer.
                    year = int(identifier_year)
                    # send two user input to function
                    get_items_by_year(item, year)

                    # switch to main function main to show the menu option
                    break
                else:
                    # in case the user print bad input its retune back to while in a loop
                    print("Invalid input. Please enter a valid year / 4-digit number.")
                    
        elif choice == '3':
            # going out from the main fuction
            print("Exiting program.")
            break
        else:
            # any value diffrent than 1 or 2 or 3 will loop back to main while loop this print 
            print("Invalid choice. Please enter a number between 1 and 3.")

if __name__ == "__main__":
    main_menu()
