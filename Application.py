from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

def initialize_db():
    """Initialize the database with sample jobs"""
    if os.path.exists('jobs.db'):
        os.remove('jobs.db')
    
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        skills TEXT NOT NULL,
        disability_support TEXT NOT NULL
    )
    """)

    sample_jobs = [
        ("Software Developer", "Python,JavaScript,HTML", "Visual,Hearing"),
        ("Data Analyst", "SQL,Python,Excel", "Mobility"),
        ("Graphic Designer", "Photoshop,Illustrator,Creativity", "Hearing"),
        ("Customer Service Representative", "Communication,Problem-Solving,Empathy", "Cognitive"),
        ("Content Writer", "Writing,Creativity,Time Management", "Visual,Mobility"),
        ("Tutor", "Teaching,Patience,Communication", "Hearing,Cognitive"),
        ("Handicraft Artist", "Creativity,Attention to Detail,Crafting", "Mobility")
    ]

    cursor.executemany("""
    INSERT INTO jobs (title, skills, disability_support)
    VALUES (?, ?, ?)
    """, sample_jobs)

    conn.commit()
    conn.close()

def get_matching_jobs(skills, disabilities):
    """Query the database for matching jobs"""
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT * FROM jobs 
        WHERE skills LIKE ? 
        AND disability_support LIKE ?
        """
        skills_pattern = f"%{','.join(skills)}%"
        disability_pattern = f"%{','.join(disabilities)}%"
        
        cursor.execute(query, (skills_pattern, disability_pattern))
        results = cursor.fetchall()
        
        return [{
            "id": row[0],
            "title": row[1],
            "skills": row[2],
            "disability_support": row[3]
        } for row in results]
        
    finally:
        conn.close()


@app.route('/')


@app.route('/search', methods=['POST', 'OPTIONS'])
def handle_search():
    """Handle the search request with CORS support"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    # Main request handling
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '')
        disabilities = request.form.getlist('disabilities')
        skills = request.form.getlist('skills')
        document = request.files.get('document')

        # Validate inputs
        errors = []
        if not name:
            errors.append("Name is required")
        if not age.isdigit() or int(age) < 1:
            errors.append("Valid age is required")
        if not disabilities:
            errors.append("At least one disability must be selected")
        if not skills:
            errors.append("At least one skill must be selected")
        if not document:
            errors.append("Document upload is required")

        if errors:
            return jsonify({"error": "Validation failed", "messages": errors}), 400

        # Get matching jobs
        jobs = get_matching_jobs(skills, disabilities)

        # Build response
        response = jsonify(jobs)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

if __name__ == '__main__':
    initialize_db()  # Initialize database on startup
    app.run(debug=True)