# Hacker News Reader
- - -
*Unofficial UI for news.ycombinator.com*

This project was started out of frustration from lack of proper mobile layout and other minor annoyances.
The main goal of the project is to give a more user friendly interface that should work on every platform. Mobile support is especially important. 
Currently it works fairly well with all sorts of discussion that I know about including polls, ask hn questions and permalinks. Adding user pages is planned. 

Currently the project scrapes news.ycombinator.com directly which leads to some problems:
* One major problem is being unable to scrape older comments too often and semi-random banning of the scrape IP.
* The “official” api HNSearch doesn’t allow fetching by id rendering it completely useless for my use and most of the other unofficial apis have some problems with the formatting. 
* Normally I would just scrape with different ip addresses, but currently the project is hosted on AppFog free tier which only gives me one ip. I have a working port to Google App Engine, but for some reason it is unable to scrape HN at all. 

The plan is to let the site act as an api too. Most pages can be read shown as json by appending .json to the URL like reddit.com does. This is mainly to support a planned Android app. 

**Hosted on http://hn.cxhristian.com**
