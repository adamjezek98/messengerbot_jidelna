# coding=utf-8
from lxml import html, etree
from collections import OrderedDict
import urllib.request
import urllib.request
import PyPDF2
import os
import re
import sqlite3
import botconfig
os.chdir(botconfig.home_folder)
dbname = botconfig.db_path

def get_links():
    pg = urllib.request.urlopen("http://www.gym-rce.cz/cz/o-skole/skolni-jidelna/jidelni-listek/")
    dt = pg.read().decode("utf-8")
    pg.close()
    tree = html.fromstring(dt)
    content = tree.xpath("//div[@id='contentRight']")
    content = html.fromstring(html.tostring(content[0]))
    links = []
    for link in content.xpath("//a"):
        for atr, val in link.attrib.items():
            if atr == "href" and "cms/get/file" in val:
                links.append("http://www.gym-rce.cz/cms/"+val.replace("./cms/",""))
    return links

def download_files(links):
    for link in links:
        urllib.request.urlretrieve(link,"temp/"+link.split("?")[-1]+".pdf")

replaces = OrderedDict([("ì","ě"),
("š","ť"),
("ø","ř"),
("ù","ů"),
("è","č"),
("ı","š"),
("ò","ň")])

def process_pdfs():
    for f in os.listdir("temp"):
        filename = "temp/"+f
        print(filename)
        pdf_file = open(filename,"rb")
        rpdf = PyPDF2.PdfFileReader(pdf_file)
        txt = rpdf.getPage(0).extractText()
        pdf_file.close()
        for c1, c2 in replaces.items():
            txt = txt.replace(c1,c2)
            txt = txt.replace(c1.upper(),c2.upper())
        week = txt.split("oddoPondělí")[0]
        body = txt.split(week+"oddo")[-1]
        week = week[0:10]+"-"+week[10:]
        print(week)

        body = body.split("Seznam alergenů")[0].replace("obsahuje alergeny: ","")
        #print(body)

        days = body.split("Oběd")
        al_chars = "1234567890,abcde"
        print("")
        for day in days:
            #print(day)
            try:
                while day[0] in al_chars: # or day[1] in al_chars:
                    day = day[1:]
            except:
                pass
            date_end = re.search("\d{1,2}\.\d{1,2}\.\d{4}",day)
            if date_end == None:
                continue
            date_end = date_end.end()
            daydate = day[0:date_end]
            print(daydate)
            date = daydate.split(" ")[-1]
            #print(date)
            d = day [date_end:]
            #print(d)
            meals = d.split("Polévka")
            for i in range(len(meals)):
                try:
                    while meals[i][0] in al_chars: # or meals[i][1] in al_chars:
                        meals[i] = meals[i][1:]
                except:
                   pass
            #print(meals)
            meal = "Pol.:\t" + meals[0] +"\nOběd:\t"+meals[1]
            #print(meal)
            write_to_db(date,daydate,meal)
            print("")
        os.rename(filename,"jidelnicky/"+week+".pdf")

def write_to_db(date, daydate, meal):
    db = sqlite3.connect(dbname)
    c = db.cursor()
    date = date.split(".")
    if len(date[1]) == 1:
        date[1] = "0"+date[1]
    if len(date[0]) == 1:
        date[0] = "0"+date[0]
    date = date[2] + "-" + date[1] + "-" + date[0]
    c.execute("select * from foods where date=julianday(?)",([date]))
    res = c.fetchall()
    print(date,daydate,meal)
    if not res:
        c.execute("INSERT INTO foods VALUES(NULL,julianday(?),?,?)",(date,daydate,meal))
        print(date,daydate,meal)
        db.commit()
        db.close()
    else:
        print("already in db",date,daydate,meal)


#print(get_links())
download_files(get_links())

#db = sqlite3.connect(dbname)
#c = db.cursor()
#c.execute("""CREATE TABLE  foods  (	 id 	INTEGER,	 date 	REAL,	 daydate 	TEXT,	 meal 	TEXT,	PRIMARY KEY( id ));""")
#db.commit()
process_pdfs()
