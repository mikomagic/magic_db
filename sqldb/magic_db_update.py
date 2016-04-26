#!/usr/bin/python


import argparse
import sqlite3


def create_tables(conn):
    try:
        with conn:
            conn.execute('''CREATE TABLE Sets (
                id text PRIMARY KEY,
                name text )''')
            conn.execute('''CREATE TABLE Cards (
                multiverseid int PRIMARY KEY,
                name text,
                language text,
                set_id REFERENCES Sets ( id ),
                card_number int )''')
    except sqlite3.OperationalError:
        pass


def set_has_cards(conn, set_id):
    cur = conn.execute('''SELECT * FROM Cards WHERE set_id = ?''', (set_id,))
    return cur.fetchone() is not None


def set_get_name(conn, set_id):
    cur = conn.execute('''SELECT name FROM Sets WHERE id = ?''', (set_id,))
    row = cur.fetchone()
    return row[0] if row else None


def remove_empty_set(conn, set_id, set_name):
    name_in_db = set_get_name(conn, set_id)
    if name_in_db is None:
        print "Set %s not found" % set_id
        return False
    elif set_name is not None and set_name != name_in_db:
        print "Name mismatch: set %s is called '%s' in DB" % (set_id, name_in_db)
        return False
    if set_has_cards(conn, set_id):
        print "Set %s is not empty" % set_id
        return False
    cur = conn.execute('''DELETE FROM Sets WHERE id = ?''', (set_id,))
    assert cur.rowcount == 1
    print "Deleted empty set %s" % set_id
    conn.commit()
    return True


def add_or_update_set(conn, set_id, set_name):
    name_in_db = set_get_name(conn, set_id)
    if name_in_db is not None:
        print "Found set %s with name '%s'" % (set_id, name_in_db)
        if set_name is not None and set_name != name_in_db:
            conn.execute('''UPDATE Sets SET name = ? WHERE id = ?''', (set_name, set_id))
            print "Updated set name to '%s'" % set_name
    else:
        if set_name is None:
            print "You need to provide a name for set %s" % set_id
            return False
        else:
            conn.execute('''INSERT INTO Sets VALUES (?, ?)''', (set_id, set_name))
            print "Added set %s with name '%s'" % (set_id, set_name)
    conn.commit()
    return True
    

def parse_args():
    parser = argparse.ArgumentParser(description='Create, update, or expand Magic DB.')
    parser.add_argument('--db', dest='db', default='magic.db', help='the DB file (SQLite)')
    parser.add_argument('--lang', dest='lang', default='en', help='language to add or update')
    parser.add_argument('--rm', dest='rm', action='store_true', help='delete empty Magic set')
    parser.add_argument('set_id', help='Short ID of Magic set to add or update (e.g., "ORI")')
    parser.add_argument('set_name', nargs='?', help='Full name of Magic set to add or update (e.g., "Magic Origins")')
    return parser.parse_args()
    

def main():
    args = parse_args()
    conn = sqlite3.connect(args.db)
    create_tables(conn)
    if args.rm:
        remove_empty_set(conn, args.set_id, args.set_name)
    else:
        add_or_update_set(conn, args.set_id, args.set_name)
    conn.close()


if __name__ == "__main__":
    main()
