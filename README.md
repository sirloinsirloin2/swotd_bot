swotd\_bot
=========

Bot used on /r/SexyWomanOfTheDay

Introduction
------------

The purpose of this bot is to make daily changes to
reddit.com/r/SexyWomanOfTheDay via Reddit's API.  This is done via a Python
class, Updater.py, which is based on [Praw](https://github.com/praw-dev/praw).
Along side the class, there are several scripts for either user interaction or
automation.  Data is stored in an Sqlite3 database.

Setup
-----

Fetch the current version however you wish.  There is no installation required
beyond this point, but one must create the tables and configure Updater.py.

1. Run "sqlite3 swotd.db < database\_schemata.txt" to create the database.
2. Edit the variables "username" and "password" with your bot's Reddit account
information.  Edit "subreddit" to reflect which subreddit the bot is supposed
to manage.  (Remember that the user account from the previous line has to be a
mod of the subreddit!)

That should be all that is required to get it running, modulo configuring your
system to execute some scripts periodically.  (I have cron jobs to run "daily"
every day at 3am, as well as run "post" every thirty minutes thereafter.)

User scripts
------------

There are several scripts for manipulating the database and managing the
subreddit.  You can run these after the database is configured.

`addgirl` inserts a girl into the database.  She is not scheduled.  Simply say
something like

    ./addgirl Alison Brie

`addtheme` does the same, but for a theme, like

    ./addtheme Community

Themes are managed as girls, but are differentiated in the database.

`search` lets you search for girls.  No wildcards are supported, but you can use a partial string, ignoring case  For example, `./search na` would return Natalie Portman and Adriana Lima.

`schedule` takes a girl's id and schedules her for a future available date.  It does not detect "holes" in the schedule, but you can use `schedule-date` to fill the hole manually.

`makepost` prepares a post for a girl.  The girl does not have to be scheduled
yet.  You use it like

    makepost 293 'Wowza, look at that!' 'http://i.imgur.com/alSlD.jpg'

`makedistinguishedpost` works similarly, but the post is mod-distinguished when it is made.


`random` simply prints a list of ten random girls -- for when you're having trouble deciding whom to schedule next. :) 

`showposts` shows *scheduled* posts; `showposts-girl` shows the posts for the girl whose id you supply.

Automation scripts
------------------

The scripts `daily`, `post`, and `update-sidebar` are intended to be run by a
cron job, but could be run yourself if you like.  `post` submits the next
eligible post to your subreddit.  `update-sidebar` does what you think it does;
see the corresponding function in `Updater.py` to see its behavior.  `daily`
updates the subreddit's flair, css, and sidebar in one go.

Here is the crontab that I use for automated moderation.

    # m h  dom mon dow   command
    
    # min | hour | date | month| day  | cmd...
    0       3      *      *      *      cd ~sirloinsirloin2/swotd; ./daily
    */30    3-23   *      *      *      cd ~sirloinsirloin2/swotd; ./post

