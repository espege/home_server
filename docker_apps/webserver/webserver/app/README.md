# Song Search App

This project is a Flask web application designed for searching and displaying songs along with their metadata. It supports multiple scores, interpreters, composers, and external media links.

## Project Structure

```
song-search-app
├── app
│   ├── __init__.py          # Initializes the Flask application and configures necessary extensions.
│   ├── main.py              # Entry point of the application, creates an instance of the Flask app and configures main routes.
│   ├── models
│   │   ├── __init__.py      # Initializes the models module.
│   │   └── song.py          # Defines the Song class representing a music piece with properties and methods for metadata management.
│   ├── routes
│   │   ├── __init__.py      # Initializes the routes module.
│   │   └── search.py        # Defines routes for song searching, handling search requests and returning results.
│   ├── templates
│   │   ├── base.html        # Base template for other pages, includes common HTML tags and links to CSS and JavaScript files.
│   │   ├── index.html       # Homepage of the application, contains a search form and displays search results.
│   │   └── song_detail.html  # Displays details of a selected song, including scores, interpreters, composers, and external media links.
│   └── static
│       ├── css
│       │   └── style.css     # CSS styles for the application, defining the appearance of the pages.
│       └── js
│           └── search.js     # JavaScript code for handling interactions on the search page, such as AJAX requests for results.
├── config.py                # Configuration file for the application, including database settings and other environment-specific configurations.
├── requirements.txt         # Lists the dependencies required for the project, including Flask and other libraries.
├── .gitignore               # Specifies files and directories to be ignored by Git when tracking changes.
└── README.md                # Documentation for the project, including setup and execution instructions.
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd song-search-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application settings in `config.py` as needed.

## Running the Application

### Dev

Debug mode:
```
flask --app run.py --debug run
```

To run the application, execute the following command:
```
python run.py
```

### Prod
gunicorn --bind 127.0.0.1:5000 "run:create_gunicorn_app()"

The application will be accessible at `http://127.0.0.1:5000`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
