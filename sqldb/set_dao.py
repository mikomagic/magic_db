from dao import DAO, TableDesc, FieldDesc


set_td = TableDesc("Sets", "short_name",
                   [FieldDesc("short_name", "text"),
                    FieldDesc("full_name", "text")])


class SetDAO(DAO):
    @staticmethod
    def create_table(conn):
        set_td.create_table(conn)

    def __init__(self, short_name, full_name, conn):
        super(SetDAO, self).__init__(set_td, conn)
        self.short_name = short_name
        self.full_name = full_name

    def get_pkey(self):
        return self.short_name

    def get_values(self):
        return [self.short_name,
                self.full_name]

    def __str__(self):
        return "set %s (%s)" % (self.short_name, self.full_name)
