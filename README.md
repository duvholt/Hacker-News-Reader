# Hacker News Reader
- - -
*Unofficial UI for news.ycombinator.com*

This project was started out of frustration from lack of proper mobile layout and other minor annoyances.
The main goal of the project is to give a more user friendly interface that should work on every platform. Mobile support is especially important. 

**Current features:** 
* Frontpage submissions and some simple sorting/filtering of those (new, top, Ask HN, etc.)
* Full support for comments viewing including polls and Ask HN posts. 
* Can act as an API a la reddit (append .json to any page to get json)
* Responsive layout thanks to Bootstrap (with some tweaking)
* Some comment enhancements like original posters name in a different color and comment collapsing. More planned. 

Written in Python 2.7 and uses the following:
* Django
* Bootstrap as a CSS framework
* BeautifulSoup for parsing HTML
* Sass/Compass for CSS
* jQuery
* PostgreSQL
* Various timezone/time packages
* Check [requirements.txt]( Hacker-News-Reader/blob/master/requirements.txt) for a full list of Python packages

Currently the project scrapes news.ycombinator.com directly which leads to some problems:
* One major problem is being unable to scrape older comments too often
    * The “official” api HNSearch doesn’t allow fetching by id rendering it completely useless for my use and most of the other unofficial apis have some problems with the formatting. 
* Semi-random banning of the scrape IP.
    * Normally I would just scrape with different IP addresses, but currently the project is hosted on AppFog free tier which only gives me one IP. I have a working port for Google App Engine, but for some reason it is unable to scrape HN at all. 

Hosted on http://hn.cxhristian.com 
