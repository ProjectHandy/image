import sys
sys.path.append('gen-py')
sys.path.append('gen-py/image')

from image import Images

from thrift import Thrift
from thrift.transport import TSocket, TSSLSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

transport = TTransport.TBufferedTransport(TSSLSocket.TSSLSocket('app.handytextbook.com', 9092, validate=False))
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = Images.Client(protocol)
transport.open()
print("client - getSellItemImages")
print("server - " + str(client.getSellItemImages("1")))
transport.close()
