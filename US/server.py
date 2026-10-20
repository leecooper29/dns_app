from flask import Flask, request, Response
import socket
import urllib.request
import urllib.error

app = Flask(__name__)

@app.route("/fibonacci", methods=["GET"])


def handle_fibonacci():
    print("Received args:", request.args)

    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return Response("Missing required parameters", status=400)

    try:
        int(number)
        as_port = int(as_port)
        fs_port = int(fs_port)
    except ValueError:
        return Response("Invalid parameter format", status=400)

    # Query Authoritative Server via UDP
    dns_query = f"TYPE=A\nNAME={hostname}\n"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)
        sock.sendto(dns_query.encode("utf-8"), (as_ip, as_port))
        data, _ = sock.recvfrom(2048)
        sock.close()
    except Exception as e:
        return Response(f"DNS query failed: {str(e)}", status=500)

    dns_response = data.decode("utf-8").strip()
    if dns_response == "NOT_FOUND":
        return Response("DNS record not found", status=404)

    fs_ip = None
    for line in dns_response.split("\n"):
        if line.startswith("VALUE="):
            fs_ip = line.split("=", 1)[1].strip()
            break

    if not fs_ip:
        return Response("Could not resolve IP from DNS response", status=500)

    # Query Fibonacci Server over HTTP
    fs_url = f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"
    try:
        req = urllib.request.Request(fs_url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8")
            return Response(body, status=resp.status, mimetype="text/plain")
    except urllib.error.HTTPError as e:
        return Response(e.read().decode("utf-8"), status=e.code)
    except Exception as e:
        return Response(f"Failed to reach Fibonacci Server: {str(e)}", status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)