import socket
import json
import time

HOST = "127.0.0.1"
PORT = 5000
ROOM_ID = "R102"
LOCK_TIMEOUT_SECONDS = 30
BUFFER_SECONDS = 2 

def send_request(sock, request):
    sock.sendall(json.dumps(request).encode("utf-8"))
    data = sock.recv(1024)
    return json.loads(data.decode("utf-8"))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

print(f"=== Timeout Test: Room {ROOM_ID} ===\n")

# Step 1: Lock the room
print("[1] Locking room...")
res = send_request(sock, {"action": "LOCK_ROOM", "room_id": ROOM_ID})
print(f"    Response: {res}")
assert res["status"] == 202, f"FAIL: expected 202, got {res['status']}"
print("    -> Lock acquired successfully.\n")

# Step 2: Wait past the timeout window
wait_time = LOCK_TIMEOUT_SECONDS + BUFFER_SECONDS
print(f"[2] Waiting {wait_time}s for the lock to expire...")
time.sleep(wait_time)
print("    -> Wait complete.\n")

# Step 3: Try to confirm booking after expiry -> should fail with 410
print("[3] Attempting to confirm booking after expiry...")
res = send_request(sock, {"action": "CONFIRM_BOOKING", "room_id": ROOM_ID})
print(f"    Response: {res}")
assert res["status"] == 410, f"FAIL: expected 410, got {res['status']}"
print("    -> Correctly rejected: lock had already expired.\n")

# Step 4: Try locking the room again -> should succeed since it was released
print("[4] Attempting to lock the room again...")
res = send_request(sock, {"action": "LOCK_ROOM", "room_id": ROOM_ID})
print(f"    Response: {res}")
assert res["status"] == 202, f"FAIL: expected 202, got {res['status']}"
print("    -> Room was correctly released and is lockable again.\n")

print("=== PASS: Timeout mechanism works correctly ===")
sock.close()