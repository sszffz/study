import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.Socket;

public class SocketClient {
    public static void main(String[] args) {
        try {
            Socket client = new Socket("192.168.150.11", 9090);
            client.setSendBufferSize(20);
            client.setTcpNoDelay(true);
            OutputStream out = client.getOutputStream();
            
            InputStream in = System.in;
            BufferedReader reader = new BufferedReader(new InputStreamReader(in));

            while(true) {
                String line = reader.readLine();
                if (line != null) {
                    byte[] bb = line.getBytes();
                    for (byte b: bb) {
                        out.write(b);
                    }
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
