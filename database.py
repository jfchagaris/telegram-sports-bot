import sqlite3
def initalize_db():
    con = sqlite3.connect("shared_links.db")
    cur = con.cursor()
    cur.execute('''
            CREATE TABLE IF NOT EXISTS group_links(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            user TEXT,
            timestamp TEXT
            )
    ''')
    cur.execute('''
            CREATE TABLE IF NOT EXISTS private_links(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            user TEXT,
            timestamp TEXT
            )
    ''')
    con.commit
    con.close

def insert_group_link(title, url, user, timestamp):
    con = sqlite3.connect("shared_links.db")
    cur = con.cursor()
    sql = "SELECT * FROM group_links WHERE URL = ?"
    params = (url,)
    dupe_check = cur.execute(sql, params).fetchone()
    if dupe_check is not None:
        con.close()
        return
    sql = "INSERT INTO group_links (title, url, user, timestamp) VALUES (?, ?, ?, ?)"
    params = (title, url, user, timestamp)
    cur.execute(sql, params)
    con.commit()
    con.close()

def insert_private_link(title, url, user, timestamp):
    con = sqlite3.connect("shared_links.db")
    cur = con.cursor()
    sql = "SELECT * FROM private_links WHERE url = ?"
    params = (url,)
    dupe_check = cur.execute(sql, params).fetchone()
    if dupe_check is not None:
        con.close()
        return
    sql = "INSERT INTO private_links (title, url, user, timestamp) VALUES (?, ?, ?, ?)"
    params = (title, url, user, timestamp)
    cur.execute(sql, params)
    con.commit()
    con.close()

def query_shared_links(user=None, random=False, limit=None, table_name="group_links"):
    con = sqlite3.connect("shared_links.db")
    cur = con.cursor()
    if user == None:
        sql = f"SELECT * FROM {table_name}"
        params = ()
    else:
        sql = f"SELECT * FROM {table_name} WHERE user = ?"
        params = (user,)
    if random == True:
        sql += " ORDER BY RANDOM() LIMIT 1"
    else:
        sql += " ORDER BY timestamp DESC"
    query = cur.execute(sql, params)
    query = query.fetchall()
    print(type(query))
    #print(query)
    return query


# if __name__ == "__main__":
#     query_shared_links(user='bum')
# insert_link(
#     title="test",
#     url="https://example.com",
#     user="sampleUser",
#     timestamp="2025-11-15 10:30:00",
# )
print("insert complted")

