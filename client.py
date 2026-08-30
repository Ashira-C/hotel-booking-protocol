import socket;
import json;

def send_request(sock, request):
    message = json.dumps(request)
    sock.sendall(message.encode("utf-8"))
    print(f"Sent request to server: {request}")

    data = sock.recv(1024)
    response = json.loads(data.decode("utf-8"))
    print(f"Received response from server: {response}")
    return response

HOST = "127.0.0.1"
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print(f"Connected to server at {HOST}:{PORT}")

while True:
    print("\nHotel Booking menu")
    print("1. Search Rooms")
    print("2. Lock Room")
    print("3. Confirm Booking")
    print("4. Cancel Lock")
    print("0. Exit")
    choice = input("Enter your choice: ")

    if choice == "0":
        print("Exiting...")
        break
    elif choice == "1":
        request = {"action": "SEARCH_ROOMS"}
        send_request(client_socket, request)
    elif choice == "2":
        room_id = input("Enter room ID to lock: ")
        request = {"action": "LOCK_ROOM", "room_id": room_id}
        send_request(client_socket, request)
    elif choice == "3":
        room_id = input("Enter room ID to confirm booking: ")
        request = {"action": "CONFIRM_BOOKING", "room_id": room_id}
        send_request(client_socket, request)
    elif choice == "4":
        room_id = input("Enter room ID to cancel lock: ")
        request = {"action": "CANCEL_LOCK", "room_id": room_id}
        send_request(client_socket, request)
    else:
        print("Invalid choice. Please try again.")

client_socket.close()