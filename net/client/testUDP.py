import remote

remote.setupParameters()
try:
    remote.init_connection(input("Addr? "))
except Exception as e:
    print(f"Failed to establish a connection to the remote: {e}")

fn = 1
while True:
    r = remote.readFrom("UDP", remote.UDP_SOCKET, 2048)
    #print(r)
    if r != None:
        print("Received from remote: ",r)        
        fn += 1
        
    if fn % 5 == 0:
        remote.sendTo("TCP", remote.TCP_SOCKET, "I just recv'd frame #"+str(fn))
            
# 10.81.0.156
# 192.168.137.1
