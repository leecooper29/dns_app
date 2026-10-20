import socket
import os

AS_PORT = 53533
DB_FILE = "dns_records.txt"

def load_records():
    records = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    rec_type, name, value, ttl = parts
                    records[(rec_type, name)] = (value, ttl)
    return records

def save_record(rec_type, name, value, ttl):
    records = load_records()
    records[(rec_type, name)] = (value, ttl)
    with open(DB_FILE, "w") as f:
        for (t, n), (v, ttl_val) in records.items():
            f.write(f"{t},{n},{v},{ttl_val}\n")

def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", AS_PORT))
    print(f"AS listening on UDP port {AS_PORT}...")

    while True:
        data, client_addr = sock.recvfrom(2048)
        message = data.decode("utf-8").strip()
        lines = [line.strip() for line in message.split("\n") if line.strip()]

        parsed = {}
        for line in lines:
            if "=" in line:
                key, val = line.split("=", 1)
                parsed[key.strip()] = val.strip()

        # Registration format: TYPE, NAME, VALUE, TTL
        if "VALUE" in parsed and "TTL" in parsed:
            rec_type = parsed.get("TYPE")
            name = parsed.get("NAME")
            val = parsed.get("VALUE")
            ttl = parsed.get("TTL")
            save_record(rec_type, name, val, ttl)
            sock.sendto(b"SUCCESS\n", client_addr)

        # Query format: TYPE, NAME
        elif "NAME" in parsed and "TYPE" in parsed:
            rec_type = parsed.get("TYPE")
            name = parsed.get("NAME")
            records = load_records()
            if (rec_type, name) in records:
                value, ttl = records[(rec_type, name)]
                response = f"TYPE={rec_type}\nNAME={name}\nVALUE={value}\nTTL={ttl}\n"
                sock.sendto(response.encode("utf-8"), client_addr)
            else:
                sock.sendto(b"NOT_FOUND\n", client_addr)

if __name__ == "__main__":
    run_server()