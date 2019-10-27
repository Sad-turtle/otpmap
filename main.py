import tornado.ioloop
from tornado.web import Application
from tornado.ioloop import IOLoop

from locator import ATMLocatorService
from qr import WithdrawalQRCodeService
    
def make_app():
  urls = [
      ("/atms/([^/]+)/", ATMLocatorService),
      ("/withdraw/([^/]+)/", WithdrawalQRCodeService)
  ]
  return Application(urls)

if __name__ == '__main__':
    try:
        app = make_app()
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(8080)
        print("Listening on 0.0.0.0:8080")
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("\nExiting")
