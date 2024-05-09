from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
import sqlite3

db = sqlite3.connect("../../nostr-rs-relay/nostr.db")
db = db.cursor()

def tags(request):
    prefix = request.params.get("prefix")
    if not prefix:
        # Missing or empty prefix.
        return {"tags": []}

    prefix = prefix.replace("\\", "\\\\").replace("%", "\\%") + "%"

    q = db.execute(
    	"SELECT DISTINCT value FROM tag"\
        " WHERE name='s' AND value LIKE :prefix ESCAPE '\\'",
            dict(prefix=prefix))

    tags = list(map(lambda x: x[0], q.fetchall()))
    return {"tags": tags}

if __name__ == '__main__':
    with Configurator() as config:
        config.add_route('tags', '/api/tags')
        config.add_view(tags, route_name='tags', renderer='json')
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 4000, app)
    print("Tagserver listening on 127.0.0.1:4000")
    server.serve_forever()
