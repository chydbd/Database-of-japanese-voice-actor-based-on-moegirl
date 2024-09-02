import sqlite3

def query_seiyuu_and_projects_no_duplicates(seiyuu_name, database_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Query to find the projects and project names of the given seiyuu
    query = """
    SELECT DISTINCT p.id, p.name
    FROM seiyuu s
    JOIN seiyuu_character sr ON s.id = sr.seiyuu_id
    JOIN character c ON sr.character_id = c.id
    JOIN project p ON c.project_id = p.id
    WHERE s.name = ?
    """
    cursor.execute(query, (seiyuu_name,))
    projects = cursor.fetchall()

    # If no projects found for the given seiyuu, return empty list
    if not projects:
        return []

    # Collect all project ids and their names
    project_details = {project[0]: project[1] for project in projects}

    # Query to find other seiyuu who have worked on the same projects
    other_seiyuu_query = """
    SELECT DISTINCT s.id, s.name, c.name, p.name
    FROM seiyuu s
    JOIN seiyuu_character sr ON s.id = sr.seiyuu_id
    JOIN character c ON sr.character_id = c.id
    JOIN project p ON c.project_id = p.id
    WHERE p.id IN ({}) AND s.name != ?
    """.format(','.join('?'*len(project_details)))

    # Add project ids and the seiyuu name to the parameters
    params = list(project_details.keys()) + [seiyuu_name]

    cursor.execute(other_seiyuu_query, params)
    other_seiyuu = cursor.fetchall()

    # Close the connection to the database
    conn.close()

    # Prepare the result with project names and character names, removing duplicates
    result = {}
    for seiyuu_id, seiyuu_name, character_name, project_name in other_seiyuu:
        if project_name not in result:
            result[project_name] = {}
        if seiyuu_name not in result[project_name]:
            result[project_name][seiyuu_name] = []
        result[project_name][seiyuu_name].append(character_name)

    # Convert the result to a list of tuples
    result_list = [(project_name, (seiyuu_name, characters)) for project_name, seiyuu_characters in result.items() for seiyuu_name, characters in seiyuu_characters.items()]

    return result_list

# Replace 'your_database.db' with the path to your actual database file
database_path = 'database.db'
seiyuu_name = "Machico"  # Replace with an actual seiyuu name
other_seiyuu_and_projects_no_duplicates = query_seiyuu_and_projects_no_duplicates(seiyuu_name, database_path)
for elements in other_seiyuu_and_projects_no_duplicates:
    print(elements)
