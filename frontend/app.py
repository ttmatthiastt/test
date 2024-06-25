from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from flask_cors import CORS
import os
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

BACKEND_ENDPOINT = 'http://localhost:5001'

# Path to the JSON file
REVIEWS_FILE = os.path.join(app.root_path, 'reviews.json')

def load_reviews():
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_reviews(reviews):
    with open(REVIEWS_FILE, 'w') as file:
        json.dump(reviews, file, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/favourites')
def favourites():
    return render_template('favourites.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/reviews')
def reviews():
    all_reviews = load_reviews()
    sort_by = request.args.get('sort_by', 'newest')

    if sort_by == 'alphabetical':
        all_reviews = sorted(all_reviews, key=lambda x: x['title'].lower())
    elif sort_by == 'newest':
        all_reviews = sorted(all_reviews, key=lambda x: datetime.strptime(x['created_at'], '%Y-%m-%d %H:%M:%S'), reverse=True)
    elif sort_by == 'oldest':
        all_reviews = sorted(all_reviews, key=lambda x: datetime.strptime(x['created_at'], '%Y-%m-%d %H:%M:%S'))

    return render_template('reviews.html', reviews=all_reviews)


@app.route('/create_review', methods=['POST'])
def create_review():
    title = request.form.get('title')  # Use get to avoid KeyError
    content = request.form.get('content')
    if not title or not content:
        return "Missing title or content", 400
    
    all_reviews = load_reviews()
    new_review = {
        'id': len(all_reviews) + 1,
        'title': title,
        'content': content,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    all_reviews.append(new_review)
    save_reviews(all_reviews)
    return redirect(url_for('reviews'))

@app.route('/suggestions')
def suggestions():
    query = request.args.get('query')
    popularity = request.args.get('popularity')

    if not query or not popularity:
        return redirect(url_for('search'))

    try:
        response = requests.get(f'{BACKEND_ENDPOINT}/recommendations', params={'song_name': query, 'popularity': popularity})
        response.raise_for_status()
        suggestions = response.json()
    except requests.RequestException as e:
        print(f"Error fetching recommendations: {e}")
        suggestions = []

    return render_template('suggestions.html', query=query, suggestions=suggestions)
@app.route('/delete_review', methods=['POST'])
def delete_review():
    review_id = int(request.form['review_id'])
    all_reviews = load_reviews()
    all_reviews = [review for review in all_reviews if review['id'] != review_id]
    save_reviews(all_reviews)
    return redirect(url_for('reviews'))

@app.route('/update_review', methods=['POST'])
def update_review():
    review_id = int(request.form['review_id'])
    all_reviews = load_reviews()
    for review in all_reviews:
        if review['id'] == review_id:
            title = request.form.get('title')
            content = request.form.get('content')
            if title:
                review['title'] = title
            if content:
                review['content'] = content
            review['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    save_reviews(all_reviews)
    return redirect(url_for('reviews'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
