import logging

log = logging.getLogger(__name__)


class Card(object):
    '''Technically, a card face, in a particular translations.  Practically,
    anything with a multiverseid. '''
    def __init__(self):
        self.multiverseid = None # unique identifier
        self.set_code = None     # three-letter set code
        self.number = None       # collector's number; same for front and back, and for all translations; unique within set

        self.name = None         # same for variations of the same card
        self.artist = None
        self.color = None
        self.rarity = None       # in [ 'C', 'U', 'R', 'M', 'L' ]

        self.back_face = None    # link to back face, if any
        self.back_face_of = None # link to front face (back faces only)

        self.language = "en"     # two letters, from languages.ALL_LANGS
        self.translations = {}   # { lang -> card }, English cards reference all translations, non-English cards reference English card only

    def link_back_face(self, other):
        assert not self.back_face_of and not self.back_face
        assert not other.back_face_of and not other.back_face
        self.back_face = other
        other.back_face_of = self
        log.debug("linked %s as back face of %s" % (other, self))

    def add_translation(self, translated):
        lang = translated.language
        assert not lang in self.translations
        assert not translated.translations
        self.translations[lang] = translated
        translated.translations["en"] = self
        for attr in ['set_code', 'number', 'artist', 'color', 'rarity']:
            if not getattr(translated, attr):
                setattr(translated, attr, getattr(self, attr))
            assert getattr(self, attr) == getattr(translated, attr)
        if self.back_face_of and not translated.back_face_of:
            front_en = self.back_face_of
            front_tr = front_en.translations[lang]
            front_tr.link_back_face(translated)
        log.debug("%s is the translation of %s" % (translated, self))

    def has_translations(self):
        return self.translations and True

    def __str__(self):
        return "%3d, %s, %s" % (self.number,
                                self.multiverseid,
                                self.name)
