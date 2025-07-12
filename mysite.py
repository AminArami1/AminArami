import os
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_from_directory, jsonify
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuration
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg'}
CONTENT_FILE = 'content.json'

# Admin users
ADMIN_USERS = {
    'AminArami': 'Am1680454481',
    'AmirMohammadSezavar': '1234566'
}

# Platforms and actions
PLATFORMS = {
    'Video Platforms': ['YouTube', 'TikTok', 'Instagram', 'Snapchat', 'Likee', 'Twitch'],
    'Messaging Apps': ['Telegram', 'WhatsApp', 'Signal', 'Messenger'],
    'Social Platforms': ['TwitterX', 'Threads', 'Reddit', 'Pinterest'],
    'Professional': ['LinkedIn'],
    'Design & Art': ['Behance', 'DeviantArt'],
    'Music': ['Spotify', 'SoundCloud']
}
ACTIONS = ['Create Account', 'Delete Account', 'Increase Followers', 'Prevent Hacking']

def allowed_file(filename, file_type='image'):
    allowed_extensions = ALLOWED_IMAGE_EXTENSIONS if file_type == 'image' else ALLOWED_VIDEO_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def load_content():
    try:
        if os.path.exists(CONTENT_FILE):
            with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading content: {e}")
    
    # Initialize content structure if file doesn't exist or is corrupted
    content = {}
    for category, platforms in PLATFORMS.items():
        for platform in platforms:
            content[platform] = {}
            for action in ACTIONS:
                action_key = action.lower().replace(' ', '_')
                content[platform][action_key] = {
                    'text': f"Guide for {action} on {platform}",
                    'images': [],
                    'videos': [],
                    'additional_content': ''
                }
    return content

def save_content(content):
    try:
        with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving content: {e}")
        flash('Error saving content', 'error')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Platform Account Guides</title>
    <style>
        /* Modern, clean CSS */
        :root {
            --primary: #00695c;
            --primary-light: #00796b;
            --primary-dark: #004d40;
            --text: #333;
            --text-light: #777;
            --bg: #f5f5f5;
            --card-bg: #fff;
            --shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        body.dark-mode {
            --primary: #00796b;
            --primary-light: #00897b;
            --primary-dark: #006064;
            --text: #e0e0e0;
            --text-light: #b0b0b0;
            --bg: #121212;
            --card-bg: #1e1e1e;
            --shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            transition: all 0.3s ease;
        }
        header {
            background: var(--primary);
            color: white;
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--shadow);
        }
        nav {
            background: var(--primary-dark);
            padding: 1rem;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        nav a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1.5rem;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        nav a:hover {
            background: var(--primary-light);
            transform: translateY(-2px);
        }
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .card {
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }
        .platform-card {
            margin-bottom: 2rem;
        }
        .action-link {
            display: block;
            color: var(--primary);
            text-decoration: none;
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-left: 3px solid var(--primary-light);
            transition: all 0.3s ease;
            border-radius: 4px;
        }
        .action-link:hover {
            background: rgba(0, 121, 107, 0.1);
            transform: translateX(5px);
        }
        #searchInput {
            width: 100%;
            padding: 1rem;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            background: var(--card-bg);
            color: var(--text);
        }
        #searchInput:focus {
            border-color: var(--primary-light);
            outline: none;
            box-shadow: 0 0 0 3px rgba(0, 121, 107, 0.2);
        }
        .search-results {
            background: var(--card-bg);
            border-radius: 8px;
            box-shadow: var(--shadow);
            max-height: 300px;
            overflow-y: auto;
            display: none;
            position: absolute;
            width: calc(100% - 2rem);
            z-index: 100;
        }
        .search-result {
            padding: 1rem;
            border-bottom: 1px solid var(--primary-dark);
            transition: all 0.2s ease;
        }
        .search-result:hover {
            background: rgba(0, 121, 107, 0.1);
        }
        .search-highlight {
            background-color: #fff9c4;
            font-weight: bold;
            padding: 0 2px;
            border-radius: 3px;
            color: #333;
        }
        .btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }
        .content-media {
            max-width: 100%;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: var(--shadow);
        }
        .admin-form {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: var(--primary-light);
        }
        .form-control {
            width: 100%;
            padding: 0.8rem;
            border: 1px solid var(--primary-dark);
            border-radius: 4px;
            font-size: 1rem;
            background: var(--bg);
            color: var(--text);
        }
        textarea.form-control {
            min-height: 150px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .action-tabs {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }
        .action-tab {
            padding: 0.5rem 1rem;
            background: var(--primary-light);
            color: white;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .action-tab.active {
            background: var(--primary-dark);
        }
        .action-tab:hover {
            transform: translateY(-2px);
        }
        /* Dark mode toggle */
        .dark-mode-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--primary);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: var(--shadow);
            z-index: 1000;
            border: none;
            outline: none;
        }
        /* Content page styles */
        .content-page {
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .content-page img, 
        .content-page video {
            max-width: 100%;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: var(--shadow);
        }
        .error-message {
            color: #d32f2f;
            background-color: #fde8e8;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
        }
        .url-option {
            margin: 10px 0;
            text-align: center;
            font-weight: bold;
            color: var(--primary);
        }
        /* New styles for multiple media */
        .media-list {
            margin-bottom: 1rem;
        }
        .media-item {
            display: flex;
            align-items: center;
            padding: 0.5rem;
            background: rgba(0, 121, 107, 0.1);
            border-radius: 4px;
            margin-bottom: 0.5rem;
        }
        .media-item a {
            flex-grow: 1;
            margin-right: 1rem;
            word-break: break-all;
        }
        .media-item button {
            background: #d32f2f;
            color: white;
            border: none;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            cursor: pointer;
        }
        .media-input-group {
            margin-bottom: 1rem;
        }
        .add-media-btn {
            background: var(--primary-light);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 0.5rem;
        }
        .add-media-btn:hover {
            background: var(--primary-dark);
        }
    </style>
</head>
<body class="{% if 'dark_mode' in session %}dark-mode{% endif %}">
    <header>
        <h1>Platform Account Guides</h1>
        <p>Complete tutorials for account management on all major platforms</p>
    </header>

    <nav>
        <a href="{{ url_for('index') }}">Home</a>
        <a href="#search">Search</a>
        {% if 'admin' in session %}
            <a href="#admin">Admin Panel</a>
            <a href="{{ url_for('logout') }}">Logout</a>
        {% else %}
            <a href="#admin">Admin Login</a>
        {% endif %}
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="card error-message">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <section id="home" class="card">
            <h2>Platform Guides</h2>
            <div id="platformList">
                {% for category, platforms in PLATFORMS.items() %}
                <div class="platform-card card">
                    <h3>{{ category }}</h3>
                    {% for platform in platforms %}
                    <div class="platform-item">
                        <h4>{{ platform }}</h4>
                        <div class="action-links">
                            {% for action in ACTIONS %}
                                {% set action_key = action.lower().replace(' ', '_') %}
                                <a class="action-link" 
                                   href="{{ url_for('content_page', platform=platform, action=action_key) }}"
                                   data-platform="{{ platform }}"
                                   data-action="{{ action_key }}">
                                    {{ action }}
                                </a>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
        </section>

        <section id="search" class="card">
            <h2>Search Guides</h2>
            <div style="position: relative;">
                <input type="text" id="searchInput" placeholder="Search for platform or action..." autocomplete="off">
                <div id="searchResults" class="search-results"></div>
            </div>
        </section>

        {% if 'admin' in session %}
        <section id="admin" class="card">
            <div class="admin-panel">
                <h2>Admin Panel</h2>
                {% for category, platforms in PLATFORMS.items() %}
                    <h3>{{ category }}</h3>
                    {% for platform in platforms %}
                        <div class="platform-section card">
                            <h4>{{ platform }}</h4>
                            <div class="action-tabs">
                                {% for action in ACTIONS %}
                                    {% set action_key = action.lower().replace(' ', '_') %}
                                    <div class="action-tab {% if loop.first %}active{% endif %}" 
                                         onclick="showTab('{{ platform }}', '{{ action_key }}')">
                                        {{ action }}
                                    </div>
                                {% endfor %}
                            </div>
                            
                            {% for action in ACTIONS %}
                                {% set action_key = action.lower().replace(' ', '_') %}
                                <div id="{{ platform }}-{{ action_key }}-tab" class="tab-content {% if loop.first %}active{% endif %}">
                                    <form method="post" action="{{ url_for('update_content') }}" enctype="multipart/form-data" class="admin-form">
                                        <input type="hidden" name="platform" value="{{ platform }}">
                                        <input type="hidden" name="action_type" value="{{ action_key }}">
                                        
                                        <div class="form-group">
                                            <label>Main Content</label>
                                            <textarea name="content_text" class="form-control">{{ content[platform][action_key]['text'] }}</textarea>
                                        </div>
                                        
                                        <div class="form-group">
                                            <label>Additional Content</label>
                                            <textarea name="additional_content" class="form-control">{{ content[platform][action_key]['additional_content'] }}</textarea>
                                        </div>
                                        
                                        <div class="form-group">
                                            <label>Images</label>
                                            <div class="media-list" id="{{ platform }}-{{ action_key }}-images-list">
                                                {% for image in content[platform][action_key]['images'] %}
                                                    <div class="media-item">
                                                        <a href="{{ image if image.startswith('http') else url_for('static', filename='uploads/' + image.split('/')[-1]) }}" target="_blank">
                                                            {{ image }}
                                                        </a>
                                                        <button type="button" onclick="removeMedia('{{ platform }}', '{{ action_key }}', 'image', {{ loop.index0 }})">Remove</button>
                                                    </div>
                                                {% endfor %}
                                            </div>
                                            <div class="media-input-group">
                                                <input type="file" name="image_files" class="form-control" accept="image/*" multiple>
                                                <div class="url-option">OR</div>
                                                <input type="text" name="image_urls" class="form-control" placeholder="Enter image URLs (separate by comma)">
                                            </div>
                                        </div>
                                        
                                        <div class="form-group">
                                            <label>Videos</label>
                                            <div class="media-list" id="{{ platform }}-{{ action_key }}-videos-list">
                                                {% for video in content[platform][action_key]['videos'] %}
                                                    <div class="media-item">
                                                        <a href="{{ video if video.startswith('http') else url_for('static', filename='uploads/' + video.split('/')[-1]) }}" target="_blank">
                                                            {{ video }}
                                                        </a>
                                                        <button type="button" onclick="removeMedia('{{ platform }}', '{{ action_key }}', 'video', {{ loop.index0 }})">Remove</button>
                                                    </div>
                                                {% endfor %}
                                            </div>
                                            <div class="media-input-group">
                                                <input type="file" name="video_files" class="form-control" accept="video/*" multiple>
                                                <div class="url-option">OR</div>
                                                <input type="text" name="video_urls" class="form-control" placeholder="Enter video URLs (separate by comma)">
                                            </div>
                                        </div>
                                        
                                        <button type="submit" class="btn">Save Content</button>
                                    </form>
                                </div>
                            {% endfor %}
                        </div>
                    {% endfor %}
                {% endfor %}
            </div>
        </section>
        {% else %}
        <section id="admin" class="card">
            <div class="admin-login">
                <h2>Admin Login</h2>
                {% if login_error %}
                    <div class="error-message">{{ login_error }}</div>
                {% endif %}
                <form method="post" action="{{ url_for('login') }}" class="admin-form">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="admin_user" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="admin_pass" class="form-control" required>
                    </div>
                    <button type="submit" class="btn">Login</button>
                </form>
            </div>
        </section>
        {% endif %}
    </div>

    <button class="dark-mode-toggle" onclick="toggleDarkMode()">
        {% if 'dark_mode' in session %}🌙{% else %}☀️{% endif %}
    </button>

    <script>
        // Advanced search functionality
        document.getElementById('searchInput').addEventListener('input', function() {
            const searchTerm = this.value.trim().toLowerCase();
            const resultsContainer = document.getElementById('searchResults');
            
            if (searchTerm.length < 2) {
                resultsContainer.style.display = 'none';
                return;
            }
            
            // Tokenize search terms and remove small words
            const searchTokens = searchTerm.split(' ')
                .filter(token => token.length > 2);
            
            if (searchTokens.length === 0) {
                resultsContainer.style.display = 'none';
                return;
            }
            
            const matches = [];
            const actionLinks = document.querySelectorAll('.action-link');
            
            actionLinks.forEach(link => {
                const linkText = link.textContent.toLowerCase();
                const platform = link.dataset.platform.toLowerCase();
                let matchScore = 0;
                let matchedTokens = [];
                
                // Score each token match
                searchTokens.forEach(token => {
                    // Check in platform name
                    if (platform.includes(token)) {
                        matchScore += 15; // Higher score for platform matches
                        matchedTokens.push(token);
                    }
                    
                    // Check in action text
                    if (linkText.includes(token)) {
                        const tokenWeight = token.length / searchTerm.length;
                        matchScore += tokenWeight * 10; // Base score
                        
                        // Bonus for exact matches
                        if (linkText === token || 
                            linkText.includes(` ${token} `) || 
                            linkText.startsWith(`${token} `) || 
                            linkText.endsWith(` ${token}`)) {
                            matchScore += 5;
                        }
                        
                        matchedTokens.push(token);
                    }
                });
                
                if (matchScore > 0) {
                    matches.push({
                        element: link,
                        score: matchScore,
                        text: link.textContent,
                        platform: link.dataset.platform,
                        action: link.dataset.action,
                        matchedTokens: matchedTokens
                    });
                }
            });
            
            // Sort by match score (best matches first)
            matches.sort((a, b) => b.score - a.score);
            
            if (matches.length > 0) {
                resultsContainer.innerHTML = '';
                
                // Group by platform for better organization
                const platformGroups = {};
                
                matches.forEach(match => {
                    if (!platformGroups[match.platform]) {
                        platformGroups[match.platform] = [];
                    }
                    platformGroups[match.platform].push(match);
                });
                
                // Display results grouped by platform
                for (const [platform, platformMatches] of Object.entries(platformGroups)) {
                    const platformHeader = document.createElement('div');
                    platformHeader.className = 'search-result';
                    platformHeader.innerHTML = `<strong>${platform}</strong>`;
                    resultsContainer.appendChild(platformHeader);
                    
                    platformMatches.forEach(match => {
                        let highlightedText = match.text;
                        
                        // Highlight all matched tokens
                        match.matchedTokens.forEach(token => {
                            const regex = new RegExp(token, 'gi');
                            highlightedText = highlightedText.replace(regex, 
                                `<span class="search-highlight">$&</span>`);
                        });
                        
                        const resultItem = document.createElement('div');
                        resultItem.className = 'search-result';
                        resultItem.innerHTML = `
                            <a href="/content/${match.platform}/${match.action}">
                                ${highlightedText}
                            </a>`;
                        resultsContainer.appendChild(resultItem);
                    });
                }
                
                resultsContainer.style.display = 'block';
            } else {
                resultsContainer.innerHTML = '<div class="search-result">No results found</div>';
                resultsContainer.style.display = 'block';
            }
        });

        // Close search results when clicking elsewhere
        document.addEventListener('click', function(e) {
            const searchContainer = document.querySelector('#search');
            if (!searchContainer.contains(e.target)) {
                document.getElementById('searchResults').style.display = 'none';
            }
        });

        // Tab switching in admin panel
        function showTab(platform, action) {
            // Hide all tabs for this platform
            const section = document.querySelector(`#${platform}-${action}-tab`).closest('.platform-section');
            section.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(`${platform}-${action}-tab`).classList.add('active');
            
            // Update active tab styling
            section.querySelectorAll('.action-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
        }

        // Dark mode toggle
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode);
            
            // Update toggle button icon
            const toggleBtn = document.querySelector('.dark-mode-toggle');
            if (isDarkMode) {
                toggleBtn.innerHTML = '🌙';
            } else {
                toggleBtn.innerHTML = '☀️';
            }
            
            // Send to server to store in session
            fetch('/toggle_dark_mode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ dark_mode: isDarkMode })
            });
        }

        // Initialize dark mode if previously set
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
            document.querySelector('.dark-mode-toggle').innerHTML = '🌙';
        }

        // Remove media (image or video)
        function removeMedia(platform, action, mediaType, index) {
            if (confirm(`Are you sure you want to remove this ${mediaType}?`)) {
                fetch('/remove_media', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        platform: platform,
                        action: action,
                        media_type: mediaType,
                        index: index
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error removing media');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error removing media');
                });
            }
        }
    </script>
</body>
</html>
"""

CONTENT_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ platform }} - {{ action }}</title>
    <style>
        :root {
            --primary: #00695c;
            --primary-light: #00796b;
            --primary-dark: #004d40;
            --text: #333;
            --text-light: #777;
            --bg: #f5f5f5;
            --card-bg: #fff;
            --shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        body.dark-mode {
            --primary: #00796b;
            --primary-light: #00897b;
            --primary-dark: #006064;
            --text: #e0e0e0;
            --text-light: #b0b0b0;
            --bg: #121212;
            --card-bg: #1e1e1e;
            --shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            transition: all 0.3s ease;
        }
        .content-page {
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .content-card {
            background: var(--card-bg);
            border-radius: 8px;
            padding: 2rem;
            box-shadow: var(--shadow);
        }
        .content-card img, 
        .content-card video {
            max-width: 100%;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: var(--shadow);
        }
        .back-btn {
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 0.8rem 1.5rem;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 1rem;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }
        .dark-mode-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--primary);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: var(--shadow);
            z-index: 1000;
            border: none;
            outline: none;
        }
        /* Media gallery styles */
        .media-gallery {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin: 1rem 0;
        }
        .media-item {
            flex: 1 1 300px;
            max-width: 100%;
        }
    </style>
</head>
<body class="{% if 'dark_mode' in session %}dark-mode{% endif %}">
    <div class="content-page">
        <div class="content-card">
            <h1>{{ platform }} - {{ action }}</h1>
            
            <div class="content-text">
                {{ content.text.replace('\n', '<br>') | safe }}
            </div>
            
            {% if content.additional_content %}
            <div class="additional-content">
                {{ content.additional_content.replace('\n', '<br>') | safe }}
            </div>
            {% endif %}
            
            {% if content.images %}
            <h3>Images</h3>
            <div class="media-gallery">
                {% for image in content.images %}
                    {% if image.startswith('http') %}
                        <div class="media-item">
                            <img src="{{ image }}" alt="{{ platform }} {{ action }} image {{ loop.index }}">
                        </div>
                    {% else %}
                        <div class="media-item">
                            <img src="{{ url_for('static', filename='uploads/' + image.split('/')[-1]) }}" 
                                 alt="{{ platform }} {{ action }} image {{ loop.index }}">
                        </div>
                    {% endif %}
                {% endfor %}
            </div>
            {% endif %}
            
            {% if content.videos %}
            <h3>Videos</h3>
            <div class="media-gallery">
                {% for video in content.videos %}
                    {% if video.startswith('http') %}
                        <div class="media-item">
                            <video controls>
                                <source src="{{ video }}" type="video/mp4">
                            </video>
                        </div>
                    {% else %}
                        <div class="media-item">
                            <video controls>
                                <source src="{{ url_for('static', filename='uploads/' + video.split('/')[-1]) }}" 
                                        type="video/mp4">
                            </video>
                        </div>
                    {% endif %}
                {% endfor %}
            </div>
            {% endif %}
            
            <a href="{{ url_for('index') }}" class="back-btn">Back to All Guides</a>
        </div>
    </div>

    <button class="dark-mode-toggle" onclick="toggleDarkMode()">
        {% if 'dark_mode' in session %}🌙{% else %}☀️{% endif %}
    </button>

    <script>
        // Dark mode toggle
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode);
            
            // Update toggle button icon
            const toggleBtn = document.querySelector('.dark-mode-toggle');
            if (isDarkMode) {
                toggleBtn.innerHTML = '🌙';
            } else {
                toggleBtn.innerHTML = '☀️';
            }
            
            // Send to server to store in session
            fetch('/toggle_dark_mode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ dark_mode: isDarkMode })
            });
        }

        // Initialize dark mode if previously set
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
            document.querySelector('.dark-mode-toggle').innerHTML = '🌙';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    content = load_content()
    login_error = request.args.get('login_error', '')
    
    return render_template_string(HTML_TEMPLATE, 
                               PLATFORMS=PLATFORMS,
                               ACTIONS=ACTIONS,
                               content=content,
                               login_error=login_error)

@app.route('/content/<platform>/<action>')
def content_page(platform, action):
    content_data = load_content()
    
    if platform not in content_data:
        flash('Platform not found', 'error')
        return redirect(url_for('index'))
    
    if action not in content_data[platform]:
        flash('Action not found for this platform', 'error')
        return redirect(url_for('index'))
    
    action_display = action.replace('_', ' ').title()
    return render_template_string(CONTENT_PAGE_TEMPLATE,
                                platform=platform,
                                action=action_display,
                                content=content_data[platform][action])

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('admin_user')
    password = request.form.get('admin_pass')
    
    if not username or not password:
        return redirect(url_for('index', login_error='Username and password are required'))
    
    if username in ADMIN_USERS and ADMIN_USERS[username] == password:
        session['admin'] = True
        session['username'] = username
        return redirect(url_for('index'))
    
    return redirect(url_for('index', login_error='Invalid credentials'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    session.pop('username', None)
    session.pop('dark_mode', None)
    return redirect(url_for('index'))

@app.route('/toggle_dark_mode', methods=['POST'])
def toggle_dark_mode():
    if request.is_json:
        data = request.get_json()
        session['dark_mode'] = data.get('dark_mode', False)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/update_content', methods=['POST'])
def update_content():
    if 'admin' not in session:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    platform = request.form.get('platform')
    action_type = request.form.get('action_type')
    
    if not platform or not action_type:
        flash('Invalid request', 'error')
        return redirect(url_for('index'))
    
    content = load_content()
    
    if platform not in content or action_type not in content[platform]:
        flash('Invalid platform or action', 'error')
        return redirect(url_for('index'))
    
    # Update text content
    content[platform][action_type]['text'] = request.form.get('content_text', '')
    content[platform][action_type]['additional_content'] = request.form.get('additional_content', '')
    
    # Handle image uploads
    if 'image_files' in request.files:
        image_files = request.files.getlist('image_files')
        for image_file in image_files:
            if image_file.filename != '':
                if allowed_file(image_file.filename, 'image'):
                    try:
                        filename = secure_filename(f"{platform}_{action_type}_img_{datetime.now().timestamp()}_{image_file.filename}")
                        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        image_file.save(image_path)
                        content[platform][action_type]['images'].append(f"uploads/{filename}")
                    except Exception as e:
                        flash(f'Error saving image: {str(e)}', 'error')
                else:
                    flash('Invalid image file type', 'error')
    
    # Handle image URLs
    if 'image_urls' in request.form and request.form['image_urls'].strip():
        urls = [url.strip() for url in request.form['image_urls'].split(',') if url.strip()]
        content[platform][action_type]['images'].extend(urls)
    
    # Handle video uploads
    if 'video_files' in request.files:
        video_files = request.files.getlist('video_files')
        for video_file in video_files:
            if video_file.filename != '':
                if allowed_file(video_file.filename, 'video'):
                    try:
                        filename = secure_filename(f"{platform}_{action_type}_vid_{datetime.now().timestamp()}_{video_file.filename}")
                        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        video_file.save(video_path)
                        content[platform][action_type]['videos'].append(f"uploads/{filename}")
                    except Exception as e:
                        flash(f'Error saving video: {str(e)}', 'error')
                else:
                    flash('Invalid video file type', 'error')
    
    # Handle video URLs
    if 'video_urls' in request.form and request.form['video_urls'].strip():
        urls = [url.strip() for url in request.form['video_urls'].split(',') if url.strip()]
        content[platform][action_type]['videos'].extend(urls)
    
    save_content(content)
    flash('Content updated successfully', 'success')
    return redirect(url_for('index', _anchor='admin'))

@app.route('/remove_media', methods=['POST'])
def remove_media():
    if 'admin' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    platform = data.get('platform')
    action = data.get('action')
    media_type = data.get('media_type')
    index = data.get('index')
    
    if not platform or not action or media_type not in ['image', 'video'] or index is None:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    
    content = load_content()
    
    if platform not in content or action not in content[platform]:
        return jsonify({'success': False, 'error': 'Content not found'}), 404
    
    media_key = f"{media_type}s"
    if 0 <= index < len(content[platform][action][media_key]):
        # Remove the media file if it exists locally
        media_path = content[platform][action][media_key][index]
        if media_path and not media_path.startswith('http'):
            try:
                file_path = os.path.join('static', media_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error removing file: {e}")
        
        # Remove the media reference
        content[platform][action][media_key].pop(index)
        save_content(content)
    
    return jsonify({'success': True})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)