import urllib.request
from datetime import datetime
import lxml.html as ET
import sqlite3
import botconfig
import tools
import copy
import sender
from structs import ClassRoomStruct, SuplStruct


class ClassScraper():
    def __init__(self):
        self.db = sqlite3.connect(botconfig.db_path)
        self.c = self.db.cursor()

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
                self.send_new_supl(classroom.classroom, str(classroom))

    def get_td_p_or_none(self, node):
        n = node.xpath(".//p")
        if (len(n)):
            return n[0].text
        return None

    def send_new_supl(self, classroom, text):
        self.c.execute("SELECT userid FROM class_notify WHERE room=?", [classroom])
        for user_id in self.c.fetchall():
            user_id = user_id[0]
            sender.send_message(user_id, text)

    def send_from_db(self, user_id):
        self.c.execute("SELECT room FROM class_notify WHERE userid = ?", [user_id])
        text = ""
        for r in self.c.fetchall():
            classroom = r[0]
            self.c.execute("SELECT shortStr, day FROM suplstructs WHERE (classroom=? AND day >= JULIANDAY('now'))",
                           [classroom])

            olddate = None
            for row in self.c.fetchall():
                date = datetime.strptime(row[1].split(" ")[0],"%Y-%m-%d")
                supl = row[0]
                if date != olddate:
                    olddate = date
                    print(date)
                    text += "\n"+tools.get_cs_weekday(date).title() + " " + \
                            datetime.strftime(date, "%d.%m.") + " | " + classroom
                text += "\n"+supl
        sender.send_message(user_id, text)


if __name__ == "__main__":
    classScraper = ClassScraper()
    classScraper.suplovani()
    #classScraper.send_from_db(1508122325941445)
