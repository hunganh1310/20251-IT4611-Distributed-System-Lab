import socket
import sys

# --- CẤU HÌNH ---
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5050
ENCODING = 'utf-8'

def start_client():
    try:
        # Tạo socket và kết nối đến server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Đã kết nối đến {SERVER_HOST}:{SERVER_PORT}")
        print("Nhập lệnh (ví dụ: KV/1.0 GET key). Gõ 'exit' để thoát client.")

        while True:
            # 1. Đọc lệnh từ người dùng
            user_input = input("Client> ")
            
            if not user_input:
                continue

            if user_input.lower() == 'exit':
                break

            # 2. Gửi lệnh sang Server (Thêm \n vì đây là line-based protocol)
            # [cite: 20] Đơn vị thông điệp: dòng văn bản kết thúc bằng \n
            if not user_input.endswith('\n'):
                message = user_input + '\n'
            else:
                message = user_input
            
            client_socket.sendall(message.encode(ENCODING))

            # 3. Nhận phản hồi từ Server
            data = client_socket.recv(1024)
            response = data.decode(ENCODING).strip()
            
            # 4. In kết quả ra màn hình
            print(f"Server: {response}")

            # Nếu gửi lệnh QUIT thì client cũng nên chủ động thoát
            if "QUIT" in user_input.upper():
                break

    except ConnectionRefusedError:
        print("Lỗi: Không thể kết nối đến Server. Hãy chắc chắn Server đang chạy.")
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        client_socket.close()
        print("Đã ngắt kết nối.")

if __name__ == "__main__":
    start_client()