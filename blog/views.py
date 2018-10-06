from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
import sqlite3
from datetime import datetime
from dateutil import tz
from typing import List
import pytz

cursor = None


class Post:
    def __init__(self, id, title: str, text: str, timestamp: str):
        self.id = id
        self.title = title
        self.text = text
        self.timestamp = timestamp
    def __repr__(self):
        return "<Post: %r>" % self.id

    @property
    def abstract(self):
        return self.text[:120]

    @property
    def text_lines(self):
        return self.text.split("\n")

    @property
    def local_time(self):
        utc = datetime.strptime(self.timestamp, "%Y-%m-%d %H:%M:%S.%f")
        utc = utc.replace(tzinfo=tz.tzutc())
        localtz = pytz.timezone("Asia/Shanghai")
        local = utc.astimezone(localtz)
        return local.strftime("%Y-%m-%d %H:%M")


def db(func):
    def wrapper(*args, **kwargs):
        global cursor
        conn = sqlite3.connect("data.sqlite3")
        cursor = conn.cursor()
        ret = func(*args, **kwargs)
        try:
            conn.commit()
        except Exception as e:
            print(e)
            print("Failed reading/writing database!")
        conn.close()
        return ret
    return wrapper

def get_post(id: int) -> Post:
    result = cursor.execute("SELECT * FROM posts where id=?", (id,))
    return Post(*result.fetchone())

def get_posts(offset: int=0, limit: int=10) -> List[Post]:
    sql = "SELECT * FROM posts ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    cursor.execute(sql, (limit, offset))
    res = [Post(*row) for row in cursor.fetchall()]
    return res

def create_post(title: str, text: str) -> Post:
    if not title:
        raise Exception("title must not be empty")
    if not text:
        raise Exception("text must not be emtpy")
    sql = "INSERT INTO posts(title, text, timestamp) values (?, ?, ?)"
    cursor.execute(sql, (title, text, datetime.utcnow()))
    row = cursor.execute("SELECT * from posts where id=last_insert_rowid()").fetchone()
    return Post(*row)

def modify_post(id: int, title: str, text: str) -> Post:
    if not id:
        raise Exception("id must not by empty")
    if not title:
        raise Exception("title must not be emtpy")
    if not text:
        raise Exception("text must not be empty")
    sql = "UPDATE posts SET title=?, text=? WHERE id=?"
    cursor.execute(sql, (title, text, id))
    row = cursor.execute("SELECT * from posts where id=?", (id,)).fetchone()
    return Post(*row)

def delete_post(id: int):
    sql = "DELETE FROM posts where id=?"
    cursor.execute(sql, (id,))

@db
def post_delete(request, id: int):
    delete_post(id)
    return redirect(index)

@db
def post_view(request, id: int):
    post = get_post(id)
    template = loader.get_template("blog/post.html")
    context = {
        "post": post,
    }
    return HttpResponse(template.render(context, request))

@db
def post_edit(request, id: int=None):
    post = None
    if request.method == 'POST':
        print(request.POST)
        title = request.POST.get('title', '')
        text = request.POST.get('text', '')
        if id != None: # update row
            post = modify_post(id, title, text)
        else: # create row
            post = create_post(title, text)
            id = post.id
        return redirect(post_view, id=id)
    # edit post
    post = get_post(id) if id else None
    template = loader.get_template("blog/post_edit.html")
    context = {
        "post": post,
    }
    return HttpResponse(template.render(context, request))


@db
def index(request):
    template = loader.get_template("blog/index.html")
    context = {
        "post_list": get_posts(),
    }
    return HttpResponse(template.render(context, request))
