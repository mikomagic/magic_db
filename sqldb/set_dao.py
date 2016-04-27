from common.logger import Log

class SetDAO(object):
    @staticmethod
    def create_table(conn):
        conn.execute('''CREATE TABLE Sets (
            id text PRIMARY KEY,
            name text )''')

    def __init__(self, set_id, set_name, conn):
        self.id = set_id
        self.name = set_name
        self.tuple = (self.id, self.name)
        self.conn = conn

    def __find_by_id(self):
        return self.conn.execute('''SELECT * FROM Sets WHERE id = ?''', (self.id,)).fetchone()

    def __find_by_id_and_name(self):
        return self.conn.execute('''SELECT * FROM Sets WHERE id = ? AND name = ?''', (self.tuple)).fetchone()

    def insert(self):
        if not self.name:
            Log.error("Name required when adding set.")
            return False
        self.conn.execute('''INSERT INTO Sets VALUES (?, ?)''', (self.tuple))
        self.conn.commit()
        Log.info("Added %s" % self)
        return True

    def update(self):
        if not self.name:
            return False # nothing to do
        row = self.__find_by_id()
        if row[1] != self.name:
            self.conn.execute('''UPDATE Sets SET name = ? WHERE id = ?''', (self.name, self.id))
            self.conn.commit()
            Log.info("Updated %s" % self)
            return True
        return False

    def insert_or_update(self):
        row = self.__find_by_id()
        if not row:
            return self.insert()
        else:
            return self.update()

    def delete(self):
        if self.name:
            if not self.__find_by_id_and_name():
                Log.error('%s not found in DB' % self)
                return False
        else:
            if not self.__find_by_id():
                Log.error('%s not found in DB' % self)
                return False
        cur = self.conn.execute('''DELETE FROM Sets WHERE id = ?''', (self.id,))
        assert cur.rowcount == 1
        self.conn.commit()
        Log.info("Deleted %s" % self)
        return True

    def __str__(self):
        if self.name:
            return "set %s (%s)" % (self.tuple)
        else:
            return "set %s" % (self.id)

