import http.server
import sqlite3
import datetime
import botconfig
import os

os.chdir(botconfig.home_folder)

class WebHandler(http.server.SimpleHTTPRequestHandler):
    # def log_message(self, format, *args):
    #    return


    def do_GET(self):
        result = """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head><meta charset='UTF-8'>
        <meta property="og:url"                content="http://ajezek.cz:8000" />
        <meta property="og:type"               content="article" />
        <meta property="og:title"              content="Jídelní lístek" />
        <meta property="og:description"        content="Školní jídelna Gymnázium Roudnice" />
        <meta property="og:image"              content="https://ajezek.cz/images/icon_jidelna.png" />
        </head><body>
        <h1>Jídelní lístek</h1><br/>"""  # <h2>Školní jídelna Gymázium Roudnice nad Labem<h2/>"
        db = sqlite3.connect("database.sqlite3")
        c = db.cursor()
        c.execute("SELECT * FROM foods WHERE date >= julianday(?) ORDER BY date;",
                  ([datetime.date.today().strftime("%Y-%m-%d")]))
        result += '<table style="text-align: left;" border="1">'
        for r in c.fetchall():
            result += "<tr><th>" + r[2] + "</th><th>" + r[3].replace("\n", "<br/>") + "</th></tr>"
        result += """</table>
        </body>
        </html>
"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(str(result), "utf-8"))


server = http.server.HTTPServer(("0.0.0.0", 8000), WebHandler)
server.serve_forever()
