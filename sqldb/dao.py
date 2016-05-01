import logging

log = logging.getLogger(__name__)


class FieldDesc(object):
    def __init__(self, name, field_type):
        self.name = name
        self.field_type = field_type

    def sql(self, pkey):
        return "%s %s%s" % (
            self.name,
            self.field_type,
            self.name == pkey and " primary key" or "")


class TableDesc(object):
    def __init__(self, name, pkey, fields):
        self.name = name
        self.pkey = pkey
        self.fields = fields
        self.pkey_index = [f.name for f in fields].index(pkey)
        self.select_stmt = "select * from %s where %s = ?" % (name, pkey)
        self.insert_stmt = "insert into %s values (%s)" % (
            name, ", ".join(["?"] * len(fields)))
        self.update_stmt = "update %s set %s where %s = ?" % (
            name, ", ".join([("%s = ?" % f.name) for f in fields if f.name != pkey]), pkey)
        self.delete_stmt = "delete from %s where %s = ?" % (name, pkey)

    def create_table(self, conn):
        stmt = "create table %s (%s)" % (
            self.name,
            ", ".join([f.sql(self.pkey) for f in self.fields]))
        conn.execute(stmt)
        log.info("created table %s" % self.name)


class DAO(object):
    def __init__(self, table_desc, conn):
        self.td = table_desc
        self.conn = conn

    def values_excl_pkey(self):
        v = self.get_values()
        v.pop(self.td.pkey_index)
        return v

    def find_by_pkey(self):
        cur = self.conn.execute(self.td.select_stmt,
                                [self.get_pkey()])
        assert cur.rowcount <= 1
        return cur.fetchone()

    def insert(self):
        self.conn.execute(self.td.insert_stmt,
                          self.get_values())
        log.info("added %s" % self)

    def update(self):
        row = self.find_by_pkey()
        v = self.get_values()
        different = False
        for i, f in enumerate(self.td.fields):
            if row[i] != v[i]:
                log.debug("field %s changed from %s to %s" % (f.name, row[i], v[i]))
                different = True
        if different:
            self.conn.execute(self.td.update_stmt,
                              self.values_excl_pkey() + [self.get_pkey()])
            log.info("updated %s" % self)
        else:
            log.debug("%s unchanged" % self)

    def save(self):
        row = self.find_by_pkey()
        if not row:
            return self.insert()
        else:
            return self.update()

    def delete(self):
        row = self.find_by_pkey()
        if not row:
            log.error("%s not found" % self)
        else:
            cur = self.conn.execute(self.td.delete_stmt, [self.get_pkey()])
            assert cur.rowcount == 1
            log.info("deleted %s" % self)
