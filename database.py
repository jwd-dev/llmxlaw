import sqlite3

conn = sqlite3.connect(':memory:')
c = conn.cursor()

class Database:
  def __init__(self) -> None:
    c.execute("""
      CREATE TABLE "Events" (
        "eventName" text,
        "description" text,
        "start_time" datetime,
        "end_time" datetime,
        "referencedDocuments" text
      )
    """)


  def add_event(self, eventName, description, datetime, referenced_documents=""):
    c.execute("INSERT INTO 'Events' ('eventName', 'description', 'start_time', 'end_time', 'referencedDocuments') VALUES (?, ?, ?, ?, ?)",
              (eventName, description, datetime, referenced_documents))
    conn.commit()

  def query_events(self):
    c.execute("SELECT * FROM 'Events' ORDER BY 'start_time' ASC")
    return c.fetchall()
  


# add_event("Imposition of Sentence on Paras Jha", "The court hearing for the imposition of sentence on Paras Jha took place", "09-18-2018 09-18-2018")
# print(query_events())