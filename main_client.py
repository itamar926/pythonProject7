import random
import sys
from client import Client


def main():
    print("=== Welcome to Onion Chat ===")

    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty.")
        sys.exit()

    listen_port = random.randint(10000, 50000)

    client = Client(
        name=username,
        server_host="127.0.0.1",
        server_port=9010,
        listen_port=listen_port,
        client_ip="127.0.0.1",
        keys=[33, 22, 11]
    )

    client.start()
    print(f"Logged in as '{username}' (Listening on port {listen_port})")
    print("To send a message, use: TargetName|Message (e.g., Bob|Hello!)")
    print("To broadcast to all, use: ALL|Message")
    print("-" * 50)

    while True:
        try:
            user_input = input(f"{username}> ")
            if not user_input.strip():
                continue

            if "|" not in user_input:
                print("Error: Invalid format. Please use TargetName|Message")
                continue

            target, msg = user_input.split("|", 1)
            client.send_message(target.strip(), msg.strip())

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()