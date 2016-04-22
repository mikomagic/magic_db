from logger import Log

class CardItem(object):
    def __init__(self):
        self.multiverseid = None
        self.number = None

        self.name = None
        self.artist = None
        self.color = None
        self.rarity = None

        self.back_side = None
        self.front_side = None

        self.language = "en"
        # English cards reference all translations
        # Non-English cards reference the English card
        self.translations = {} # lang -> multiverseid

    def link_back_side(self, other):
        assert self.front_side is None and self.back_side is None
        assert other.front_side is None and other.back_side is None
        self.back_side = other.multiverseid
        other.front_side = self.multiverseid
        Log.debug("linked %s as back side of %s" % (other, self))

    def add_translation(self, translated, db):
        lang = translated.language
        assert not lang in self.translations
        self.translations[lang] = translated.multiverseid
        translated.translations["en"] = self.multiverseid
        for attr in ['number', 'artist', 'color', 'rarity']:
            if not getattr(translated, attr):
                setattr(translated, attr, getattr(self, attr))
            assert getattr(self, attr) == getattr(translated, attr)
        if self.front_side:
            front_en = db.get(self.front_side)
            front_tr = db.get(front_en.translations[lang])
            front_tr.link_back_side(translated)
        Log.debug("%s is the translation of %s" % (translated, self))

    def has_translations(self):
        return self.translations and True

    def __str__(self):
        return "%3d, %s, %s" % (self.number,
                                self.multiverseid,
                                self.name)
