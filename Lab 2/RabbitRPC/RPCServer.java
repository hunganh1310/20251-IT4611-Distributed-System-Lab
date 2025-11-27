import com.rabbitmq.client.*;

public class RPCServer {

    private static final String RPC_QUEUE_NAME = "rpc_queue";

    // Hàm tính số Fibonacci
    private static int fib(int n) {
        if (n == 0) return 0;
        if (n == 1) return 1;
        return fib(n - 1) + fib(n - 2);
    }

    public static void main(String[] argv) throws Exception {
        ConnectionFactory factory = new ConnectionFactory(); // Tạo kết nối đến RabbitMQ server
        factory.setHost("localhost"); // Đặt host là localhost

        try (Connection connection = factory.newConnection();
             Channel channel = connection.createChannel()) {
            
            // Khai báo hàng đợi
            channel.queueDeclare(RPC_QUEUE_NAME, false, false, false, null);
            channel.queuePurge(RPC_QUEUE_NAME);

            // Server chỉ nhận 1 yêu cầu xử lý tại 1 thời điểm
            channel.basicQos(1);

            System.out.println(" [x] Awaiting RPC requests");

            Object monitor = new Object();
            
            // Callback xử lý khi nhận được tin nhắn
            DeliverCallback deliverCallback = (consumerTag, delivery) -> {
                AMQP.BasicProperties replyProps = new AMQP.BasicProperties
                        .Builder()
                        .correlationId(delivery.getProperties().getCorrelationId())
                        .build();

                String response = "";

                try {
                    String message = new String(delivery.getBody(), "UTF-8");
                    int n = Integer.parseInt(message);

                    System.out.println(" [.] fib(" + message + ")");
                    response += fib(n);
                    try {
                        Thread.sleep(2000); // Ngủ 2 giây
                    } catch (InterruptedException _ignored) {
                        Thread.currentThread().interrupt();
                    }
                } catch (RuntimeException e) {
                    System.out.println(" [.] " + e.toString());
                } finally {
                    // Gửi kết quả trả về hàng đợi replyTo của Client
                    channel.basicPublish("", delivery.getProperties().getReplyTo(), replyProps, response.getBytes("UTF-8"));
                    // Xác nhận đã xử lý xong
                    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
                    
                    // Notify để tiếp tục chờ tin nhắn khác (cơ chế thread safe)
                    synchronized (monitor) {
                        monitor.notify();
                    }
                }
            };

            channel.basicConsume(RPC_QUEUE_NAME, false, deliverCallback, (consumerTag -> { }));

            // Vòng lặp chờ tin nhắn
            while (true) {
                synchronized (monitor) {
                    try {
                        monitor.wait();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        }
    }
}