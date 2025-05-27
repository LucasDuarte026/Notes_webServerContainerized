from flask import Flask, render_template, jsonify, request
import psycopg2 as sql
from psycopg2 import OperationalError, ProgrammingError
import logging # Import logging module
import re # Import regex for email validation

# Configure logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

app.config['POSTGRES_HOST'] = 'db'
app.config['POSTGRES_PORT'] = '5432'
app.config['POSTGRES_DB'] = 'pn_database'
app.config['POSTGRES_USER'] = 'lucas'
app.config['POSTGRES_PASSWORD'] = '1234'

def get_db_connection():
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
    current_tag=None
    conn, cur = None,None
    conn = get_db_connection()
    if not conn:
        app.logger.error("Could not get database connection for configuration.")
        return

    # Check if table exists before trying to select from it
    cur = conn.cursor()
    cur.execute("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename  = 'notes');")
    table_exists = cur.fetchone()[0]

    try:
        if table_exists:
            # IMPORTANT: Adjust this SELECT statement if your table columns are different
            cur.execute("SELECT MAX(tag) FROM notes;") # Select specific columns

            highest_tag = cur.fetchone()

            if highest_tag:
                current_tag = int(highest_tag[0])
                app.logger.info(f"highest_tag: {current_tag}")
            else:
                app.logger.info("problem with tag value.")
        else:
            app.logger.warning("Table 'notes' does not exist. Please create it manually if needed.")
    

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
    if not conn:
        app.logger.error("Failed to get database connection for note creation.")
        return jsonify({'error': 'Failed to connect to the database.'}), 500

    cursor = None


    tag = get_current_tag()
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


if __name__ == '__main__':
    # Run the Flask app
    app.logger.info("Iniciando o servidor Flask...")
    get_current_tag()  # Configure the database (check/create table)
    app.run(host='0.0.0.0', port=5000, debug=True)
