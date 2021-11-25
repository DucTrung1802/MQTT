import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
from paho.mqtt import client as mqtt_client
import threading
import queue
import random
import time

broker = 'broker.emqx.io'
port = 1883
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'trung'
password = 'abcd1234'


class VIEW(tk.Tk):

    def __init__(self, controller, queue):
        super().__init__()
        self.controller = controller
        self.queue = queue

        self.title("Subscriber")
        # self.minsize(600, 768)
        self.geometry("250x400")
        self.resizable(False, False)
        # Adjust transparent of window tkinter (0 to 1)
        self.attributes('-alpha', 1)

        # windows only (remove the minimize/maximize button)
        # self.attributes('-toolwindow', True)

        self.view_rows_columns_configure()
        self.create_frames()

    def init_display(self):
        self.mainloop()

    def create_frames(self):
        self.main_frame = MAIN_FRAME(self, self.controller)
        self.main_frame.grid(row=0, column=0, sticky=N+E+W)
        
    def view_rows_columns_configure(self):
        # Rows confiure
        self.rowconfigure(0, weight=1)

        # Colums configure
        self.columnconfigure(0, weight=1)
        
    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                print(msg)
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass
        
class MAIN_FRAME(ttk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_style()

        self.topic = StringVar()
        self.message = StringVar()
        # self.password = StringVar()
        # self.token = StringVar()
        # self.slider_value = tk.DoubleVar()

        self.configure_rows_columns()
        self.setup_widgets()

    def configure_rows_columns(self):
        # Rows confiure (11)
        # weight = 0 means no responsive
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        # self.rowconfigure(6, weight=1)
        # self.rowconfigure(7, weight=1)
        # self.rowconfigure(8, weight=1)
        # self.rowconfigure(9, weight=1)
        # self.rowconfigure(10, weight=1)
        # self.rowconfigure(11, weight=1)

        # Colums configure (0)
        self.columnconfigure(0, weight=1)

    def setup_style(self):
        self.theme_style = ttk.Style()
        # self.theme_style.configure("Standard.TFrame", background="green")
        self.theme_style.configure(
            "Topic.TLabel", font=('Helvetica', 14, 'bold'))

    def setup_widgets(self):

        # TOPIC
        self.topic_label = ttk.Label(self, text="Topic:", style='Topic.TLabel')
        self.topic_label.grid(row=0, column=0, padx=5, pady=5, sticky=NSEW)
        self.topic_entry = ttk.Entry(self, textvariable=self.topic)
        self.topic_entry.grid(row=1, column=0, padx=5, pady=5, sticky=NSEW)
        self.topic_entry.focus()
        
        # start subcribe button
        self.start_subcribe_button = ttk.Button(
            self, text='Start Subcribe', command=self.controller.start_subcribe_button, state=NORMAL)
        self.start_subcribe_button.grid(
            row=2, column=0, padx=5, pady=5, sticky=NSEW)
        
        # stop subcribe button
        self.stop_subcribe_button = ttk.Button(
            self, text='Stop Subcribe', command=self.controller.stop_subcribe_button, state=DISABLED)
        self.stop_subcribe_button.grid(
            row=3, column=0, padx=5, pady=5, sticky=NSEW)
        
        # display content of message
        # self.treeview_content = ttk.Treeview(self)
        # self.treeview_content_heading = self.treeview_content.heading(
        #     "#0", text="Content", anchor='w')
        # self.treeview_content.column("#0", anchor=CENTER)
        # self.treeview_content.grid(
        #     row=4, column=0, sticky=NSEW, pady=5, padx=5)
        
        self.message_label = ttk.Label(self, text="Messsage:")
        self.message_label.grid(row=4, column=0, padx=5, pady=5, sticky=NSEW)
        self.message_content = ttk.Label(self, wraplength=240)
        self.message_content.grid(
            row=5, column=0, padx=5, pady=5, sticky=NSEW)

class CONTROLLER:

    def __init__(self):
        # Create the queue
        self.queue = queue.Queue()
        
        # Set up the GUI part
        self.view = VIEW(self, self.queue)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = True

    def start_app(self):
        self.view.init_display()

    # con.close()

    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        self.client = mqtt_client.Client(client_id)
        self.client.username_pw_set(username, password)
        self.client.on_connect = on_connect
        self.client.connect(broker, port)
        return self.client

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.view.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.view.after(200, self.periodicCall)
        
    def start_subcribe_button(self):
        # Create the queue
        self.queue = queue.Queue()
        
        client = self.connect_mqtt()
        
        # Create thread
        self.thread = threading.Thread(target=self.subscribe, args=[client])
        self.view.main_frame.start_subcribe_button['state'] = DISABLED
        self.view.main_frame.stop_subcribe_button['state'] = NORMAL
        self.thread.start()
        
        client.loop_start()
        
        self.stop_thread = False
        
        # Start the periodic call in the GUI to check if the queue contains anything
        self.periodicCall()
        
    def stop_subcribe_button(self):
        self.view.main_frame.start_subcribe_button['state'] = NORMAL
        self.view.main_frame.stop_subcribe_button['state'] = DISABLED
        self.client.disconnect(broker, port)
        print("Subscribing is stopped!")
        self.stop_thread = True
        self.thread.join()
        
    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received '{msg.payload.decode()}' from '{msg.topic}' topic")
            self.view.main_frame.message_content.configure(text=f"Received '{msg.payload.decode()}' from '{msg.topic}' topic")

        topic = self.view.main_frame.topic.get()
        client.subscribe(topic)
        client.on_message = on_message
        
def main():
    app = CONTROLLER()
    app.start_app()


if __name__ == "__main__":
    main()






