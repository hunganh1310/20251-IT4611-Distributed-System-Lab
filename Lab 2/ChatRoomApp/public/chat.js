$(function(){
    // Tạo kết nối
    var socket = io.connect('http://localhost:3000')

    // Các biến trỏ tới các thẻ HTML
    var message = $("#message")
    var username = $("#username")
    var send_message = $("#send_message")
    var send_username = $("#send_username")
    var chatroom = $("#chatroom")

    // 1. Gửi tin nhắn (Emit message)
    send_message.click(function() {
        // Gửi sự kiện 'new_message' lên server kèm dữ liệu là nội dung tin nhắn
        socket.emit('new_message', {message: message.val()})
    });

    // 2. Lắng nghe tin nhắn mới (Listen on new_message)
    socket.on("new_message", (data) => {
        feedback.html('');
        // Xóa ô nhập liệu
        message.val('');
        // Thêm tin nhắn mới vào khung chat
        chatroom.append("<p class='message'>" + data.username + ": " + data.message + "</p>")
    });

    // 3. Gửi yêu cầu đổi tên (Emit a username)
    send_username.click(function() {
        socket.emit('change_username', {username: username.val()})
    });

    // 4. Lắng nghe sự kiện 'typing' (Listen on typing)
    var feedback = $("#feedback") // Khai báo biến trỏ đến thẻ div hiển thị thông báo
    
    message.bind("keypress", () => {
        socket.emit('typing')
    })

    // Lắng nghe sự kiện 'typing' từ server
    socket.on('typing', (data) => {
        feedback.html("<p><i>" + data.username + " is typing a message..." + "</i></p>")
    })
});