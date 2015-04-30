# League-Analyzer
Database assignment for school, written in Python CGI

## Setup
1. The directory this web application is stored in **must** be called `analyzer`.
2. Place the `analyzer` folder into your CGI server folder.
3. Open `/framework/templates.py` with a text editor.
4. Change `webRootPath = "http://localhost/analyzer"` near the top of the file to the root URL of the website pointing to the analyzer folder, without a trailing forward slash. For example:<br>`webRootPath = "http://tartarus.ccgs.wa.edu.au/~1018017/analyzer"`.
5. Navigate your browser to the `/analyzer` page, which should load the index.html and redirect you to the appropriate landing page.

## File locations
- scraper
    + Contains the programs used to scrape data from the League of Legends servers, and also the automated insert and create statements.
    + Insert and create statements can be found in the `/scraper/createdb.py` file.
    + Even more insert statements can be found in the `/scraper/scrape.py` file, which scrapes the match data from the League of Legends servers periodically into the database.
- models
    + Contains the database package, which contains all of the database read queries used in the web application.
- controllers
    + Contains the controllers for the views.
    + A database insert query is stored in `/controllers/admin/add-match.py`.
- static
    + Contains static files such as CSS, JS and fonts.
- views
    + Contains views (templates) for pages on the site.
- components
    + Contains components for the views (only the navbar).
- framework
    + Contains the files for the framework which adds handy functions to perform repetitive operations, or core operations a web framework would usually do that I can't live without.
