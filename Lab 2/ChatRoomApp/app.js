const express = require('express') 
const app = express() 
//set the template engine ejs 
app.set('view engine', 'ejs') 
//middlewares 
app.use(express.static('public')) 
//routes 
//routes
app.get('/', (req, res) => {
    res.render('index')
})
//Listen on port 3000 
server = app.listen(3000)

//socket.io instantiation
const io = require("socket.io")(server)

//listen on every connection
io.on('connection', (socket) => {
    console.log('New user connected')

    // Tên mặc định ban đầu là Anonymous
    socket.username = "Anonymous"

    // 1. Lắng nghe sự kiện đổi tên
    socket.on('change_username', (data) => {
        socket.username = data.username
    })

    // 2. Lắng nghe tin nhắn mới
    socket.on('new_message', (data) => {
        // Phát lại tin nhắn đó cho TẤT CẢ các client đang kết nối (broadcast)
        io.sockets.emit('new_message', {
            message: data.message, 
            username: socket.username
        });
    })

    // Lắng nghe sự kiện 'typing' (đang gõ)
    socket.on('typing', (data) => {
        // Gửi tin nhắn này đến tất cả mọi người TRỪ người gửi (broadcast)
        socket.broadcast.emit('typing', {
            username: socket.username
        })
    })
})