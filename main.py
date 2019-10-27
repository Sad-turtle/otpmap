import tornado.ioloop
from tornado.web import Application
from tornado.ioloop import IOLoop

from locator import ATMLocatorService
from qr import WithdrawalQRCodeService
from pending import ConfirmATMSelectionService, schedule_pending_visitor_cleanup
    
def make_app():
  urls = [
      ("/atms/([^/]+)/", ATMLocatorService),
      ("/withdraw/([^/]+)/", WithdrawalQRCodeService),
      ("/confirm/([^/]+)/", ConfirmATMSelectionService),
  ]
  return Application(urls)

if __name__ == '__main__':
    try:
        app = make_app()
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(8080)
        print("Listening on 0.0.0.0:8080")
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.start()
        schedule_pending_visitor_cleanup(ioloop)
    except KeyboardInterrupt:
        print("\nExiting")
