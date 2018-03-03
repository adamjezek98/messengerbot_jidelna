import urllib.request
from datetime import datetime
import lxml.html as ET
import sqlite3
import botconfig
import tools
import copy
import sender

db = sqlite3.connect(botconfig.db_path)
c = db.cursor()

class ClassScraper():
    def get_html(self, url):
        f = urllib.request.urlopen(url)
        html = str(f.read(), "windows-1250")
        return html

    def suplovani(self):
        html = self.get_html("http://old.gym-rce.cz/suplobec.htm")
        root = ET.fromstring(html)
        alldays = html.split('<p class="textlarge_3">Suplování:')
        classStructs = []
        for oneday in alldays[1:]:
            oneday = '<p class="textlarge_3">Suplování:' + oneday

            root = ET.fromstring(oneday)
            day = root.findall('.//p[@class="textlarge_3"]')
            date = day[0].text.split(" ")[1]

            rozvrhTrid = root.xpath('.//table[contains(.,"Změny v rozvrzích tříd")]')[0]
            lines = rozvrhTrid.xpath('.//tr[not(@class="tr_supltrid_3")]')
            classroom = ""
            classStruct = None

            for line in lines:
                nodes = line.xpath('.//td')
                supl = SuplStruct()
                newclassroom = self.get_td_p_or_none(nodes[0])

                if newclassroom is not None:  # if new class
                    classroom = newclassroom.replace(" ", "")
                    if classStruct is not None:
                        classStructs.append(copy.deepcopy(classStruct))

                    classStruct = ClassRoomStruct()
                    classStruct.suplStructs = []
                    classStruct.classroom = classroom
                    classStruct.date = datetime.strptime(date, "%d.%m.%Y")

                supl.classroom = classroom
                supl.hour = str(self.get_td_p_or_none(nodes[1])).replace(".hod", "")
                supl.subj = self.get_td_p_or_none(nodes[2])
                supl.group = self.get_td_p_or_none(nodes[3])
                supl.room = self.get_td_p_or_none(nodes[4])
                supl.type = self.get_td_p_or_none(nodes[5])
                supl.teacher = self.get_td_p_or_none(nodes[6])
                supl.oldteacher = self.get_td_p_or_none(nodes[7])
                supl.date = datetime.strptime(date, "%d.%m.%Y")
                is_new = supl.save_self_to_db_is_new()
                if is_new:
                    classStruct.has_new = True
                classStruct.suplStructs.append(supl)

            classStructs.append(copy.deepcopy(classStruct))

        for classroom in classStructs:
            if classroom.has_new:
                print(classroom.date, classroom.classroom)
                print(str(classroom))
                self.send_new_supl(classroom.classroom,str(classroom))

    def get_td_p_or_none(self, node):
        n = node.xpath(".//p")
        if (len(n)):
            return n[0].text
        return None

    def send_new_supl(self,classroom, text):
        c.execute("SELECT userid FROM class_notify WHERE room=?",[classroom])
        for user_id in c.fetchall():
            user_id = user_id[0]
            sender.send_message(user_id, text)



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
        s = self.hour + ". hodinu "
        if self.group is not None:
            s += "skupina "+self.group
            s += (" nemá " if self.type == "odpadá" or self.type == "přesun >>" else " má ")
        else:
            s +=(" nemáte " if self.type == "odpadá" or self.type == "přesun >>" else " máte ")
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
            c.execute(
                "INSERT INTO suplstructs(day, classroom, hour, subj, classgroup, room, type, teacher, oldteacher, UID) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)", (self.date, self.classroom, self.hour, self.subj, self.group, self.room,
                                                 self.type, self.teacher, self.oldteacher, self.get_uid()))

            db.commit()
            return True
        except sqlite3.IntegrityError:
            return True


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


classScraper = ClassScraper()
classScraper.suplovani()
