from flask import Flask, request, Response
import socket

app = Flask(__name__)

def fib(n: int) -> int:
    if n < 0:
        raise ValueError("Sequence number must be non-negative")
    if n == 0:
        return 0
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

@app.route("/register", methods=["PUT"])
def register():
    try:
        data = request.get_json(force=True)
        hostname = data["hostname"]
        ip = data["ip"]
        as_ip = data["as_ip"]
        as_port = int(data["as_port"])
    except Exception:
        return Response("Bad Request: Invalid JSON body", status=400)

    # Simplified DNS registration message format
    dns_message = f"TYPE=A\nNAME={hostname} VALUE={ip} TTL=10\n"

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(4.0)
        sock.sendto(dns_message.encode("utf-8"), (as_ip, as_port))
        sock.recvfrom(1024)
        sock.close()
        return Response("Registration successful", status=201)
    except Exception as e:
        return Response(f"Registration failed: {str(e)}", status=500)

@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():
    num_str = request.args.get("number")
    if num_str is None:
        return Response("Missing parameter 'number'", status=400)

    try:
        # Rejects floats, strings, negative values
        val = int(num_str)
        if val < 0:
            return Response("Number must be a positive integer or zero", status=400)
        res = fib(val)
        return Response(str(res), status=200, mimetype="text/plain")
    except ValueError:
        return Response("Invalid format: 'number' must be an integer", status=400)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)