#!/bin/bash

# Khai bao mau sac cho dep
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

INTERFACE="eth0"
VIDEO_FILE="video.mp4"
VLC_PID=""

# Ham reset mang ve binh thuong
function reset_netem() {
    echo -e "${YELLOW}[System] Dang xoa cau hinh NetEm cu...${NC}"
    sudo tc qdisc del dev $INTERFACE root 2>/dev/null
    echo -e "${GREEN}[OK] Mang da tro lai binh thuong.${NC}"
}

# Ham ap dung NetEm
function apply_netem() {
    reset_netem
    echo -e "${YELLOW}[System] Dang ap dung cau hinh moi: $1${NC}"
    sudo tc qdisc add dev $INTERFACE root netem $1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK] Da ap dung thanh cong! Hay kiem tra video tren Windows.${NC}"
    else
        echo -e "${RED}[Loi] Khong the ap dung NetEm. Hay kiem tra quyen sudo.${NC}"
    fi
}

# Hien thi Menu
function show_menu() {
    clear
    echo "========================================================"
    echo "   AUTO SCRIPT LAB 3: VIDEO STREAMING & QOS (NETEM)"
    echo "========================================================"
    echo "1. Cài đặt môi trường & Tải video (Chạy lần đầu)"
    echo "2. Bắt đầu phát Video (Streaming Server)"
    echo "--------------------------------------------------------"
    echo "3. Thí nghiệm 1: Gây trễ (Delay 200ms) "
    echo "4. Thí nghiệm 2: Gây biến động trễ (Jitter 100ms ±20ms) "
    echo "5. Thí nghiệm 3: Gây mất gói (Packet Loss 10%) "
    echo "6. Thí nghiệm 4: Gây lặp gói (Duplicate 5%) [cite: 543]"
    echo "7. Thí nghiệm 5: Đảo thứ tự gói (Reorder) [cite: 558]"
    echo "--------------------------------------------------------"
    echo "8. Xóa mọi lỗi mạng (Về bình thường)"
    echo "9. Dừng Server, Xóa video & Thoát"
    echo "========================================================"
}

while true; do
    show_menu
    read -p "Chọn chức năng (1-9): " choice

    case $choice in
        1)
            echo -e "${YELLOW}Dang cai dat VLC va iproute2...${NC}"
            sudo apt update && sudo apt install vlc-bin vlc-plugin-base iproute2 -y
            echo -e "${YELLOW}Dang tai video mau...${NC}"
            # Xoa video cu neu co de tai cai moi
            rm -f $VIDEO_FILE
            wget http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4 -O $VIDEO_FILE
            echo -e "${GREEN}[OK] Hoan tat cai dat.${NC}"
            read -p "An Enter de quay lai menu..."
            ;;
        2)
            if [ ! -f "$VIDEO_FILE" ]; then
                echo -e "${RED}[Loi] Khong tim thay file video. Hay chon muc 1 truoc!${NC}"
            else
                # Chay VLC trong background, chuyen log vao /dev/null de khong bi rac man hinh
                cvlc -vvv $VIDEO_FILE --sout '#standard{access=http,mux=ts,dst=:8080}' --loop --sout-keep > /dev/null 2>&1 &
                VLC_PID=$!
                echo -e "${GREEN}[OK] Server dang phat video tai: http://localhost:8080${NC}"
                echo -e "${YELLOW}Luu y: Mo VLC tren Windows va Open Network Stream de xem.${NC}"
            fi
            read -p "An Enter de quay lai menu..."
            ;;
        3)
            # Delay 200ms
            apply_netem "delay 200ms"
            read -p "An Enter de quay lai menu..."
            ;;
        4)
            # Jitter 100ms +- 20ms
            apply_netem "delay 100ms 20ms"
            read -p "An Enter de quay lai menu..."
            ;;
        5)
            # Loss 10% (Chinh len 10% de de thay loi hon muc 0.1% cua lab)
            apply_netem "loss 10%"
            read -p "An Enter de quay lai menu..."
            ;;
        6)
            # Duplicate 5%
            apply_netem "duplicate 5%"
            read -p "An Enter de quay lai menu..."
            ;;
        7)
            # Reorder: 25% goi tin bi gui ngay lap tuc, cac goi khac tre 10ms
            apply_netem "delay 10ms reorder 25% 50%"
            read -p "An Enter de quay lai menu..."
            ;;
        8)
            reset_netem
            read -p "An Enter de quay lai menu..."
            ;;
        9)
            echo -e "${YELLOW}Dang don dep he thong...${NC}"
            # Dung VLC
            if [ ! -z "$VLC_PID" ]; then
                kill $VLC_PID 2>/dev/null
            fi
            # Xoa file video
            rm -f $VIDEO_FILE
            # Xoa NetEm
            sudo tc qdisc del dev $INTERFACE root 2>/dev/null
            echo -e "${GREEN}Da thoat va don dep sach se. Bye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Lua chon khong hop le!${NC}"
            sleep 1
            ;;
    esac
done
