import sqlite3
import os
import datetime
from django import db
from django.core.management import BaseCommand


#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#DATABASE = os.path.join(BASE_DIR, "data.sqlite3")
DATABASE = db.connections.databases['default']['NAME']

def recreate_database():
    print("Deleting database...")
    try:
        os.remove("data.sqlite3")
    except FileNotFoundError:
        pass
    print("Creating database...")
    connection = sqlite3.connect(DATABASE)
    sql_command = """
        CREATE TABLE posts (
        id INTEGER PRIMARY KEY,
        title TEXT,
        text TEXT,
        timestamp timestamp);
    """
    cursor = connection.cursor()
    cursor.execute(sql_command)
    connection.commit()
    connection.close()


def generate_fake():
    print("Generating fake data...")
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    posts = [
        ("Hello, World!", "This is a post for testing", datetime.datetime.now()),
        ("你好，世界！", "这是一个测试帖子", datetime.datetime.utcnow()),
    ]
    for post in posts:
        sql = "INSERT INTO posts(title, text, timestamp) values (?, ?, ?)"
        cur.execute(sql, (post[0], post[1], post[2]))
    conn.commit()
    conn.close()

def init_database():
    recreate_database()
    generate_fake()


class Command(BaseCommand):
    def handle(self, *args, **options):
        init_database()

if __name__ == '__main__':
    print("Please use \"init_database\" command with manage.py")



