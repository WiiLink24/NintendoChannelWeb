import socket
import json
import config


def file_generator_socket(arguments: str):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect("/tmp/nc-gen.sock")
        payload = {
            "arguments": arguments,
            "secret": config.socket_secret
        }
        payload_raw = json.dumps(payload).encode("utf-8")
        client.send(payload_raw)
        resp_raw = client.recv(1024)
        resp = json.loads(resp_raw.decode("utf-8"))
        client.close()

    return resp