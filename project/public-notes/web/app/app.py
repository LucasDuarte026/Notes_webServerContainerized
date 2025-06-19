from flask import Flask, render_template, jsonify, request
import psycopg2 as sql
from psycopg2 import OperationalError, ProgrammingError
import logging # Import logging module
import re # Import regex for email validation
import os # Import os for environment variables


# Configure logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

app.config['POSTGRES_HOST'] = os.getenv('POSTGRES_HOST') 
app.config['POSTGRES_PORT'] = os.getenv('POSTGRES_PORT')
app.config['POSTGRES_DB'] = os.getenv('POSTGRES_DB')
app.config['POSTGRES_USER'] = os.getenv('POSTGRES_USER')
app.config['POSTGRES_PASSWORD'] = os.getenv('POSTGRES_PASSWORD')


def get_db_connection(check_health=False):
    print(f"Database configuration: {app.config['POSTGRES_HOST']}:{app.config['POSTGRES_PORT']}/{app.config['POSTGRES_DB']} as {app.config['POSTGRES_USER']}")
    """Establishes and returns a database connection."""
    conn = None
    try:    
        conn = sql.connect(
            host=app.config['POSTGRES_HOST'],
            port=app.config['POSTGRES_PORT'],
            database=app.config['POSTGRES_DB'],
            user=app.config['POSTGRES_USER'],
            password=app.config['POSTGRES_PASSWORD'],
            client_encoding="UTF8" 

        )
        if check_health:
            app.logger.info("Successfully connected to the database!")
    except OperationalError as e:
        app.logger.error(f"Error connecting to the database: {e}")
        # Log the full traceback for debugging in development
        app.logger.exception("Full traceback for database connection error:")
    return conn

def get_current_tag():
    """
    connect to the database and get the current tag value.
    """
    current_tag = -1
    conn, cur = None,None
    conn = get_db_connection()
 

    # Check if table exists before trying to select from it
    if not conn:
        app.logger.error("Failed to connect to the database. Cannot check for table existence.")
        return current_tag
    cur = conn.cursor()
    cur.execute("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename  = 'notes');")
    table_exists = cur.fetchone()[0]

    try:
        if table_exists:
            # IMPORTANT: Adjust this SELECT statement if your table columns are different
            cur.execute("SELECT MAX(tag) FROM notes;") # Select specific columns

            highest_tag = cur.fetchone()

        if highest_tag and highest_tag[0] is not None:
            current_tag = int(highest_tag[0])
            app.logger.info(f"Initialized current highest tag to: {current_tag}")
        else:
            # This branch should theoretically be covered by COALESCE, but acts as a fallback
            current_tag = -1 # If no notes, start from 0 or 1
            app.logger.info(f"No existing notes found. Initializing current highest tag to: {current_tag}")

        conn.commit() # Commit any potential changes (like table creation)

    except sql.Error as e:
        app.logger.error(f"Error during database configuration: {e}")
        app.logger.exception("Full traceback for database configuration error:")
        if conn:
            conn.rollback()  # Rollback in case of error
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return current_tag

@app.route('/')
def main_page():
    """Renders the main page for creating notes."""
    return render_template('create_page.html')

@app.route('/search')
def search_page():
    """Renders the main page for searching notes."""
    return render_template('search_page.html')

@app.route('/notesperuser')
def user_page():
    """Renders the main page for displaying notes per user."""
    return render_template('user_page.html')

@app.route('/health')
def health_check():
    try:
        # Tente conectar ao DB para um health check mais robusto
        conn = get_db_connection(True)
        conn.close()
        return jsonify(status="ok", db_connection="successful"), 200
    except Exception as e:
        return jsonify(status="error", db_connection="failed", message=str(e)), 500

@app.route('/create_note', methods=['POST'])
def create_note():
    """
    Handles the creation of a new note.
    Validates incoming data and inserts it into the database.
    """
    app.logger.info("Received request to create a note.")
    data = request.get_json()

    # Log raw received data for debugging
    app.logger.info(f"Raw data received: {data}")

    # --- Data Validation ---
    required_fields = ['title', 'name', 'email', 'text']
    if not data:
        app.logger.warning("No JSON data received.")
        return jsonify({'error': 'No data provided.'}), 400

    for field in required_fields:
        if field not in data:
            app.logger.warning(f"Missing required field: {field}")
            return jsonify({'error': f'Missing required field: {field}'}), 400

    title = data['title'].strip() # Strip whitespace from title
    name = data['name'].strip()
    email = data['email'].strip()
    text = data['text'].strip()

    # Validate 'title' (not empty, max 255 chars)
    if not title:
        app.logger.warning("Title cannot be empty.")
        return jsonify({'error': 'Title cannot be empty.'}), 400
    if len(title) > 255:
        app.logger.warning(f"Title exceeds max length (255): {len(title)} chars.")
        return jsonify({'error': 'Title exceeds maximum length of 255 characters.'}), 400

    # Validate 'name' (not empty, max 255 chars)
    if not name:
        app.logger.warning("Name cannot be empty.")
        return jsonify({'error': 'Name cannot be empty.'}), 400
    if len(name) > 255:
        app.logger.warning(f"Name exceeds max length (255): {len(name)} chars.")
        return jsonify({'error': 'Name exceeds maximum length of 255 characters.'}), 400

    # Validate 'email' (not empty, max 255 chars, basic format)
    if not email:
        app.logger.warning("Email cannot be empty.")
        return jsonify({'error': 'Email cannot be empty.'}), 400
    if len(email) > 255:
        app.logger.warning(f"Email exceeds max length (255): {len(email)} chars.")
        return jsonify({'error': 'Email exceeds maximum length of 255 characters.'}), 400
    # Basic email regex validation (not perfect, but catches common errors)
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        app.logger.warning(f"Invalid email format: {email}")
        return jsonify({'error': 'Invalid email format.'}), 400

    # Validate 'text' (not empty, max 2000 chars)
    if not text:
        app.logger.warning("Text content cannot be empty.")
        return jsonify({'error': 'Text content cannot be empty.'}), 400
    if len(text) > 2000:
        app.logger.warning(f"Text content exceeds max length (2000): {len(text)} chars.")
        return jsonify({'error': 'Text content exceeds maximum length of 2000 characters.'}), 400

    # --- Database Insertion ---
    conn = get_db_connection()
 
    cursor = None


    tag = get_current_tag()
    app.logger.info(f"tag debug: {tag}")

    tag+=1
    try:
        cursor = conn.cursor()
        query = "INSERT INTO notes (tag, title, name, email, text) VALUES (%s, %s, %s, %s, %s);"
        cursor.execute(query, (tag, title, name, email, text))
        conn.commit()
        app.logger.info("Note successfully created in the database.")
        return jsonify({'message': 'Note successfully created!'}), 201

    except ProgrammingError as e:
        if conn:
            conn.rollback()
        app.logger.error(f"Database programming error during note creation: {e}")
        app.logger.exception("Full traceback for database programming error:")
        return jsonify({'error': f"Database error: {e}"}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        app.logger.error(f"An unexpected error occurred during note creation: {e}")
        app.logger.exception("Full traceback for unexpected error:")
        return jsonify({'error': f"An unexpected error occurred: {e}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/remove_notes_by_tag', methods=['DELETE'])
def remove_note_tag():
    """
    Removes notes by a tag.
    """
    app.logger.info("Received request to delete a note.")
    data = request.get_json()

    # Log raw received data for debugging
    app.logger.info(f"Retrieved tag_from_request: {data} (Type: {type(data)})")

    # --- Data Validation ---
    if not data:
        app.logger.warning("No JSON data received.")
        return jsonify({'error': 'No data provided.'}), 400

    remove_tag = data.get('tag')    
    try:
        test_nummeric = int(remove_tag)  # Attempt to convert to integer
    except ValueError:
        # This block executes if int(data) failed because it wasn't a valid integer string.
        app.logger.warning(f"Invalid tag format received: '{data}'. Tag must be a whole number.")
        return jsonify({'error': 'Invalid tag format. Tag must be a whole number.'}), 400
    except TypeError:
        # This handles cases where data isn't a string or a number at all (e.g., a list, dict)
        app.logger.warning(f"Unexpected data type for tag received: '{type(data)}'. Tag must be a number or a string representing a number.")
        return jsonify({'error': 'Invalid tag type. Tag must be a number or a string representing a number.'}), 400

    # --- Database Insertion ---
    conn = get_db_connection()
 
    cursor = None

    try:
        cursor = conn.cursor()
        query = "DELETE FROM notes WHERE tag = %s;"
        cursor.execute(query, (remove_tag))
        conn.commit()
        app.logger.info("Note successfully deleted in the database.")
        return jsonify({'message': 'Note successfully deleted!'}), 201

    except ProgrammingError as e:
        if conn:
            conn.rollback()
        app.logger.error(f"Database programming error during note erasing: {e}")
        app.logger.exception("Full traceback for database programming error:")
        return jsonify({'error': f"Database error: {e}"}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        app.logger.error(f"An unexpected error occurred during note erasing: {e}")
        app.logger.exception("Full traceback for unexpected error:")
        return jsonify({'error': f"An unexpected error occurred: {e}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/get_all_notes', methods=['GET'])
def get_all_notes():
    """
    Fetches all notes from the database, ordered by tag, with a limit.
    Returns them as a JSON array.
    """
    app.logger.info("Received request to fetch all notes.")
    conn = get_db_connection()
 
    cursor = None
    notes = []
    try:
        cursor = conn.cursor()
        # Now 'tag' is the primary key, so we select 'tag' instead of 'id'
        cursor.execute("SELECT tag, title, name, email, text FROM notes ORDER BY tag ASC LIMIT 80;")
        column_names = [desc[0] for desc in cursor.description]

        for row in cursor.fetchall():
            note = dict(zip(column_names, row))
            notes.append(note)

        app.logger.info(f"Fetched {len(notes)} notes from the database.")
        return jsonify(notes), 200

    except ProgrammingError as e:
        app.logger.error(f"Database programming error during notes fetch: {e}")
        app.logger.exception("Full traceback for database programming error:")
        return jsonify({'error': f"Database error: {e}"}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during notes fetch: {e}")
        app.logger.exception("Full traceback for unexpected error:")
        return jsonify({'error': f"An unexpected error occurred: {e}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/get_notes_per_tag', methods=['POST'])
def get_notes_per_tag():
    """
    Fetches notes from the database matching a given tag.
    Returns them as a JSON array.
    """
    app.logger.info("Received request to fetch notes by tag for search.")
    data = request.get_json()

    if not data or 'tag' not in data:
        app.logger.warning("Tag not provided in request body for search.")
        return jsonify({'error': 'Tag parameter is required.'}), 400
    tag_to_search = data.get('tag')    
    try:
        test_nummeric = int(tag_to_search)  # Attempt to convert to integer
    except ValueError:
        # This block executes if int(data) failed because it wasn't a valid integer string.
        app.logger.warning(f"Invalid tag format received: '{data}'. Tag must be a whole number.")
        return jsonify({'error': 'Invalid tag format. Tag must be a whole number.'}), 400

    except TypeError:
        # This handles cases where data isn't a string or a number at all (e.g., a list, dict)
        app.logger.warning(f"Unexpected data type for tag received: '{type(data)}'. Tag must be a number or a string representing a number.")
        return jsonify({'error': 'Invalid tag type. Tag must be a number or a string representing a number.'}), 400

    conn = get_db_connection()
    cursor = None
    notes = []
    try:
        cursor = conn.cursor()
        
        query = "SELECT tag, title, name, email, text FROM notes WHERE tag = %s ORDER BY tag ASC LIMIT 80;"
        cursor.execute(query, (tag_to_search,)) # <--- This is where the query is executed

        column_names = [desc[0] for desc in cursor.description]

        for row in cursor.fetchall():
            note = dict(zip(column_names, row))
            notes.append(note)

        app.logger.info(f"Fetched {len(notes)} notes for tag '{tag_to_search}' from the database.")
        return jsonify(notes), 200

    except ProgrammingError as e:
        app.logger.error(f"Database programming error during notes fetch for tag '{tag_to_search}': {e}")
        app.logger.exception("Full traceback for database programming error:")
        return jsonify({'error': f"Database error: {e}"}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during notes fetch for tag '{tag_to_search}': {e}")
        app.logger.exception("Full traceback for unexpected error:")
        return jsonify({'error': f"An unexpected error occurred: {e}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/get_notes_per_email', methods=['POST'])
def get_notes_per_email():
    """
    Fetches notes from the database matching a given email.
    Returns them as a JSON array.
    """
    app.logger.info("Received request to fetch notes by email for search.")
    data = request.get_json()

    if not data or 'email' not in data:
        app.logger.warning("email not provided in request body for search.")
        return jsonify({'error': 'email parameter is required.'}), 400
    email_to_search = data.get('email')    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email_to_search):
        app.logger.warning(f"Invalid email format: {email_to_search}")
        return jsonify({'error': 'Invalid email format.'}), 400

    conn = get_db_connection()
    cursor = None
    notes = []
    try:
        cursor = conn.cursor()
        
        query = "SELECT tag, email, title, name, email, text FROM notes WHERE email = %s ORDER BY email ASC LIMIT 80;"
        cursor.execute(query, (email_to_search,)) # <--- This is where the query is executed

        column_names = [desc[0] for desc in cursor.description]

        for row in cursor.fetchall():
            note = dict(zip(column_names, row))
            notes.append(note)
    
        app.logger.info(f"Fetched {len(notes)} notes for email '{email_to_search}' from the database.")
        return jsonify(notes), 200

    except ProgrammingError as e:
        app.logger.error(f"Database programming error during notes fetch for email '{email_to_search}': {e}")
        app.logger.exception("Full traceback for database programming error:")
        return jsonify({'error': f"Database error: {e}"}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during notes fetch for email '{email_to_search}': {e}")
        app.logger.exception("Full traceback for unexpected error:")
        return jsonify({'error': f"An unexpected error occurred: {e}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
if __name__ == '__main__':
    # Run the Flask app
    app.logger.info("Iniciando o servidor Flask...")
    get_current_tag()  # Configure the database (check/create table)
    app.run(host='0.0.0.0', port=5000, debug=True)
