from common.logger import Log
from dao import DAO, TableDesc

card_td = TableDesc("Cards", "multiverseid",
                    ["multiverseid",
                     "name",
                     "language",
                     "set_id",
                     "card_number"])

class CardDAO(DAO):
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
        super(CardDAO, self).__init__(card_td, conn)
        self.card = card
        self.set_id = set_id

    def get_pkey(self):
        return self.card.multiverseid

    def get_values(self):
        return [self.card.multiverseid,
                self.card.name,
                self.card.language,
                self.set_id,
                self.card.number]

    def delete(self):
        if not self.find_by_pkey():
            Log.error('%s not found in DB' % self)
            return False
        cur = self.conn.execute('''DELETE FROM Cards WHERE id = ?''', (self.card.multiverseid,))
        assert cur.rowcount == 1
        self.conn.commit()
        Log.info("Deleted %s" % self)
        return True

    def __str__(self):
        return str(self.card)
