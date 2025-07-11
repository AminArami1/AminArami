<?php
session_start();

// --- File paths ---
$visit_file = "visits.json";
$user_file = "users.json";
$content_file = "content.json";
$upload_dir = "uploads/";

// Create upload directory if it doesn't exist
if (!file_exists($upload_dir)) {
  mkdir($upload_dir, 0755, true);
}

// --- Log visits and IP ---
function get_ip() {
  if (!empty($_SERVER['HTTP_CLIENT_IP'])) return $_SERVER['HTTP_CLIENT_IP'];
  if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) return $_SERVER['HTTP_X_FORWARDED_FOR'];
  return $_SERVER['REMOTE_ADDR'] ?? 'UNKNOWN';
}
function log_visit() {
  global $visit_file, $user_file;
  $ip = get_ip();
  $time = date("Y-m-d H:i:s");

  // Log total visits
  $visits = file_exists($visit_file) ? json_decode(file_get_contents($visit_file), true) : ['count'=>0];
  $visits['count'] = ($visits['count'] ?? 0) + 1;
  file_put_contents($visit_file, json_encode($visits, JSON_PRETTY_PRINT));

  // Log users
  $users = file_exists($user_file) ? json_decode(file_get_contents($user_file), true) : [];
  $users[] = ['ip'=>$ip, 'time'=>$time];
  file_put_contents($user_file, json_encode($users, JSON_PRETTY_PRINT));
}
log_visit();

// --- Topics and actions ---
$topics = [
  'Video Platforms' => ['YouTube', 'TikTok', 'Instagram', 'Snapchat', 'Likee', 'Twitch'],
  'Messaging Apps' => ['Telegram', 'WhatsApp', 'Signal', 'Messenger'],
  'Social Platforms' => ['TwitterX', 'Threads', 'Reddit', 'Pinterest'],
  'Professional' => ['LinkedIn'],
  'Design & Art' => ['Behance', 'DeviantArt'],
  'Music' => ['Spotify', 'SoundCloud']
];
$actions = ['Create Account', 'Delete Account', 'Increase Followers', 'Prevent Hacking'];

// --- Load content ---
$content = file_exists($content_file) ? json_decode(file_get_contents($content_file), true) : [];

foreach ($topics as $cat => $apps) {
  foreach ($apps as $app) {
    if (!isset($content[$app])) {
      $content[$app] = [
        'text' => '',
        'image' => '',
        'video' => '',
        'accounts' => [],
      ];
    }
  }
}

// --- Read visit count ---
$visit_count = file_exists($visit_file) ? json_decode(file_get_contents($visit_file), true)['count'] : 0;
?>
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Master Account - Account Management Guides</title>
  <meta name="description" content="Learn to create, manage and secure accounts on popular platforms like YouTube, Telegram, Instagram and more." />
  <meta name="keywords" content="create account, delete account, security, prevent hacking, YouTube, Instagram, Telegram, account management" />
  <meta name="author" content="Master Account Team" />
  <link rel="icon" href="favicon.ico" type="image/x-icon" />
  <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: linear-gradient(to right, #e0f7fa, #fff);
      color: #333;
      transition: background 0.3s, color 0.3s;
      direction: ltr;
    }
    body.dark { background: #121212; color: #eee; }
    header, footer {
      background: #00695c;
      color: white;
      text-align: center;
      padding: 1em;
    }
    nav {
      background: #004d40;
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 15px;
      padding: 1em;
    }
    nav a {
      color: white;
      text-decoration: none;
      padding: 8px 15px;
      background: #00796b;
      border-radius: 5px;
    }
    nav a:hover { background: #004d40; }
    .container { max-width: 1000px; margin: auto; padding: 1em; }
    .section {
      background: white;
      padding: 1em;
      margin-bottom: 1em;
      border-radius: 12px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    body.dark .section { background: #1e1e1e; }
    h2 { color: #00796b; }
    a.link { display: block; margin: 5px 0; color: #00796b; text-decoration: none; }
    .dark-toggle {
      margin-top: 1em;
      background: #00796b;
      color: white;
      border: none;
      padding: 10px;
      border-radius: 8px;
      cursor: pointer;
    }
    .app-box { margin-top: 10px; margin-left: 15px; }
    .app-box a { font-size: 14px; margin-left: 10px; }
    #searchInput {
      width: 100%;
      padding: 10px;
      border-radius: 8px;
      margin-bottom: 20px;
    }
    .search-results {
      margin-top: 20px;
      padding: 15px;
      background: #f0f0f0;
      border-radius: 8px;
    }
    .search-highlight {
      background-color: yellow;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <header>
    <h1>Master Account Guides 🌐</h1>
    <p>Learn how to manage accounts on your favorite platforms!</p>
    <button class="dark-toggle" onclick="toggleDarkMode()">Toggle Dark Mode</button>
  </header>

  <nav>
    <a href="#home">Home</a>
    <a href="#about">About</a>
    <a href="#services">Services</a>
    <a href="#search">Search</a>
    <a href="#settings">Settings</a>
  </nav>

  <div class="container">
    <section class="section" id="home">
      <h2>Get Started</h2>
      <p>Step-by-step guides for all major platforms:</p>
      <div id="appList">
      <?php
      foreach ($topics as $category => $apps) {
        echo "<div class='section topic'><h3>$category</h3>";
        foreach ($apps as $app) {
          echo "<div class='app-item'><strong>📘 $app</strong><div class='app-box'>";
          foreach ($actions as $action) {
            echo "<a class='link' href='#'>$action on $app</a>";
          }
          echo "</div></div>";
        }
        echo "</div>";
      }
      ?>
      </div>
    </section>

    <section class="section" id="about">
      <h2>About Master Account</h2>
      <p>We provide comprehensive guides for account management on various platforms to help users safely navigate digital services.</p>
    </section>

    <section class="section" id="services">
      <h2>Our Services</h2>
      <ul>
        <li>Step-by-step account creation guides</li>
        <li>Account deletion instructions</li>
        <li>Security and privacy recommendations</li>
        <li>Platform-specific tips and tricks</li>
      </ul>
    </section>

    <section class="section" id="search">
      <h2>Search Guides</h2>
      <input type="text" id="searchInput" placeholder="Search platform or topic..." autocomplete="off">
      <div id="searchResults" class="search-results" style="display:none;"></div>
    </section>

    <section class="section" id="settings">
      <h2>Site Settings</h2>
      <p>Customize your experience with dark mode and other preferences.</p>
    </section>
  </div>

  <footer>
    &copy; <?php echo date("Y"); ?> Master Account. All rights reserved.
  </footer>

  <script>
    function toggleDarkMode() {
      document.body.classList.toggle('dark');
      localStorage.setItem('darkMode', document.body.classList.contains('dark'));
    }

    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
      document.body.classList.add('dark');
    }

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const allContent = <?= json_encode($content) ?>;
    const allTopics = <?= json_encode($topics) ?>;
    const allActions = <?= json_encode($actions) ?>;

    searchInput.addEventListener('input', function() {
      const keyword = this.value.trim().toLowerCase();
      searchResults.innerHTML = '';
      
      if (keyword.length < 2) {
        searchResults.style.display = 'none';
        return;
      }
      
      let resultsFound = false;
      
      // Search in apps
      for (const [category, apps] of Object.entries(allTopics)) {
        for (const app of apps) {
          if (app.toLowerCase().includes(keyword)) {
            addSearchResult(category, app, 'App');
            resultsFound = true;
          }
        }
      }
      
      // Search in actions
      for (const action of allActions) {
        if (action.toLowerCase().includes(keyword)) {
          addSearchResult('Actions', action, 'Action matches');
          resultsFound = true;
        }
      }
      
      if (resultsFound) {
        searchResults.style.display = 'block';
        highlightSearchResults(keyword);
      } else {
        searchResults.innerHTML = '<p>No results found</p>';
        searchResults.style.display = 'block';
      }
    });
    
    function addSearchResult(category, title, description) {
      const resultItem = document.createElement('div');
      resultItem.className = 'search-result-item';
      resultItem.innerHTML = `
        <h4>${title}</h4>
        <p><em>${category}</em> - ${description}</p>
      `;
      searchResults.appendChild(resultItem);
    }
    
    function highlightSearchResults(keyword) {
      const regex = new RegExp(keyword, 'gi');
      const resultItems = searchResults.querySelectorAll('.search-result-item');
      
      resultItems.forEach(item => {
        item.innerHTML = item.innerHTML.replace(regex, match => 
          `<span class="search-highlight">${match}</span>`
        );
      });
    }
    
    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
      if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.style.display = 'none';
      }
    });
  </script>
</body>
</html>
