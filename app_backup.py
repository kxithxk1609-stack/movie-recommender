from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import pandas as pd
import random
import json
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_bcrypt import Bcrypt
from flask_session import Session

app = Flask(__name__)

# ============================================
# SECRET KEY & SESSION CONFIG
# ============================================
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)
bcrypt = Bcrypt(app)

# ============================================
# USER DATABASE (JSON File)
# ============================================
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

users = load_users()

# ============================================
# 60 MOVIES DATASET
# ============================================
movies = [
    # Tamil Movies
    {"id": 1, "title": "Vikram", "genre": "Action Crime Thriller", "year": 2022, "rating": 8.4, "language": "Tamil"},
    {"id": 2, "title": "Leo", "genre": "Action Crime Drama", "year": 2023, "rating": 7.8, "language": "Tamil"},
    {"id": 3, "title": "Jailer", "genre": "Action Comedy Drama", "year": 2023, "rating": 7.5, "language": "Tamil"},
    {"id": 4, "title": "Master", "genre": "Action Drama Thriller", "year": 2021, "rating": 7.8, "language": "Tamil"},
    {"id": 5, "title": "Baahubali", "genre": "Action Drama Fantasy", "year": 2015, "rating": 8.5, "language": "Tamil"},
    {"id": 6, "title": "KGF", "genre": "Action Crime Drama", "year": 2018, "rating": 8.2, "language": "Tamil"},
    {"id": 7, "title": "Soorarai Pottru", "genre": "Biography Drama", "year": 2020, "rating": 8.6, "language": "Tamil"},
    {"id": 8, "title": "Jai Bhim", "genre": "Crime Drama Legal", "year": 2021, "rating": 8.8, "language": "Tamil"},
    {"id": 9, "title": "Ponniyin Selvan 1", "genre": "Action Drama History", "year": 2022, "rating": 8.0, "language": "Tamil"},
    {"id": 10, "title": "Ponniyin Selvan 2", "genre": "Action Drama History", "year": 2023, "rating": 8.2, "language": "Tamil"},
    {"id": 11, "title": "Vikram Vedha", "genre": "Action Crime Thriller", "year": 2017, "rating": 8.0, "language": "Tamil"},
    {"id": 12, "title": "Kaithi", "genre": "Action Crime Thriller", "year": 2019, "rating": 8.2, "language": "Tamil"},
    {"id": 13, "title": "Super Deluxe", "genre": "Comedy Drama Thriller", "year": 2019, "rating": 8.3, "language": "Tamil"},
    {"id": 14, "title": "Vada Chennai", "genre": "Crime Drama Thriller", "year": 2018, "rating": 8.5, "language": "Tamil"},
    {"id": 15, "title": "Asuran", "genre": "Action Drama", "year": 2019, "rating": 8.4, "language": "Tamil"},
    
    # Hindi Movies
    {"id": 16, "title": "3 Idiots", "genre": "Comedy Drama", "year": 2009, "rating": 8.4, "language": "Hindi"},
    {"id": 17, "title": "Dangal", "genre": "Biography Drama Sport", "year": 2016, "rating": 8.4, "language": "Hindi"},
    {"id": 18, "title": "PK", "genre": "Comedy Drama Sci-Fi", "year": 2014, "rating": 8.1, "language": "Hindi"},
    {"id": 19, "title": "Bajrangi Bhaijaan", "genre": "Comedy Drama", "year": 2015, "rating": 8.0, "language": "Hindi"},
    {"id": 20, "title": "Hera Pheri", "genre": "Comedy Crime", "year": 2000, "rating": 8.2, "language": "Hindi"},
    {"id": 21, "title": "Andhadhun", "genre": "Comedy Crime Thriller", "year": 2018, "rating": 8.3, "language": "Hindi"},
    {"id": 22, "title": "Sholay", "genre": "Action Adventure Drama", "year": 1975, "rating": 8.2, "language": "Hindi"},
    {"id": 23, "title": "Lagaan", "genre": "Drama Sport", "year": 2001, "rating": 8.1, "language": "Hindi"},
    {"id": 24, "title": "Taare Zameen Par", "genre": "Drama", "year": 2007, "rating": 8.3, "language": "Hindi"},
    {"id": 25, "title": "Rang De Basanti", "genre": "Crime Drama", "year": 2006, "rating": 8.1, "language": "Hindi"},
    {"id": 26, "title": "Swades", "genre": "Drama", "year": 2004, "rating": 8.0, "language": "Hindi"},
    {"id": 27, "title": "Queen", "genre": "Comedy Drama", "year": 2014, "rating": 8.2, "language": "Hindi"},
    {"id": 28, "title": "Badhaai Ho", "genre": "Comedy Drama", "year": 2018, "rating": 7.9, "language": "Hindi"},
    {"id": 29, "title": "Stree", "genre": "Comedy Horror", "year": 2018, "rating": 7.5, "language": "Hindi"},
    {"id": 30, "title": "Munna Bhai MBBS", "genre": "Comedy Drama", "year": 2003, "rating": 8.2, "language": "Hindi"},
    
    # Malayalam Movies
    {"id": 31, "title": "Drishyam", "genre": "Crime Drama Thriller", "year": 2013, "rating": 8.6, "language": "Malayalam"},
    {"id": 32, "title": "Kumbalangi Nights", "genre": "Comedy Drama", "year": 2019, "rating": 8.6, "language": "Malayalam"},
    {"id": 33, "title": "Premam", "genre": "Comedy Drama Romance", "year": 2015, "rating": 8.0, "language": "Malayalam"},
    {"id": 34, "title": "Bangalore Days", "genre": "Comedy Drama Romance", "year": 2014, "rating": 8.0, "language": "Malayalam"},
    {"id": 35, "title": "Minnal Murali", "genre": "Action Comedy Superhero", "year": 2021, "rating": 8.0, "language": "Malayalam"},
    {"id": 36, "title": "Malik", "genre": "Action Crime Drama", "year": 2021, "rating": 8.2, "language": "Malayalam"},
    {"id": 37, "title": "Joji", "genre": "Crime Drama Thriller", "year": 2021, "rating": 8.0, "language": "Malayalam"},
    {"id": 38, "title": "Romancham", "genre": "Comedy Horror", "year": 2023, "rating": 8.0, "language": "Malayalam"},
    {"id": 39, "title": "Ayyappanum Koshiyum", "genre": "Action Drama", "year": 2020, "rating": 8.4, "language": "Malayalam"},
    {"id": 40, "title": "The Great Indian Kitchen", "genre": "Drama", "year": 2021, "rating": 8.0, "language": "Malayalam"},
    {"id": 41, "title": "Home", "genre": "Comedy Drama", "year": 2021, "rating": 8.0, "language": "Malayalam"},
    {"id": 42, "title": "Nayattu", "genre": "Crime Drama Thriller", "year": 2021, "rating": 8.0, "language": "Malayalam"},
    {"id": 43, "title": "Manichitrathazhu", "genre": "Horror Comedy Thriller", "year": 1993, "rating": 8.5, "language": "Malayalam"},
    {"id": 44, "title": "Devasuram", "genre": "Action Drama", "year": 1993, "rating": 8.0, "language": "Malayalam"},
    {"id": 45, "title": "Bharatham", "genre": "Drama", "year": 1991, "rating": 8.2, "language": "Malayalam"},
    
    # English Movies
    {"id": 46, "title": "The Dark Knight", "genre": "Action Crime Drama", "year": 2008, "rating": 9.0, "language": "English"},
    {"id": 47, "title": "Inception", "genre": "Action Sci-Fi Thriller", "year": 2010, "rating": 8.8, "language": "English"},
    {"id": 48, "title": "Interstellar", "genre": "Adventure Drama Sci-Fi", "year": 2014, "rating": 8.6, "language": "English"},
    {"id": 49, "title": "The Matrix", "genre": "Action Sci-Fi", "year": 1999, "rating": 8.7, "language": "English"},
    {"id": 50, "title": "Pulp Fiction", "genre": "Crime Drama Thriller", "year": 1994, "rating": 8.9, "language": "English"},
    {"id": 51, "title": "Fight Club", "genre": "Drama Thriller", "year": 1999, "rating": 8.8, "language": "English"},
    {"id": 52, "title": "Forrest Gump", "genre": "Comedy Drama Romance", "year": 1994, "rating": 8.8, "language": "English"},
    {"id": 53, "title": "The Godfather", "genre": "Crime Drama", "year": 1972, "rating": 9.2, "language": "English"},
    {"id": 54, "title": "The Shawshank Redemption", "genre": "Drama", "year": 1994, "rating": 9.3, "language": "English"},
    {"id": 55, "title": "The Lord of the Rings", "genre": "Adventure Fantasy", "year": 2001, "rating": 8.8, "language": "English"},
    {"id": 56, "title": "Star Wars", "genre": "Action Adventure Sci-Fi", "year": 1977, "rating": 8.6, "language": "English"},
    {"id": 57, "title": "The Avengers", "genre": "Action Adventure Sci-Fi", "year": 2012, "rating": 8.0, "language": "English"},
    {"id": 58, "title": "Gladiator", "genre": "Action Adventure Drama", "year": 2000, "rating": 8.5, "language": "English"},
    {"id": 59, "title": "Titanic", "genre": "Drama Romance", "year": 1997, "rating": 7.8, "language": "English"},
    {"id": 60, "title": "The Lion King", "genre": "Animation Adventure Drama", "year": 1994, "rating": 8.5, "language": "English"},
]

df = pd.DataFrame(movies)

# ============================================
# MACHINE LEARNING MODEL
# ============================================
vectorizer = TfidfVectorizer(stop_words='english')
feature_matrix = vectorizer.fit_transform(df['genre'])
similarity = cosine_similarity(feature_matrix)

def get_recommendations(title, n=5, exclude_language=None):
    try:
        idx = df[df['title'].str.lower() == title.lower()].index[0]
        scores = list(enumerate(similarity[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        recommendations = []
        for i in scores[1:]:
            movie = df.iloc[i[0]].to_dict()
            if exclude_language and movie['language'] == exclude_language:
                continue
            recommendations.append(movie)
            if len(recommendations) >= n:
                break
        return recommendations
    except:
        return None

# ============================================
# ADMIN CREDENTIALS
# ============================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def is_admin():
    return session.get('is_admin', False)

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return render_template('register.html')
        
        if username in users:
            flash('Username already exists!', 'danger')
            return render_template('register.html')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users[username] = {
            'email': email,
            'password': hashed_password,
            'created_at': datetime.now().isoformat(),
            'watchlist': [],
            'ratings': {},
            'preferences': {'languages': [], 'genres': []}
        }
        save_users(users)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username not in users:
            flash('Invalid username or password!', 'danger')
            return render_template('login.html')
        
        if not bcrypt.check_password_hash(users[username]['password'], password):
            flash('Invalid username or password!', 'danger')
            return render_template('login.html')
        
        session['username'] = username
        session['user'] = users[username]
        
        flash(f'Welcome back, {username}!', 'success')
        return redirect(url_for('home'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('Please login to view your profile.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=session['user'])

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    if request.method == 'POST':
        if 'preferences' in request.form:
            session['user']['preferences'] = {
                'languages': request.form.getlist('languages'),
                'genres': request.form.getlist('genres')
            }
            users[username]['preferences'] = session['user']['preferences']
            save_users(users)
            flash('Preferences updated!', 'success')
        
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=session['user'])

# ============================================
# WATCHLIST ROUTES
# ============================================

@app.route('/watchlist')
def watchlist():
    if 'username' not in session:
        flash('Please login to view your watchlist.', 'warning')
        return redirect(url_for('login'))
    
    watchlist = session['user'].get('watchlist', [])
    watchlist_movies = [m for m in movies if m['id'] in watchlist]
    
    return render_template('watchlist.html', movies=watchlist_movies)

@app.route('/watchlist/add/<int:movie_id>', methods=['POST'])
def add_to_watchlist(movie_id):
    if 'username' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    username = session['username']
    if movie_id not in session['user']['watchlist']:
        session['user']['watchlist'].append(movie_id)
        users[username]['watchlist'] = session['user']['watchlist']
        save_users(users)
        return jsonify({'message': 'Added to watchlist!'})
    
    return jsonify({'message': 'Already in watchlist!'})

@app.route('/watchlist/remove/<int:movie_id>', methods=['POST'])
def remove_from_watchlist(movie_id):
    if 'username' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    username = session['username']
    if movie_id in session['user']['watchlist']:
        session['user']['watchlist'].remove(movie_id)
        users[username]['watchlist'] = session['user']['watchlist']
        save_users(users)
        return jsonify({'message': 'Removed from watchlist!'})
    
    return jsonify({'error': 'Movie not in watchlist'}), 404

# ============================================
# RATING ROUTES
# ============================================

@app.route('/rate/<int:movie_id>', methods=['GET', 'POST'])
def rate_movie_page(movie_id):
    if 'username' not in session:
        flash('Please login to rate movies!', 'warning')
        return redirect(url_for('login'))
    
    movie = None
    for m in movies:
        if m['id'] == movie_id:
            movie = m
            break
    
    if not movie:
        flash('Movie not found!', 'danger')
        return redirect(url_for('home'))
    
    current_rating = session['user']['ratings'].get(str(movie_id), None)
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        if rating and rating.isdigit() and 1 <= int(rating) <= 5:
            username = session['username']
            session['user']['ratings'][str(movie_id)] = int(rating)
            users[username]['ratings'] = session['user']['ratings']
            save_users(users)
            flash(f'⭐ You rated "{movie["title"]}" {rating}/5!', 'success')
            return redirect(url_for('rate_movie_page', movie_id=movie_id))
        else:
            flash('Please select a valid rating (1-5)!', 'danger')
    
    return render_template('rate.html', movie=movie, current_rating=current_rating)

@app.route('/my-ratings')
def my_ratings():
    if 'username' not in session:
        flash('Please login to view your ratings!', 'warning')
        return redirect(url_for('login'))
    
    user_ratings = session['user']['ratings']
    rated_movies = []
    
    for movie_id, rating in user_ratings.items():
        for m in movies:
            if str(m['id']) == movie_id:
                rated_movies.append({
                    'movie': m,
                    'rating': rating
                })
                break
    
    return render_template('my_ratings.html', rated_movies=rated_movies)

@app.route('/rated-recommendations')
def rated_recommendations():
    if 'username' not in session:
        flash('Please login to get personalized recommendations!', 'warning')
        return redirect(url_for('login'))
    
    user_ratings = session['user']['ratings']
    
    if not user_ratings:
        flash('You haven\'t rated any movies yet! Rate some movies to get recommendations.', 'info')
        return redirect(url_for('home'))
    
    best_rated_id = max(user_ratings, key=user_ratings.get)
    best_rated_movie = None
    
    for m in movies:
        if str(m['id']) == best_rated_id:
            best_rated_movie = m
            break
    
    if not best_rated_movie:
        flash('Something went wrong!', 'danger')
        return redirect(url_for('home'))
    
    recs = get_recommendations(best_rated_movie['title'], n=10)
    rated_ids = [int(id) for id in user_ratings.keys()]
    recs = [r for r in recs if r['id'] not in rated_ids]
    
    return render_template('recommendations.html', 
                         movie=best_rated_movie, 
                         recommendations=recs[:8],
                         title='Based on your highest rated movie')

# ============================================
# ADMIN ROUTES
# ============================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            session['username'] = 'Admin'
            flash('Welcome Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin():
        flash('Please login as admin!', 'warning')
        return redirect(url_for('admin_login'))
    
    # Statistics
    total_users = len(users)
    total_movies = len(movies)
    total_ratings = sum(len(u['ratings']) for u in users.values())
    total_watchlist = sum(len(u['watchlist']) for u in users.values())
    
    # FIXED: Calculate average rating - handles zero ratings
    all_ratings = []
    for u in users.values():
        all_ratings.extend(u['ratings'].values())
    
    if all_ratings:
        avg_rating = round(sum(all_ratings) / len(all_ratings), 1)
    else:
        avg_rating = 0
    
    # Language distribution
    lang_dist = df['language'].value_counts().to_dict()
    
    # Rating distribution
    rating_dist = {}
    for u in users.values():
        for r in u['ratings'].values():
            rating_dist[r] = rating_dist.get(r, 0) + 1
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_movies=total_movies,
                         total_ratings=total_ratings,
                         total_watchlist=total_watchlist,
                         avg_rating=avg_rating,
                         lang_dist=lang_dist,
                         rating_dist=rating_dist,
                         users=users)

@app.route('/admin/movies')
def admin_movies():
    if not is_admin():
        return redirect(url_for('admin_login'))
    return render_template('admin_movies.html', movies=movies)

@app.route('/admin/add_movie', methods=['GET', 'POST'])
def admin_add_movie():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        new_id = max([m['id'] for m in movies]) + 1
        new_movie = {
            'id': new_id,
            'title': request.form.get('title'),
            'genre': request.form.get('genre'),
            'year': int(request.form.get('year')),
            'rating': float(request.form.get('rating')),
            'language': request.form.get('language')
        }
        movies.append(new_movie)
        
        # Update DataFrame and model
        global df, feature_matrix, similarity
        df = pd.DataFrame(movies)
        feature_matrix = vectorizer.fit_transform(df['genre'])
        similarity = cosine_similarity(feature_matrix)
        
        flash(f'Movie "{new_movie["title"]}" added successfully!', 'success')
        return redirect(url_for('admin_movies'))
    
    return render_template('admin_add_movie.html')

@app.route('/admin/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def admin_edit_movie(movie_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if not movie:
        flash('Movie not found!', 'danger')
        return redirect(url_for('admin_movies'))
    
    if request.method == 'POST':
        movie['title'] = request.form.get('title')
        movie['genre'] = request.form.get('genre')
        movie['year'] = int(request.form.get('year'))
        movie['rating'] = float(request.form.get('rating'))
        movie['language'] = request.form.get('language')
        
        # Update DataFrame and model
        global df, feature_matrix, similarity
        df = pd.DataFrame(movies)
        feature_matrix = vectorizer.fit_transform(df['genre'])
        similarity = cosine_similarity(feature_matrix)
        
        flash(f'Movie "{movie["title"]}" updated successfully!', 'success')
        return redirect(url_for('admin_movies'))
    
    return render_template('admin_edit_movie.html', movie=movie)

@app.route('/admin/delete_movie/<int:movie_id>')
def admin_delete_movie(movie_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    global movies, df, feature_matrix, similarity
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if movie:
        movies.remove(movie)
        df = pd.DataFrame(movies)
        feature_matrix = vectorizer.fit_transform(df['genre'])
        similarity = cosine_similarity(feature_matrix)
        flash(f'Movie "{movie["title"]}" deleted successfully!', 'success')
    else:
        flash('Movie not found!', 'danger')
    
    return redirect(url_for('admin_movies'))

@app.route('/admin/users')
def admin_users():
    if not is_admin():
        return redirect(url_for('admin_login'))
    return render_template('admin_users.html', users=users)

@app.route('/admin/delete_user/<username>')
def admin_delete_user(username):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    if username in users:
        del users[username]
        save_users(users)
        flash(f'User "{username}" deleted successfully!', 'success')
    else:
        flash('User not found!', 'danger')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out from admin panel.', 'info')
    return redirect(url_for('home'))

# ============================================
# MAIN ROUTES
# ============================================

@app.route('/')
def home():
    user = session.get('user', None)
    all_titles = df['title'].tolist()
    random_movies = df.sample(n=10).to_dict('records')
    
    # Check if user is admin
    if is_admin():
        username = 'Admin'
    else:
        username = session.get('username')
    
    return render_template('index.html', 
                         movies=random_movies, 
                         all_titles=all_titles, 
                         current_lang='All',
                         user=user,
                         username=username,
                         is_admin=is_admin())

@app.route('/recommend', methods=['POST'])
def recommend():
    title = request.form.get('title')
    n = int(request.form.get('n', 5))
    language = request.form.get('language', 'All')
    
    if not title:
        return jsonify({'error': 'Please select a movie'})
    
    recs = get_recommendations(title, n)
    
    if recs is None:
        return jsonify({'error': 'Movie not found!'})
    
    if language != 'All':
        recs = [m for m in recs if m['language'] == language]
    
    return jsonify({'movie': title, 'recommendations': recs})

@app.route('/language/<lang>')
def language_movies(lang):
    filtered = df[df['language'].str.lower() == lang.lower()].to_dict('records')
    all_titles = df['title'].tolist()
    return render_template('index.html', 
                         movies=filtered, 
                         all_titles=all_titles, 
                         current_lang=lang.capitalize(),
                         user=session.get('user'),
                         username=session.get('username'),
                         is_admin=is_admin())

@app.route('/all')
def all_movies():
    all_titles = df['title'].tolist()
    return render_template('index.html', 
                         movies=df.to_dict('records'), 
                         all_titles=all_titles, 
                         current_lang='All',
                         user=session.get('user'),
                         username=session.get('username'),
                         is_admin=is_admin())

@app.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('q', '').lower()
    if query:
        results = df[df['title'].str.lower().str.contains(query)].to_dict('records')
    else:
        results = df.to_dict('records')
    return render_template('index.html', 
                         movies=results, 
                         all_titles=df['title'].tolist(), 
                         current_lang='Search Results',
                         user=session.get('user'),
                         username=session.get('username'),
                         is_admin=is_admin())

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🎬 MOVIE RECOMMENDER WITH ADMIN ⭐")
    print("="*50)
    print(f"📊 Total Movies: {len(df)}")
    print(f"   - Tamil: {len(df[df['language'] == 'Tamil'])}")
    print(f"   - Hindi: {len(df[df['language'] == 'Hindi'])}")
    print(f"   - Malayalam: {len(df[df['language'] == 'Malayalam'])}")
    print(f"   - English: {len(df[df['language'] == 'English'])}")
    print(f"👥 Registered Users: {len(users)}")
    print("🌐 Open: http://127.0.0.1:5000")
    print("🔑 Admin Login: /admin/login (admin/admin123)")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)