import socket, time

# global variables that can be accessed from outside this file
# (sometimes, you have to pass in the active TCP_CONX or UDP_SOCKET to send a file, which is why they have to be public)
signaling_port = 10007
data_channel_port = 10009
TCP_SOCKET = None
UDP_SOCKET = None
TCP_REMOTE_PEER = None
TCP_CONNECTION = None

def readFrom(protocol, sock, bufSize = 1024):
    global TCP_REMOTE_PEER
    try:
        assert bufSize > 1
        if protocol == "TCP":
            try:
                return sock.recv(bufSize)
            except Exception as e:
                return None
        elif protocol == "UDP":
            assert bufSize < 65535
            try:
                return sock.recv(bufSize)
            except Exception as e:
                return None
    except (ConnectionResetError, OSError, BrokenPipeError) as e:
        print(f"[net wrapper] Cx Error {e}! Recx logic disabled.")
        #initConnection()


def sendTo(protocol, sock, message, destiny = None):
    try:
        if protocol == "TCP":
            sock.sendall(message)
        else:
            assert destiny != None
            sock.sendto(message, (destiny, data_channel_port))
        return None
    except (ConnectionResetError, OSError, BrokenPipeError) as e:
        print(f"[net wrapper] Cx Error {e}! Recx logic disabled.")
        #initConnection()

def setupParameters(tcpport = 10007, udpport = 10009):
    global signaling_port, data_channel_port
    signaling_port = tcpport
    data_channel_port = udpport
    
def initConnection():
    print("[net wrapper] Waiting to connect again...")
    global TCP_CONNECTION, TCP_SOCKET, UDP_SOCKET, TCP_REMOTE_PEER, signaling_port, data_channel_port
    # if we're breaking up with the current pair, we close() the sockets in preparation for a nwe partner
    if TCP_SOCKET:
        TCP_SOCKET.close()
        TCP_SOCKET = None
        print("[net wrapper] Closed TCP socket.")
    if UDP_SOCKET:
        UDP_SOCKET = None
        print("[net wrapper] Closed UDP socket.")

    TCP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCP_SOCKET.setblocking(0)
    TCP_SOCKET.bind(("0.0.0.0", signaling_port))
    print(f"[net wrapper] Listening on TCP port {signaling_port}")
    TCP_SOCKET.listen()
    
    # the program will block until someone else connects to the server
    while True:
        try:
            conn, addr = TCP_SOCKET.accept()
            break
        except:
            # do nothing, because there is no connection
            pass

    print(f"[net wrapper] Remote peer has connected: {addr}")

    # now that everything is set up, we can set global objects that can be read from outside this file
    TCP_CONNECTION = conn
    TCP_CONNECTION.setblocking(0)
    TCP_CONNECTION.send(bytes(str(data_channel_port), "ascii"))
    TCP_REMOTE_PEER = addr
    UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP_SOCKET.setblocking(0)
    print("[net wrapper] Success!")
    UDP_SOCKET.bind( ("0.0.0.0", data_channel_port) )
    
