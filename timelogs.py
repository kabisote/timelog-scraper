import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import requests
import lxml.html

from tornado.options import define, options
from datetime import date

define("port", default=8888, help="run on the given port", type=int)

URL = 'http://192.168.2.183/allied2011/timeslogs.cfm'
login_codes = {
    "Username": "my-username",
    "Password": "my-password",
    "Submit": "Submit",
}
crew = [
    ("11", "DSG", "Designer Dude1"),
    ("12", "DSG", "Designer Dude2"),
    ("13", "DSG", "Designer Dude3"),
    ("14", "DSG", "Designer Dude4"),
    ("15", "DSG", "Designer Dude5"),
    ("16", "PRG", "Programmer Dude1"),
    ("17", "PRG", "Programmer Dude2"),
    ("18", "PRG", "Programmer Dude3"),
    ("19", "PRG", "Programmer Dude4"),
    ("20", "PRG", "Programmer Dude5"),
]
timelogdata = {
    'LoginIDTimeSearch': None,
    'SearchDepartment': '0',
    'SerchSubmit': 'Search',
    'TimeDateSearch': None
}
logdate = date.today().strftime("%m/%d/%Y")

s = requests.Session()
s.post('http://192.168.2.183/allied2011/index.cfm', data=login_codes)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        designers = []
        programmers = []
        for c in crew:
            tmp = parselogdata(c[0], c[2], logdate)
            if c[1] == 'DSG':
                designers.append(tmp)
                continue
            programmers.append(tmp)
        designers.sort()
        programmers.sort()
        self.render('index.html', designers=designers, programmers=programmers, logdate=logdate)

    def post(self):
        designers = []
        programmers = []
        logdate = self.get_argument("the_date")
        for c in crew:
            tmp = parselogdata(c[0], c[2], logdate)
            if c[1] == 'DSG':
                designers.append(tmp)
                continue
            programmers.append(tmp)
        designers.sort()
        programmers.sort()
        self.render('index.html', designers=designers, programmers=programmers, logdate=logdate)


def parselogdata(crew_id, crew_name, logdate):
    timelogdata['LoginIDTimeSearch'] = crew_id
    timelogdata['TimeDateSearch'] = logdate
    html = s.post(URL, data=timelogdata).text
    tr = lxml.html.fromstring(html).cssselect('#TimeForm tr')
    total_time = tr[-2][8].text_content()
    rows = tr[5:-3]
    logs = []
    for row in rows:
        logs.append((row[2].text_content(), row[9].text_content(), row[11].text_content()))
    return (crew_name, logs, total_time)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
