from common.logger import Log


class TableDesc(object):
    def __init__(self, name, pkey, fields):
        self.name = name
        self.pkey = pkey
        self.fields = fields
        self.pkey_index = fields.index(pkey)
        self.select_query = "select * from %s where %s = ?" % (
            self.name,
            self.pkey)
        self.insert_query = "insert into %s values (%s)" % (
            self.name,
            ", ".join(["?"] * len(self.fields)))
        self.update_query = "update %s set %s where %s = ?" % (
            self.name,
            ", ".join([("%s = ?" % f) for f in self.fields if f != self.pkey]),
            self.pkey)


class DAO(object):
    def __init__(self, table_desc, conn):
        self.td = table_desc
        self.conn = conn

    def values_excl_pkey(self):
        v = self.get_values()
        v.pop(self.td.pkey_index)
        return v

    def find_by_pkey(self):
        cur = self.conn.execute(self.td.select_query,
                                [self.get_pkey()])
        assert cur.rowcount <= 1
        return cur.fetchone()

    def insert(self):
        self.conn.execute(self.td.insert_query,
                          self.get_values())
        self.conn.commit()
        Log.info("Added %s" % self)

    def update(self):
        self.conn.execute(self.td.update_query,
                          self.values_excl_pkey() + [self.get_pkey()])
        self.conn.commit()
        Log.info("Updated %s" % self)

    def save(self):
        row = self.find_by_pkey()
        if not row:
            return self.insert()
        else:
            return self.update()

