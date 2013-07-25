import praw
import sqlite3
import datetime

class Updater:
    user_agent = "SWOTD Updater Bot (/u/sirloinsirloin2)"
    username = "swotd_bot"
    password = "fakepass"
    subreddit = "SexyWomanOfTheDay"
    dbfile = "swotd.db"
    r = None  # Connection to reddit
    s = None  # SWOTD subreddit object
    conn = None  # Database connection

    def reddit_connect(self):
        """Initialize the reddit connection and subreddit object"""
        self.r = praw.Reddit(user_agent=self.user_agent)
        self.r.login(self.username, self.password)
        self.s = self.r.get_subreddit(subreddit)

    def current_submissions(self):
        """Lists five most recent posts to subreddit"""
        if self.r is None:
            self.reddit_connect()
        submissions = self.s.get_new(limit=5)
        for i in submissions:
            print str(i)
            print "    id:    ", i.id
            print "    name:  ", i.author.name
            print "    flair: ", i.link_flair_text

    def db_connect(self):
        """Connects to the database"""
        self.conn = sqlite3.connect(self.dbfile)
        self.conn.row_factory = sqlite3.Row

    def current_woman(self):
        """Returns the record of the current days' woman"""
        if(self.conn is None):
            self.db_connect()
        c = self.conn.cursor()
        c.execute("SELECT * FROM women " + \
                  "WHERE `date`=date('now', 'localtime')")
        try:
            return c.fetchone()
        except TypeError:
            return None 

    def add_flair_template(self):
        """Adds today's link flair to the subreddit"""
        x = self.flair_text()
        self.s.add_flair_template(x['text'], x['date'], is_link=True)

    def flair_text(self):
        """Calculates today's flair text"""
        if(self.r is None):
            self.reddit_connect()
        w = self.current_woman()
        text = w['name'].encode('ascii', 'xmlcharrefreplace')
        date = w['date'].encode('ascii')
        return {'text': text, 'date':date}


    def update_css(self):
        """Update the stylesheet to distinguish today's flair"""
        if(self.r is None):
            self.reddit_connect()
        text = open('sidebar.txt', 'r').read()
        date = datetime.datetime.now().date().isoformat()
        css = text % date
        self.s.set_stylesheet(css)
        

    def update_sidebar(self):
        """Sets the sidebar for today's content"""
        if(self.conn is None):
            self.db_connect()
        c = self.conn.cursor()
        c.execute("SELECT * FROM women " + \
            "WHERE `date` > date('now', 'localtime', '-5 days') " +\
            "AND `date` < date('now', 'localtime') ORDER BY DATE")
        old = c.fetchall()
        c.execute("SELECT * FROM women " + \
            "WHERE `date` = date('now', 'localtime')")
        curr = c.fetchone()
        c.execute("SELECT * FROM women " + \
            "WHERE `date` > date('now', 'localtime') " + \
            "AND `date` < date('now', 'localtime', '+5 days') ORDER BY DATE")
        upcoming = c.fetchall()

        text = open('sidebar.txt', 'r').read()

        table="\n\n|Date|Person|\n|:-|:-|\n"
        for v in old:
            table += "| ~~%s~~ | ~~%s~~ |\n" % (v['date'], v['name'])
        table += "| **%s** | **%s** |\n" % (curr['date'], curr['name'])
        for v in upcoming:
            table += "| *%s* | *%s* |\n" % (v['date'], v['name'])
        text += table
        settings = {'description' : unicode(text)}
        
        if self.r is None:
            self.reddit_connect()
        print self.s.update_settings(**settings)

    def makepost(self):
        """Makes the next post in the 'post' database"""
        curr = self.current_woman()['id']
        c = self.conn.cursor()
        c.execute("SELECT * FROM posts WHERE womanid=%d AND posted=0 ORDER BY distinguished DESC" % curr)

        a = c.fetchone()
        if a is None:
            return

        if self.r is None:
            self.reddit_connect()
        submission = self.s.submit(title=a['title'], url=a['link'])
        submission.approve()
        x = self.flair_text()
        self.s.set_flair(submission, x['text'], x['date'])
        if a['distinguished']:
            submission.distinguish()

        sql = "UPDATE posts SET posted=1 WHERE postid=%d" % a['postid']
        c.execute(sql)
        self.conn.commit()
