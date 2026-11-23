"""Run the API with uvicorn on one dual-stack socket ([::]:PORT, IPv4 too).

`uvicorn --host ::` listens on IPv6 only. Railway's private network is IPv6, but
IPv4-only setups (plain Docker, local tests) need IPv4 as well, so bind the
socket here with IPV6_V6ONLY off and hand it to uvicorn.
"""

import os
import socket

import uvicorn

sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
sock.bind(("::", int(os.environ.get("PORT", "8000"))))

config = uvicorn.Config("main:app", host="::", port=int(os.environ.get("PORT", "8000")))
uvicorn.Server(config).run(sockets=[sock])
