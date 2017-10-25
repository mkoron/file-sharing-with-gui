"""
This is a simple peer-to-peer file sharing program with a GUI
interface.

Example:

    You can use the program as following:

        python guiclient.py urls.txt directory http://server.name:{portNumber}
"""

from xmlrpc.client import ServerProxy, Fault
from server import Node, UNHANDLED
from threading import Thread
from time import sleep
from utils import randomString
from os import listdir
import sys
import tkinter as tk

HEAD_START = 0.1
SECRET_LENGTH = 100


class ListableNode(Node):
    """
    List the files in the shared folder.
    """
    def list(self):
        return listdir(self.dirname)

class Client(tk.Frame):
    """
    A simple GUI interface to the Node class. 
    """
    def __init__(self, master, url, dirname, urlfile):
        super().__init__(master)
        self.node_setup(url, dirname, urlfile)
        self.pack()
        self.create_widgets()

    def node_setup(self, url, dirname, urlfile):
        self.secret = randomString(SECRET_LENGTH)
        n = ListableNode(url, dirname, self.secret)
        t = Thread(target=n._start)
        t.setDaemon(1)
        t.start()
        sleep(HEAD_START)
        self.server = ServerProxy(url)
        print(self.server)
        for line in open(urlfile):
            line = line.strip()
            self.server.hello(line)

    def create_widgets(self):
        self.input = input = tk.Entry(self)
        input.pack(side='left')

        self.submit = submit = tk.Button(self)
        submit['text'] = "Fetch"
        submit['command'] = self.fetchHandler
        submit.pack()

        self.files = files = tk.Listbox()
        files.pack(side='bottom', expand=True, fill=tk.BOTH)
        self.updateList()

    def fetchHandler(self):
        query = self.input.get()
        try:
            self.server.fetch(query, self.secret)
        except Fault as f:
            if f.faultCode != UNHANDLED: raise
            print("Couldn't find the file", query)

    def updateList(self):
        self.files.delete(0, tk.END)
        self.files.insert(tk.END, self.server.list())

def main():
    urlfile, directory, url = sys.argv[1:]

    root = tk.Tk()
    root.title("File Sharing Client")

    client = Client(root, url, directory, urlfile)
    client.mainloop()


if __name__ == '__main__':
    main()
