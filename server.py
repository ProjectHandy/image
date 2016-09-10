import socket
import sys
import struct
sys.path.append('gen-py')
sys.path.append('gen-py/image')

from image import Images
from image.ttypes import *

from thrift.transport import TSSLSocket, TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from collections import namedtuple
import urllib2
import json

import atexit

import sqlite3
conn = sqlite3.connect("image.db")
c = conn.cursor()

def db_init(conn, c):
    c.execute("create table if not exists Book(isbn, title, author, image)")
    c.execute("create table if not exists Item(id, images)")
    conn.commit()

db_init(conn, c)

Book = namedtuple('Book', ['title', 'author', 'isbn', 'image'])

def google_query_book(isbn):
    querylink = 'https://www.googleapis.com/books/v1/volumes?q=isbn:%s' % isbn
    reply = json.loads(urllib2.urlopen(querylink).read())
    volumeInfo = reply['items'][0]['volumeInfo']
    return Book(title=volumeInfo['title'],
                author=volumeInfo['authors'][0],
                isbn=volumeInfo['industryIdentifiers'][0]['identifier'],
                image=urllib2.urlopen(volumeInfo['imageLinks']['thumbnail']))

def db_get_book(isbn):
    c.execute("select * from Book where isbn = ?", (isbn))
    row = c.fetchone()
    if row:
        return Book(isbn=c[0], title=c[1], author=c[2], image=c[3])
    else:
        book = google_query_book(isbn)
        c.execute("insert into Book values(?, ?, ?, ?)", (isbn, book.title, book.author, book.image))
        conn.commit()
        return book

class ImagesHandler:
    def getSellItemImages(self, id):
        c.execute("select images from Item where id = ?", (id,))
        return eval(c.fetchone()[0])

    def getBookCoverImage(self, isbn):
        book = db_get_book(isbn)
        return book.image

    def postSellItemImages(self, id, images):
        c.execute("insert into Item values(?, ?)", id, repr(images))
        conn.commit()

    def queryIsbn(self, isbn):
        book = db_get_book(isbn)
        return [book.title, book.author]

handler = ImagesHandler()
processor = Images.Processor(handler)
transport = TSSLSocket.TSSLServerSocket("localhost", 9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

def exit_handler():
    print('My application is ending!')
    conn.close()

atexit.register(exit_handler)

print("Starting thrift server in python...")
server.serve()
print("done!")
