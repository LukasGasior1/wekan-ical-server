from wekanapi import WekanApi
import BaseHTTPServer
import vobject
import dateutil.parser

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 8091

WEKAN_HOST = "http://127.0.0.1:8090"
WEKAN_USER = "admin"
WEKAN_PASSWORD = "admin"

def create_ical_event(cal, board, card, card_info):
    event = cal.add('vevent')
    event.add('summary').value = board.title + ": " + card_info['title']
    event.add('dtstart').value = dateutil.parser.parse(card_info['dueAt'])
    if 'description' in card_info: event.add('description').value = card_info['description']
    event.add('url').value = WEKAN_HOST + "/b/" + board.id + "/x/" + card.id

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        wekan_api = WekanApi(WEKAN_HOST, {"username": WEKAN_USER, "password": WEKAN_PASSWORD})

        cal = vobject.iCalendar()
        boards = wekan_api.get_user_boards()
        for board in boards:
            cardslists = board.get_cardslists()
            for cardslist in cardslists:
                cards = cardslist.get_cards()
                for card in cards:
                    info = card.get_card_info()
                    if "dueAt" in info: create_ical_event(cal, board, card, info)

        s.send_response(200)
        s.send_header("Content-type", "text/calendar")
        s.end_headers()
        s.wfile.write(cal.serialize())

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((LISTEN_HOST, LISTEN_PORT), MyHandler)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
