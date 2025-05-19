import requests
import json


def grant_access(username, resource_name, role):
    print(f"\nAttempting to grant '{role}' access to '{resource_name}' for user '{username}'.")


def process_data(item_name, year):
    if not (1000 <= year <= 9999):
        print("\nError: year must be a 4-digit number.")
        return
    print(f"\nProcessing data for '{item_name}' with year: {year}.")


def manage_member_role(username: str, entity_name: str, role: str, entity_type: str = "project"):
    gitlab_private_token = "glpat-CjWZz8kf3r2GJLxiyUEx"
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
        print(f"Error: Invalid role '{role}'. Valid roles are: {', '.join(role_mapping.keys())}")
        return
    role_id = role_mapping[role]
    try:
        # First, try to get the user ID
        user_search_url = f"{gitlab_base_url}/api/v4/users?username={username}"
        user_response = requests.get(user_search_url, headers=headers)
        user_response.raise_for_status()
        users = user_response.json()
        if not users:
            print(f"Error: User '{username}' not found.")
            return
        user_id = users[0]['id']
        if entity_type == "project":
            # First, try to get the project ID
            project_search_url = f"{gitlab_base_url}/api/v4/projects?search={entity_name}"
            project_response = requests.get(project_search_url, headers=headers)
            project_response.raise_for_status()
            projects = project_response.json()
            project = next((p for p in projects if p['name'] == entity_name or str(p['id']) == entity_name), None)
            if not project:
                print(f"Error: Project '{entity_name}' not found.")
                return
            entity_id = project['id']
            member_url = f"{gitlab_base_url}/api/v4/projects/{entity_id}/members/{user_id}"
            add_member_url = f"{gitlab_base_url}/api/v4/projects/{entity_id}/members"
        elif entity_type == "group":
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
        # Check if the user is already a member
        get_member_response = requests.get(member_url, headers=headers)
        if get_member_response.status_code == 200:
            # User is a member, update their role
            put_payload = {'access_level': role_id}
            put_response = requests.put(member_url, headers=headers, json=put_payload)
            put_response.raise_for_status()
            print(f"Successfully updated role of user '{username}' in {entity_type} '{entity_name}' to '{role}'.")
        elif get_member_response.status_code == 404:
            # User is not a member, add them
            post_payload = {'user_id': user_id, 'access_level': role_id}
            post_response = requests.post(add_member_url, headers=headers, json=post_payload)
            post_response.raise_for_status()
            print(f"Successfully added user '{username}' to {entity_type} '{entity_name}' with role '{role}'.")
        else:
            print(f"Error managing member: {get_member_response.status_code} - {get_member_response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def get_items_by_year(item_type: str, year: int):
    gitlab_private_token = "glpat-CjWZz8kf3r2GJLxiyUEx"
    gitlab_base_url = "https://gitlab.com"  

    headers = {'PRIVATE-TOKEN': gitlab_private_token}
    items = []
    page = 1
    per_page = 100  # Maximum allowed per page

    if item_type not in ['mr', 'issues']:
        print("Error: Invalid item_type. Must be 'mr' or 'issues'.")
        return items
    while True:
        if item_type == 'issues':
            #url = f"{gitlab_base_url}/api/v4/issues?scope=all&created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z&per_page={per_page}&page={page}"
            url = f"{gitlab_base_url}/api/v4/issues?created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z"       
            print(f"This is the URL sent: {url}")
        elif item_type == 'mr':
            #url = f"{gitlab_base_url}/api/v4/merge_requests?scope=all&created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z&per_page={per_page}&page={page}"
            url = f"{gitlab_base_url}/api/v4/merge_requests?created_after={year}-01-01T00:00:00Z&created_before={year+1}-01-01T00:00:00Z"
            print(f"This is the URL sent: {url}")        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            current_items = response.json()
            if not current_items:
                break  # No more items on this page
            items.extend(current_items)
            if 'X-Total-Pages' in response.headers and int(response.headers['X-Total-Pages']) <= page:
                break # No more pages
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching {item_type} (page {page}): {e}")
            break
    print(f"Found {len(items)} {item_type} created in {year}.")
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

            grant_access(username, resource, role)
            manage_member_role(username, resource, role)

            
        elif choice == '2':
            item = input("Enter mr or issues: ")
            while True:
                identifier_year = input("Enter a 4-digit year number: ")
                if identifier_year.isdigit() and len(identifier_year) == 4:
                    year = int(identifier_year)
                    #process_data(item, year)
                    get_items_by_year(item, year)
                    break
                else:
                    print("Invalid input. Please enter a valid year / 4-digit number.")
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")


if __name__ == "__main__":
    main_menu()
