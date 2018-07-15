from functools import reduce
from http.server import BaseHTTPRequestHandler, HTTPStatus, HTTPServer
import urllib
import json

from .visuals import format_tooltip


class MutableContainer:
    def __init__(self):
        self.value = None

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


def gen_server(get_handler, *args, port=8000, **kwargs):
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            get_handler(self, *args, **kwargs)

    return HTTPServer(('', port), RequestHandler)


def return_html(request_handler, html):
    b = bytearray()
    b.extend(map(ord, html))

    request_handler.send_response(HTTPStatus.OK)
    request_handler.send_header("Content-type", "text/html")
    request_handler.send_header("Content-Length", str(len(html)))
    # request_handler.send_header("Access-Control-Allow-Origin", "*")
    request_handler.end_headers()
    request_handler.wfile.write(b)


def get_handler(request_handler,
                final_selection: MutableContainer,
                template,
                env,
                graph,
                color_function=None,
                custom_tooltips=None,
                X=None,
                X_names=[],
                lens=None,
                lens_names=[]):

    parsed_path = urllib.parse.urlparse(request_handler.path)

    if parsed_path.path == "/":
        return_html(request_handler, template)

    elif parsed_path.path == "/tooltip":
        cluster_ids = json.loads(parsed_path.query)

        member_ids = [list(graph["nodes"].items())[i][1] for i in cluster_ids]
        member_ids = reduce((lambda x, y: set(x).union(set(y))), member_ids)
        member_ids = list(member_ids)
        member_ids.sort()

        tooltip = format_tooltip(env, member_ids, custom_tooltips, X, X_names, lens, lens_names, color_function, None)

        return_html(request_handler, tooltip)

    elif parsed_path.path == "/return_selection":
        final_selection.set(json.loads(parsed_path.query))
        return_html(request_handler, "")

