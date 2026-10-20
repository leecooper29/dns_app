from flask import Flask, request, Response
import socket

app = Flask(__name__)

def get_fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Negative numbers not allowed")
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

@app.route("/register", methods=["PUT"])
def register():
    data = request.get_json(force=True, silent=True)
    if not data:
        return Response("Invalid JSON", status=400)

    hostname = data.get("hostname")
    ip = data.get("ip")
    as_ip = data.get("as_ip")
    as_port = data.get("as_port")

    if not all([hostname, ip, as_ip, as_port]):
        return Response("Missing fields", status=400)

    try:
        as_port = int(as_port)
    except ValueError:
        return Response("Invalid as_port", status=400)

    dns_message = f"TYPE=A\nNAME={hostname}\nVALUE={ip}\nTTL=10\n"

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)
        sock.sendto(dns_message.encode("utf-8"), (as_ip, as_port))
        ack, _ = sock.recvfrom(1024)
        sock.close()
    except Exception as e:
        return Response(f"Registration failed: {str(e)}", status=500)

    return Response("Registered successfully", status=201)

@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    number_str = request.args.get("number")
    if number_str is None:
        return Response("Missing parameter: number", status=400)

    try:
        n = int(number_str)
        if n < 0:
            return Response("Sequence number must be non-negative", status=400)
    except ValueError:
        return Response("Parameter 'number' must be an integer", status=400)

    result = get_fibonacci(n)
    return Response(str(result), status=200, mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)