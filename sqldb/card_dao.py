import logging
from dao import DAO, TableDesc, FieldDesc

log = logging.getLogger(__name__)


card_td = TableDesc("Cards", "multiverseid",
                    [FieldDesc("multiverseid", "int"),
                     FieldDesc("name", "text"),
                     FieldDesc("language", "text"),
                     FieldDesc("set_code", "text"),
                     FieldDesc("card_number", "int")])


class CardDAO(DAO):
    @staticmethod
    def create_table(conn):
        card_td.create_table(conn)

    def __init__(self, card, conn):
        super(CardDAO, self).__init__(card_td, conn)
        self.card = card

    def get_pkey(self):
        return self.card.multiverseid

    def get_values(self):
        return [self.card.multiverseid,
                self.card.name.decode('utf-8'),
                self.card.language,
                self.card.set_code,
                self.card.number]

    def __str__(self):
        return str(self.card)
