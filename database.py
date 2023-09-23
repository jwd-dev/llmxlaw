import sqlite3

conn = sqlite3.connect(':memory:')
c = conn.cursor()

c.execute("""
  CREATE TABLE "public"."Events" (
    "eventName" text,
    "description" text,
    "datetime" text
  )
""")


def add_event(eventName, description, datetime):
  c.execute("INSERT INTO 'public'.'Events' ('eventName', 'description', 'datetime') VALUES (?, ?, ?)",
            (eventName, description, datetime))
  conn.commit()

def query_events():
  c.execute("SELECT * FROM 'public'.'Events'")
  return c.fetchall()

