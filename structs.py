import tools
import botconfig
import sqlite3
from datetime import datetime


class SuplStruct():
    classroom = None
    hour = None
    subj = None
    group = None
    room = None
    type = None
    teacher = None
    oldteacher = None
    date = None
    onlyText = None

    def __str__(self):
        s = "Třída " + tools.get_class_str(self.classroom)
        s += ", sk " + self.group if self.group else ""
        s += (" nemá " if self.type == "odpadá" else " má ") + self.hour + ". hodinu "
        s += self.subj if self.subj is not None else ""
        s += " s " + self.teacher if self.teacher is not None else ""
        s += " v " + self.room.replace("(", "").replace(")", "") if self.room is not None else ""
        if (self.type != "odpadá"):
            s += " místo " + str(self.oldteacher).replace("(", "").replace(")", "") if self.oldteacher else ""
        s += " (" + self.type + ")"
        return s

    def get_short_str(self):
        if self.onlyText != None:
            return  self.onlyText
        s = self.hour + ". hodinu "
        if self.group is not None:
            s += "skupina " + self.group
            s += (" nemá " if self.type == "odpadá" or self.type == "přesun >>" else " má ")
        else:
            s += (" nemáte " if self.type == "odpadá" or self.type == "přesun >>" else " máte ")
        s += self.subj if self.subj is not None else ""
        s += " s " + self.teacher if self.teacher is not None else ""
        s += " v " + self.room.replace("(", "").replace(")", "") if self.room is not None else ""
        if (self.type == "spojí" or self.type == "supluje"):
            s += " místo " + str(self.oldteacher).replace("(", "").replace(")", "") if self.oldteacher else ""
            s += " (" + self.type + ")"
        elif "přesun" in self.type:
            s += ", přesun " + str(self.oldteacher)

        return s

    def get_uid(self):
        uid = str(self.classroom) + ":"
        uid += str(self.hour) + ":"
        uid += str(self.subj) + ":"
        uid += str(self.group) + ":"
        uid += str(self.room) + ":"
        uid += str(self.type) + ":"
        uid += str(self.teacher) + ":"
        uid += str(self.oldteacher) + ":"
        uid += str(self.date)
        return uid

    def save_self_to_db_is_new(self):
        try:
            db = sqlite3.connect(botconfig.db_path)
            c = db.cursor()
            c.execute(
                "INSERT INTO suplstructs"
                "(day, classroom, hour, subj, classgroup, room, type, teacher, oldteacher, UID, shortStr) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (self.date, self.classroom, self.hour, self.subj, self.group, self.room,
                 self.type, self.teacher, self.oldteacher, self.get_uid(), self.get_short_str()))

            db.commit()
            return True
        except sqlite3.IntegrityError:
            return False


class ClassRoomStruct():
    suplStructs = []
    classroom = None
    date = None
    has_new = False

    def __str__(self):
        s = tools.get_cs_weekday(self.date).title() + " " + datetime.strftime(self.date, "%d.%m.")
        s += " | " + tools.get_class_str(self.classroom)
        for supl in self.suplStructs:
            s += "\n" + supl.get_short_str()
            # s += "\n" +str(supl)
        return s
