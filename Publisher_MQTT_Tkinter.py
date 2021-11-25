import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter.messagebox import showinfo
from paho.mqtt import client as mqtt_client
import random
import time
import psycopg2
import queue
import threading
# import json


# connect to the db
# con = psycopg2.connect(
#     database="postgredatabase",
#     user="",
#     password="")

# # cursor
# cur = con.cursor()

# # execute query

# create_table = """
#     CREATE TABLE IF NOT EXISTS customer (
#         User_id serial PRIMARY KEY,
#         Name VARCHAR ( 50 ) NOT NULL,
#         Age serial NOT NULL,
#         Address VARCHAR ( 150 ) NOT NULL,
#         Gender VARCHAR ( 8 ) NOT NULL,
#         Email VARCHAR ( 255 ) UNIQUE NOT NULL,
#         Phone_number VARCHAR( 10 ) UNIQUE NOT NULL,
#         Username VARCHAR ( 50 ) UNIQUE NOT NULL,
#         Password VARCHAR ( 50 ) NOT NULL
#     );"""

# cur.execute(create_table)

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

        self.title("Publisher")
        # self.minsize(600, 768)
        self.geometry("250x500")
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

        self.id = StringVar()
        self.password = StringVar()
        self.token = StringVar()
        self.slider_value = tk.DoubleVar()
        self.topic = StringVar()

        self.configure_rows_columns()
        self.setup_widgets()

    def setup_style(self):
        self.theme_style = ttk.Style()
        # self.theme_style.configure("Standard.TFrame", background="green")
        self.theme_style.configure(
            "Topic.TLabel", font=('Helvetica', 14, 'bold'))

    def configure_rows_columns(self):
        # Rows confiure (13)
        # weight = 0 means no responsive
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=1)
        self.rowconfigure(7, weight=1)
        self.rowconfigure(8, weight=1)
        self.rowconfigure(9, weight=1)
        self.rowconfigure(10, weight=1)
        self.rowconfigure(11, weight=1)
        self.rowconfigure(12, weight=1)
        self.rowconfigure(13, weight=1)

        # Colums configure (0)
        self.columnconfigure(0, weight=1)

    def setup_widgets(self):

        # TOPIC
        self.topic_label = ttk.Label(self, text="TOPIC:", style='Topic.TLabel')
        self.topic_label.grid(row=0, column=0, padx=5, pady=5, sticky=NSEW)
        self.topic_entry = ttk.Entry(self, textvariable=self.topic)
        self.topic_entry.grid(row=1, column=0, padx=5, pady=5, sticky=NSEW)
        self.topic_entry.focus()

        # name
        self.id_label = ttk.Label(self, text="ID:")
        self.id_label.grid(row=2, column=0, padx=5, pady=5, sticky=NSEW)
        self.id_entry = ttk.Entry(self, textvariable=self.id)
        self.id_entry.grid(row=3, column=0, padx=5, pady=5, sticky=NSEW)
        # name_entry.focus()

        # password
        self.password_label = ttk.Label(self, text="Password:")
        self.password_label.grid(row=4, column=0, padx=5, pady=5, sticky=NSEW)
        self.password_entry = ttk.Entry(
            self, textvariable=self.password, show="*")
        self.password_entry.grid(row=5, column=0, padx=5, pady=5, sticky=NSEW)

        # token
        self.token_label = ttk.Label(self, text="Token:")
        self.token_label.grid(row=6, column=0, padx=5, pady=5, sticky=NSEW)
        self.token_entry = ttk.Entry(self, textvariable=self.token)
        self.token_entry.grid(row=7, column=0, padx=5, pady=5, sticky=NSEW)

        # slider
        self.slider_label = ttk.Label(self, text="Slider:")
        self.slider_label.grid(row=8, column=0, padx=5, pady=5, sticky=NSEW)
        self.slider = ttk.Scale(self, from_=0, to=100, orient='horizontal',
                                variable=self.slider_value, command=lambda x: self.slider_value.set('%.2f' % float(x)))
        self.slider.grid(row=9, column=0, padx=5, pady=5, sticky=NSEW)
        self.slider_value.set('0.00')

        # button_1 button
        self.button_1 = ttk.Button(self, text='Button 1', command=None)
        self.button_1.grid(row=10, column=0, padx=5, pady=5, sticky=NSEW)

        # button_2 button
        self.button_2 = ttk.Button(self, text='Button 2', command=None)
        self.button_2.grid(row=11, column=0, padx=5, pady=5, sticky=NSEW)

        # start publish button
        self.start_publish_button = ttk.Button(
            self, text='Start Publish', command=self.controller.start_publish_button, state=NORMAL)
        self.start_publish_button.grid(
            row=12, column=0, padx=5, pady=5, sticky=NSEW)

        # stop publish button
        self.stop_publish_button = ttk.Button(
            self, text='Stop Publish', command=self.controller.stop_pulish_button, state=DISABLED)
        self.stop_publish_button.grid(
            row=13, column=0, padx=5, pady=5, sticky=NSEW)


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

    def connect_mqtt(self):
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

    def start_publish_button(self):
        # Create the queue
        self.queue = queue.Queue()

        # Create thread
        self.thread = threading.Thread(target=self.publish)
        self.view.main_frame.start_publish_button['state'] = DISABLED
        self.view.main_frame.stop_publish_button['state'] = NORMAL
        client = self.connect_mqtt()
        client.loop_start()
        self.thread.start()

        self.stop_thread = False

        # Start the periodic call in the GUI to check if the queue contains anything
        self.periodicCall()

    def stop_pulish_button(self):
        self.view.main_frame.start_publish_button['state'] = NORMAL
        self.view.main_frame.stop_publish_button['state'] = DISABLED
        self.client.disconnect(broker, port)
        print("Publishing is stopped!")
        self.stop_thread = True
        self.thread.join()

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

    def pre_process_data(self):
        msg = {}
        msg['id'] = self.view.main_frame.id.get()
        msg['password'] = self.view.main_frame.password.get()
        msg['token'] = self.view.main_frame.token.get()
        msg['slider_value'] = self.view.main_frame.slider_value.get()
        msg = str(msg)
        return msg

    def publish(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        msg_count = 0
        msg = self.pre_process_data()
        topic = self.view.main_frame.topic.get()
        # print('Thread 1 is running')
        # print(type(msg))
        # self.id = StringVar()
        # self.password = StringVar()
        # self.token = StringVar()
        # self.slider_value = tk.DoubleVar()
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following two lines with the real
            # thing.
            time.sleep(1)
            result = self.client.publish(topic, msg)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send '{msg}'' to topic '{topic}'")
            else:
                print(f"Failed to send message to topic '{topic}'")
            msg_count += 1
            if self.stop_thread:
                break


def main():
    app = CONTROLLER()
    app.start_app()


if __name__ == "__main__":
    main()
