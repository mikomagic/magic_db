from common.logger import Log


class CardDAO(object):
    @staticmethod
    def create_table(conn):
        conn.execute('''CREATE TABLE Cards (
            multiverseid int PRIMARY KEY,
            name text,
            language text,
            set_id REFERENCES Sets ( id ),
            card_number int )''')
        Log.info("Created table Cards")

    def __init__(self, card, set_id, conn):
        self.card = card
        self.set_id
        self.conn = conn

    def __get_tuple(self):
        return (self.card.multiverseid,
                self.card.name,
                self.card.language,
                self.set_id,
                self.card.number)

    def __find_by_multiverseid(self):
        return self.conn.execute('''SELECT * FROM Sets WHERE multiverseid = ?''', (self.card.id,)).fetchone()

    def __insert(self):
        self.conn.execute('''INSERT INTO Sets VALUES (?, ?, ?, ?, ?)''', self.__get_tuple())
        self.conn.commit()
        Log.info("Added %s" % self.card)
        return True

    def __update(self):
        row = self.__find_by_multiverseid()
        self.conn.execute('''UPDATE Cards SET
                               name = ?,
                               language = ?,
                               set_id = ?,
                               card_number = ?
                             WHERE multiverseid = ?''',
                          self.__get_tuple()[1:] +
                          (self.card.multiverseid,))
        self.conn.commit()
        Log.info("Updated %s" % self)
        return True

    def save(self):
        row = self.__find_by_id()
        if not row:
            return self.__insert()
        else:
            return self.__update()

    def delete(self):
        if not self.__find_by_multiverseid():
            Log.error('%s not found in DB' % self)
            return False
        cur = self.conn.execute('''DELETE FROM Cards WHERE id = ?''', (self.card.multiverseid,))
        assert cur.rowcount == 1
        self.conn.commit()
        Log.info("Deleted %s" % self)
        return True
