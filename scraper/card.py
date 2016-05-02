import logging

log = logging.getLogger(__name__)


class Card(object):
    '''Technically, a card face, in a particular translations.  Practically,
    anything with a multiverseid. '''
    def __init__(self):
        self.multiverseid = None     # (int) unique identifier
        self.set_code = None         # (str) three-letter set code (all upper case)
        self.number = None           # (int) collector's number; identifies a physical colletible card within the set
                                     # same for front and back of double-sided cards, and for all translations
        self.equivalent_to = None    # (int) first multiverseid (not necessarily lowest) from All Sets;
                                     # this should reference (one of the) earliest equivalent English card(s);
                                     # None, if this was a self-reference
        self.name = None             # (str) UTF-8 encoded name in the respective language
        self.artist = None
        self.color = None
        self.rarity = None           # single letter rarity code (i.e., 'C', 'U', 'R', 'M', or 'L')
        self.back_face = None        # (Card) link to back face, if any
        self.back_face_of = None     # (Card) link to front face (back faces only)
        self.language = "en"         # two letters, from languages.ALL_LANGS
        self.translation_of = None   # (Card) link to English card for non-English cards
        self.translations = {}       # 2-letter lang -> Card; only on English cards

    def link_back_face(self, back_face):
        # assert both unlinked
        assert not self.back_face_of and not self.back_face
        assert not back_face.back_face_of and not back_face.back_face

        # link
        self.back_face = back_face
        back_face.back_face_of = self
        log.debug("linked %s as back face of %s" % (back_face, self))

    def add_translation(self, translated):
        # assert translated card non-English and unlinked
        assert translated.language != "en"
        assert translated.translation_of is None
        assert not translated.translations

        # assert this card English and unlinked
        assert self.language == "en"
        assert self.translation_of is None
        assert not translated.language in self.translations

        # copy other attributes
        for attr in ['set_code', 'number', 'artist', 'color', 'rarity']:
            if not getattr(translated, attr):
                setattr(translated, attr, getattr(self, attr))
            assert getattr(self, attr) == getattr(translated, attr)

        # link
        self.translations[translated.language] = translated
        translated.translation_of = self
        log.debug("linked %s as translation of %s" % (translated, self))

        # equivalence of non-English card
        translated.equivalent_to = self.equivalent_to or self.multiverseid

        # double-sided cards (assume English card correct at this point)
        if self.back_face_of:
            assert not translated.back_face_of
            front_en = self.back_face_of
            # assume front face already linked to translation
            front_tr = front_en.translations[translated.language]
            front_tr.link_back_face(translated)

    def has_translations(self):
        return self.translations and True

    def __str__(self):
        return "%3d, %s, %s" % (self.number if self.number is not None else -1,
                                self.multiverseid,
                                self.name)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
