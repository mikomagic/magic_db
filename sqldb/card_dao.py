import logging
from dao import DAO, TableDesc, FieldDesc

log = logging.getLogger(__name__)


card_td = TableDesc("Cards", "multiverseid",
                    [FieldDesc("multiverseid", "int"),
                     FieldDesc("set_code", "text"),
                     FieldDesc("number", "int"),
                     FieldDesc("name", "text"),
                     FieldDesc("language", "text"),
                     FieldDesc("translation_of", "int"),
                     FieldDesc("back_face_of", "int"),
                     FieldDesc("equivalent_to", "int")])


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
                self.card.set_code,
                self.card.number,
                self.card.name.decode('utf-8'),
                self.card.language,
                self.card.translation_of.multiverseid if self.card.translation_of else None,
                self.card.back_face_of.multiverseid if self.card.back_face_of else None,
                self.card.equivalent_to]

    def __str__(self):
        return str(self.card)
