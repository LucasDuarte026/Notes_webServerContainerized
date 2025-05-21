from flask import Flask, render_template, jsonify, request
import psycopg2 as sql
from psycopg2 import OperationalError, ProgrammingError

app = Flask(__name__)

app.config['POSTGRES_HOST'] = 'db'
app.config['POSTGRES_PORT'] = '5432'
app.config['POSTGRES_DB'] = 'pn_database'
app.config['POSTGRES_USER'] = 'lucas'
app.config['POSTGRES_PASSWORD'] = '1234'

def get_db_connection():
    conn = None
    try:
        conn = sql.connect(
            host=app.config['POSTGRES_HOST'],
            port=app.config['POSTGRES_PORT'],
            database=app.config['POSTGRES_DB'],
            user=app.config['POSTGRES_USER'],
            password=app.config['POSTGRES_PASSWORD']
        )
        print("Successfully connected to the database!")  # Add a success message
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        # Consider logging the error for debugging
    return conn


@app.route('/')
def main_page():
    return render_template('create_page.html')

@app.route('/search')
def search_page():
    return render_template('search_page.html')

@app.route('/notesperuser')
def user_page():
    return render_template('user_page.html')



@app.route('/create_note', methods=['POST'])
def create_note():
 
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    cursor = None
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['tag', 'name', 'email', 'text']):
            return jsonify({'error': 'Missing required data (tag, name, email, text)'}), 400

        tag = data['tag']
        name = data['name']
        email = data['email']
        text = data['text']

        cursor = conn.cursor()
        query = "INSERT INTO notes (tag, name, email, text) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (tag, name, email, text))
        conn.commit()
        return jsonify({'message': 'Note successfully created'}), 201

    except ProgrammingError as e:
        if conn:
            conn.rollback()
        return jsonify({'error': f"Database error: {e}"}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': f"An unexpected error occurred: {e}"}), 500
    finally:
        if cursor:
            cursor.close()
        conn.close()

def config_database():
   
    conn = None
    cur = None
    try:
        conn = sql.connect(
            dbname="postgres", 
            user="postgres",  
            password="",
            host="localhost",
        )
        conn.autocommit = True  

        cur = conn.cursor()

        cur.execute("CREATE DATABASE pn_database;")

        cur.execute("CREATE USER lucas WITH PASSWORD '1234';")

        cur.execute("ALTER DATABASE pn_database OWNER TO lucas;")

        conn.close()  
        conn = sql.connect( 
            dbname="pn_database",
            user="lucas",  
            password="1234",
            host="localhost",
        )
        cur = conn.cursor()

     
        cur.execute("""
            CREATE TABLE notes (
                tag NUMERIC(4) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                text TEXT NOT NULL
            );
        """)

        cur.execute("ALTER TABLE notes OWNER TO lucas;")

        conn.commit()
        print("Banco de dados, usuário e tabela criados com sucesso.")

    except sql.Error as e:
        print(f"Erro ao configurar o banco de dados: {e}")
        if conn:
            conn.rollback()  # Rollback em caso de erro

    finally:
        # Fecha o cursor e a conexão
        if cur:
            cur.close()
        if conn:
            conn.close()
if __name__ == '__main__':
    # Run the Flask app
    print("Iniciando o servidor Flask...")
    config_database()
    app.run(host='0.0.0.0', port=5000, debug=True)