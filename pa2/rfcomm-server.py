# file: rfcomm-server.py

# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $

from bluetooth import * # all things bring bluetooth

server_sock = BluetoothSocket(RFCOMM) # from RFCOMM file create bluetooth socket, it names server_socket
server_sock.bind(("", PORT_ANY))
server_sock.listen(1)  # Accessible one device

port = server_sock.getsockname()[1] # get port number

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"  # get random number

advertise_service(server_sock,
                  "SampleServer",
                  service_id=uuid,
                  service_classes=[uuid, SERIAL_PORT_CLASS],
                  profiles=[SERIAL_PORT_PROFILE],
#                  protocols = [ OBEX_UUID ]
                  )

print "Waiting for connection on RFCOMM channel %d" % port  # entered putty this line

client_sock, client_info = server_sock.accept()  # stop to waiting for connection
print "Accepted connection from ", client_info  # v    # after connect

try:
    while True:
        data = client_sock.recv(1024) # receive something my phone
        if len(data) == 0:
            break # data's length is zero , stop
        print "received [%s]" % data # print out
        sent = client_sock.send("received [%s]\n" % data)  # send something to phone from UDOO Board
        if sent == 0:
            raise RuntimeError("socket connection broken")
except IOError:
    pass

print "disconnected"

client_sock.close()
server_sock.close()
print "all done"