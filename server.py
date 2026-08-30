import socket
import json
import threading

LOCK_TIMEOUT_SECONDS = 30

rooms = {
    "R101": {"state": "AVAILABLE", "price": 1200, "lock": threading.Lock(), "timer": None},
    "R102": {"state": "AVAILABLE", "price": 1500, "lock": threading.Lock(), "timer": None},
    "R103": {"state": "AVAILABLE", "price": 1000, "lock": threading.Lock(), "timer": None},
    "R104": {"state": "AVAILABLE", "price": 1800, "lock": threading.Lock(), "timer": None},
    "R105": {"state": "AVAILABLE", "price": 1300, "lock": threading.Lock(), "timer": None},
}

def available_rooms(request):
    available = {
        room_id: info["price"]
        for room_id, info in rooms.items()
        if info["state"] == "AVAILABLE"
    }
    return {
        "status": 200, "message": "OK", "available_rooms": available
    }

def timeout_lock(room_id):
    room_lock = rooms[room_id]["lock"]
    with room_lock:
        if rooms[room_id]["state"] == "LOCKED":
            rooms[room_id]["state"] = "AVAILABLE"
            rooms[room_id]["timer"] = None
            print(f"[LOG] Room {room_id} lock timeout ({LOCK_TIMEOUT_SECONDS}s) -> reverted to AVAILABLE")

def lock_room(request):
    room_id = request.get("room_id")
    if room_id not in rooms:
        return {"status": 404, "message": "Room not found"}

    room_lock = rooms[room_id]["lock"]
    with room_lock:
        if rooms[room_id]["state"] != "AVAILABLE":
            return {"status": 409, "message": "Room already locked"}

        rooms[room_id]["state"] = "LOCKED"

        timer = threading.Timer(LOCK_TIMEOUT_SECONDS, timeout_lock, args=(room_id,))
        timer.daemon = True
        rooms[room_id]["timer"] = timer
        timer.start()

        return {
            "status": 202,
            "message": "Lock Acquired",
            "room_id": room_id,
            "expires_in": LOCK_TIMEOUT_SECONDS 
        }

def confirm_booking(request):
    room_id = request.get("room_id")
    if room_id not in rooms:
        return {"status": 404, "message": "Room not found"}

    room_lock = rooms[room_id]["lock"]
    with room_lock:
        if rooms[room_id]["state"] != "LOCKED":
            return {"status": 410, "message": "Lock expired or room not locked"}

        if rooms[room_id]["timer"] is not None:
            rooms[room_id]["timer"].cancel()
            rooms[room_id]["timer"] = None

        rooms[room_id]["state"] = "BOOKED"
        return {"status": 201, "message": "Booking Confirmed", "room_id": room_id}

def cancel_lock(request):
    room_id = request.get("room_id")
    if room_id not in rooms:
        return {"status": 404, "message": "Room not found"}

    room_lock = rooms[room_id]["lock"]
    with room_lock:
        if rooms[room_id]["state"] == "LOCKED":
            if rooms[room_id]["timer"] is not None:
                rooms[room_id]["timer"].cancel()
                rooms[room_id]["timer"] = None
            rooms[room_id]["state"] = "AVAILABLE"
        return {"status": 200, "message": "OK", "room_id": room_id}

def handle_request(request):
    action = request.get("action")
    if action == "SEARCH_ROOMS":
        return available_rooms(request)
    elif action == "LOCK_ROOM":
        return lock_room(request)
    elif action == "CONFIRM_BOOKING":
        return confirm_booking(request)
    elif action == "CANCEL_LOCK":
        return cancel_lock(request)
    else:
        return {"status": 400, "message": "Bad Request"}

def handle_client(connection, address):
    print(f"[LOG] Client connected from {address}")

    while True:
        data = connection.recv(1024)
        if not data:
            print(f"[LOG] Client {address} disconnected")
            break

        try:
            request = json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            response = {"status": 400, "message": "Invalid JSON"}
            connection.sendall(json.dumps(response).encode("utf-8"))
            continue

        print(f"[LOG] Received request from {address}: {request}")

        response = handle_request(request)
        print(f"[LOG] Sending response to {address}: {response}")

        connection.sendall(json.dumps(response).encode("utf-8"))

    connection.close()

def main():
    HOST = "127.0.0.1"
    PORT = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        connection, address = server_socket.accept()
        client_thread = threading.Thread(
            target=handle_client, args=(connection, address)
        )
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    main()