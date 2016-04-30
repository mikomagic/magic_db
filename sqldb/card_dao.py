from common.logger import Log
from dao import DAO, TableDesc, FieldDesc


card_td = TableDesc("Cards", "multiverseid",
                    [FieldDesc("multiverseid", "int"),
                     FieldDesc("name", "text"),
                     FieldDesc("language", "text"),
                     FieldDesc("set_id", "text"),
                     FieldDesc("card_number", "int")])


class CardDAO(DAO):
    @staticmethod
    def create_table(conn):
        card_td.create_table(conn)

    @staticmethod
    def delete_set(set_id, conn):
        stmt = "delete from Cards where set_id = ?"
        cur = conn.execute(stmt, [set_id])
        Log.info("deleted all %d cards of set %s" % (cur.rowcount, set_id))

    def __init__(self, card, set_id, conn):
        super(CardDAO, self).__init__(card_td, conn)
        self.card = card
        self.set_id = set_id

    def get_pkey(self):
        return self.card.multiverseid

    def get_values(self):
        return [self.card.multiverseid,
                self.card.name.decode('utf-8'),
                self.card.language,
                self.set_id,
                self.card.number]

    def __str__(self):
        return str(self.card)
