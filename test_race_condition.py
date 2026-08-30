import socket
import json
import threading

HOST = "127.0.0.1"
PORT = 5000
ROOM_ID = "R101"
NUM_CLIENTS = 10

results = []
results_lock = threading.Lock()
barrier = threading.Barrier(NUM_CLIENTS)

def worker(client_index):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    request = {"action": "LOCK_ROOM", "room_id": ROOM_ID}
    message = json.dumps(request).encode("utf-8")

    barrier.wait()

    sock.sendall(message)
    data = sock.recv(1024)
    response = json.loads(data.decode("utf-8"))

    with results_lock:
        results.append((client_index, response["status"], response["message"]))

    sock.close()

threads = []
for i in range(NUM_CLIENTS):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("\n=== TEST RESULTS ===")
success_count = 0
for client_index, status, message in sorted(results):
    print(f"Client {client_index}: status={status} ({message})")
    if status == 202:
        success_count += 1

print(f"\nClients that successfully locked the room: {success_count} / {NUM_CLIENTS}")
assert success_count == 1, "FAIL: More than one client acquired the lock — race condition detected!"
print("PASS: Exactly one client succeeded. System is thread-safe.")