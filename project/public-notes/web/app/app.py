from flask import Flask, render_template

app = Flask(__name__)

# from app import routes

@app.route('/')
def main_page():
    return render_template('create_page.html')

@app.route('/search')
def search_page():
    return render_template('search_page.html')

@app.route('/notesperuser')
def user_page():
    return render_template('user_page.html')



if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)