from dao import DAO, TableDesc, FieldDesc


set_td = TableDesc("Sets", "code",
                   [FieldDesc("code", "text"),
                    FieldDesc("name", "text")])


class SetDAO(DAO):
    @staticmethod
    def create_table(conn):
        set_td.create_table(conn)

    def __init__(self, code, name, conn):
        super(SetDAO, self).__init__(set_td, conn)
        self.code = code
        self.name = name

    def get_pkey(self):
        return self.code

    def get_values(self):
        return [self.code,
                self.name]

    def __str__(self):
        return "set %s (%s)" % (self.code, self.name)
