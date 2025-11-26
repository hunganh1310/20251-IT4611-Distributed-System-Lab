import socket
import time

# --- CẤU HÌNH (Theo Interface Specification) ---
HOST = '127.0.0.1'  # [cite: 19]
PORT = 5050         # [cite: 19]
BUFFER_SIZE = 1024  # Kích thước gói tin nhận
ENCODING = 'utf-8'  # [cite: 21]

# --- KHO DỮ LIỆU (In-memory) ---
# Dùng Dictionary để lưu key-value 
DATA_STORE = {}

def log(message):
    """Ghi log kèm thời gian [cite: 67]"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{timestamp}] {message}")

def handle_request(request_line):
    """Xử lý logic của lệnh theo đúng Interface"""
    parts = request_line.strip().split()
    
    # Kiểm tra lệnh rỗng
    if not parts:
        return None

    # 1. Kiểm tra Phiên bản (Bắt buộc phải có KV/1.0 ở đầu) 
    if parts[0] != "KV/1.0":
        return "426 UPGRADE_REQUIRED"

    # Kiểm tra xem có lệnh (command) không
    if len(parts) < 2:
        return "400 BAD REQUEST"

    command = parts[1].upper() # [cite: 26]
    
    # 2. Xử lý từng lệnh cụ thể
    try:
        # Lệnh PUT <key> <value>
        if command == "PUT":
            if len(parts) < 4: # Cần: Version, Command, Key, Value
                return "400 BAD REQUEST"
            key = parts[2]
            value = " ".join(parts[3:]) # Lấy hết phần sau làm value
            DATA_STORE[key] = value
            return "201 CREATED" # [cite: 35]

        # Lệnh GET <key>
        elif command == "GET":
            if len(parts) < 3:
                return "400 BAD REQUEST"
            key = parts[2]
            if key in DATA_STORE:
                return f"200 OK {DATA_STORE[key]}" # [cite: 34]
            else:
                return "404 NOT FOUND" # [cite: 39]

        # Lệnh DEL <key>
        elif command == "DEL":
            if len(parts) < 3:
                return "400 BAD REQUEST"
            key = parts[2]
            if key in DATA_STORE:
                del DATA_STORE[key]
                return "204 NO CONTENT" # [cite: 37]
            else:
                # Idempotent: Xóa key không tồn tại vẫn phải trả về 404 theo đề bài
                return "404 NOT FOUND" # [cite: 68, 69]

        # Lệnh STATS
        elif command == "STATS":
            count = len(DATA_STORE)
            return f"200 OK keys={count}" # [cite: 58]

        # Lệnh QUIT
        elif command == "QUIT":
            return "200 OK bye" # [cite: 60]

        # Lệnh lạ
        else:
            return "400 BAD REQUEST"

    except Exception as e:
        log(f"Error: {e}")
        return "500 SERVER ERROR" # [cite: 41]

def start_server():
    """Hàm chính để chạy server"""
    # Tạo socket TCP [cite: 19]
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Cho phép dùng lại port ngay lập tức nếu server restart (tránh lỗi Address already in use)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((HOST, PORT))
    server_socket.listen(5) # Hàng đợi tối đa 5 kết nối
    
    log(f"Server đang chạy tại {HOST}:{PORT}...")

    try:
        while True:
            # Chấp nhận kết nối từ Client (Xử lý tuần tự) [cite: 65]
            client_socket, client_address = server_socket.accept()
            log(f"Kết nối mới từ: {client_address}")

            with client_socket:
                while True:
                    data = client_socket.recv(BUFFER_SIZE)
                    if not data:
                        break # Client ngắt kết nối
                    
                    # Giải mã tin nhắn [cite: 21]
                    request = data.decode(ENCODING).strip()
                    log(f"Nhận: {request}")
                    
                    # Xử lý
                    response = handle_request(request)
                    
                    if response:
                        log(f"Gửi: {response}")
                        # Gửi phản hồi kèm ký tự xuống dòng [cite: 20]
                        client_socket.sendall((response + "\n").encode(ENCODING))
                        
                        # Nếu lệnh là QUIT thì đóng kết nối này
                        if "QUIT" in request:
                            break
            
            log(f"Đóng kết nối với: {client_address}")

    except KeyboardInterrupt:
        log("Đang dừng server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()