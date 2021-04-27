import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import colorchooser
import numpy as np
import cv2
import os 
import re
import serial
import sys
import glob
import serial
 

#global variables
is_ready=False
port_is_set=False
previosus_port=0
r_val_port = (0, 2)
g_val_port = (0, 1)
b_val_port = (0, 0)
data_frame = np.zeros((16 ,5), np.uint16)
driver_registers = 16
driver_number = 5

#setup of root window
root = tk.Tk()
root.title("PC TO STM32 USART COMMUNICATION")
root.resizable(False, False)
root.iconphoto(False, tk.PhotoImage(file="ICONS\ICON.png"))

#global variables for GUI usage
selected_port = StringVar()
selected_port.set("Select available port")
r_val = StringVar()
r_val.set("00000")
g_val = StringVar()
g_val.set("00000")
b_val = StringVar()
b_val.set("00000")
color_info_text = StringVar()
color_info_text.set("THIS IS EXPECTED COLOR")
connection_label_text = StringVar()
connection_label_text.set("Choose port from list above")
finished_frame = StringVar()
finished_frame.set("STATUS:\n\nFrame NOT ready to be sent!\n\nFirst you need to CREATE FRAME!")


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def get_serial_ports():
	""" Sets a expandable list of up ports

        :returns: nothing
    """
	up_ports=serial_ports()
	port_combobox["values"]=up_ports

def create_expected_color_img(bitmap_is_given=False, image_bitmap=0):
	""" Creates expected color image form given bitmap, if non is given creates black image
	    Keyword arguments:
		bitmap_is_given -- is and bitmap beeing given to this function
		image_bitmap -- image bitmap given to function
        :returns: nothing
    """

	if os.path.exists("ICONS\EXPECTED_COLOR.png"):
		os.remove("ICONS\EXPECTED_COLOR.png")
	if(bitmap_is_given==False):
		expected_color=np.zeros((400,400,3), np.uint16)
		cv2.imwrite("ICONS\EXPECTED_COLOR.png", expected_color)

	else:
		cv2.imwrite("ICONS\EXPECTED_COLOR.png", image_bitmap)
		expected_img.config(file="ICONS\EXPECTED_COLOR.png")


create_expected_color_img(False);


def check_num(newval):
	""" Checks if input in RGB value fields is valid

        :returns: nothing
    """
	return re.match('^[0-9]*$', newval) is not None and len(newval) <= 5 and newval <= "65535"

check_num_wrapper = (root.register(check_num), '%P')

def set_status(color_status=False, port_status=False):
	""" Sets status info for port and frame
	    Keyword arguments:
		color_status -- is color frame created (default False)
		port_status -- is port selected (default False)
        :returns: nothing
    """
	if(color_status and not port_status):
		finished_frame.set("STATUS:\n\nYou have to select port!")
		frame_indicator_img.config(file="ICONS\delete-icon.png")
		send_frame_button.config(bg = "DimGray")
		return
	elif(port_status and not color_status or not port_status and not color_status):
		return
	else:
		finished_frame.set("STATUS:\n\nFrame READY to be sent!")
		frame_indicator_img.config(file="ICONS\sign-check-icon.png")
		send_frame_button.config(bg = "#263D42")
	

def create_color():
	""" Creates data frame and background color

    :returns: nothing
	:invokes: set_status()
	
    """
	global is_ready, port_is_set

	expected_color=np.zeros((400,400,3), np.uint16)
	for i in range (0, 400):
		for j in range (0, 400):
			expected_color[i,j,2]=int(r_val.get())
			expected_color[i,j,1]=int(g_val.get())
			expected_color[i,j,0]=int(b_val.get())

	create_expected_color_img(True, expected_color);
	is_ready=True
	set_status(is_ready, port_is_set)
	data_frame[r_val_port]=int(r_val.get())
	data_frame[g_val_port]=int(g_val.get())
	data_frame[b_val_port]=int(b_val.get())
	print("Data frame:\n\n{}".format(data_frame))


def disconnect_from_stm():
	ports=serial_ports()
	for port in ports:
		try:
			ser = serial.Serial(port, baudrate=115200, timeout = 0.1, write_timeout = 0.1)  # open serial port
			print("Disconnecting from port: {}".format(ser.name))       # check which port was really used
			ser.write(b'2')     # write a string
			ser.close() 
			port_is_set = False
		except serial.SerialTimeoutException:
			ser.close() 
			port_is_set = False
			pass


def	check_if_connected(port):
	global port_is_set, is_ready, previosus_port

	if(previosus_port==selected_port.get() and port_is_set):
		return

	disconnect_from_stm()

	try:
		previosus_port = selected_port.get()
		ser = serial.Serial(port=selected_port.get(), baudrate=115200, timeout = 0.1, write_timeout = 0.1)  # open serial port
		print("Connecting to port: {}".format(ser.name))       # check which port was really used
		ser.write(b'1')     # write a string
		read_msg=ser.read(size=1)
		print("Connecting response: {}".format(read_msg))
		if(read_msg==b'1'):
			connection_label_text.set("PORT STATUS:\n\nConnected with STM32 on port {}.".format(selected_port.get()))
			ser.close()           # close port
			port_is_set = True
			set_status(is_ready, port_is_set)

			return
		else:
			connection_label_text.set("PORT STATUS:\n\nNo or invalid response on this port!")
			port_is_set = False
			set_status(is_ready, port_is_set)
	except serial.SerialTimeoutException:
		ser.close()           # close port
		connection_label_text.set("PORT STATUS:\n\nWrite timeout!")
		port_is_set = False
		set_status(is_ready, port_is_set)
	pass

def send_test():
	""" Sends frame via selected port

    :returns: nothing
	
    """
	global port_is_set, is_ready, driver_registers, driver_number

	if(is_ready and port_is_set):
		try:
			ser = serial.Serial(port=selected_port.get(), baudrate=115200, timeout=1)  # open serial port
			print("Sending to port: {}".format(ser.name))       # check which port was really used

			ser.write(b'3')
			send_response = ser.read(size=1)
			print("Send response: {}".format(send_response))
			if(send_response==b'3'):
				send_buffer=""
				reci_buffer=""

				root.after(1)

				for driver_register in range(16):
					for driver in range(5):
						send_buffer = send_buffer + '{:0>4}'.format(hex(data_frame[driver_register, driver])[2:])

				encoded_send_buffer = send_buffer.encode('utf-8')
			
				print("SEND BUFFER: {}".format(send_buffer))

				print("Number of bytes sent: {}".format((ser.write(encoded_send_buffer))))

				reci_buffer=ser.read(size=320)
				print("RECI BUFFER: {}".format(reci_buffer.decode('utf-8')))

				finished_frame.set("STATUS:\n\nFrame has been sent!")
				ser.close()           # close port
				frame_indicator_img.config(file="ICONS\green-mail-send-icon.png")
		except:
			finished_frame.set("STATUS:\n\nFrame has been sent!\n\nFEEDBACK: \n\nNo response on this port.")
			pass

def choose_color():
	""" Opens color wizard and converts to 16 bit img

    :executes: create_color()
	
    """
	choosen_color=[0,0,0]
	read_rgb=["00000", "00000", "00000"]
	choosen_color_tup = tk.colorchooser.askcolor()[0]
	
	try:
		for i in range(0,3):
			choosen_color[i]=int(choosen_color_tup[i])

		for i in range (0,3):
			read_rgb[i] = str(int((choosen_color[i]*257)))
			if(len(read_rgb[i])<5):
				j=5-len(read_rgb[i])
				read_rgb[i] = j*"0"+read_rgb[i]

		r_val.set(read_rgb[0])
		g_val.set(read_rgb[1])
		b_val.set(read_rgb[2])
		
		create_color()
	except:
		pass


############################################################
################## APP CONTENT CONFIFURATION ###############
############################################################


content = tk.Frame(root,padx = 10, pady = 10,)

frame  = tk.Canvas(content, borderwidth = 5, relief = "ridge", width = 400, height = 400)

expected_img = tk.PhotoImage(file="ICONS\EXPECTED_COLOR.png")
frame.create_image(8, 8, image=expected_img, anchor='nw')

frame_indicator_img = tk.PhotoImage(file="ICONS\delete-icon.png")

frame_status_image = tk.Label(content, image=frame_indicator_img)
frame_status_text = tk.Label(content, textvariable = finished_frame)

color_info = tk.Label(content, textvariable = color_info_text)

port_combobox_label = tk.Label(content, text="PORT SELECTED FOR \nCOMMUNICATION WITH STM32")

port_combobox = ttk.Combobox(content, textvariable=selected_port, postcommand=get_serial_ports, state="readonly")
port_combobox.bind("<<ComboboxSelected>>", check_if_connected)

r_entry = tk.Entry(content, textvariable=r_val, validate='key', validatecommand=check_num_wrapper)
r_label = tk.Label(content, text='RED LED PWM FILL\n00000-65535:')

g_entry = tk.Entry(content, textvariable=g_val, validate='key', validatecommand=check_num_wrapper)
g_label = tk.Label(content, text='GREEN LED PWM FILL\n00000-65535:')

b_entry = tk.Entry(content, textvariable=b_val, validate='key', validatecommand=check_num_wrapper)
b_label = tk.Label(content, text='BLUE LED PWM FILL\n00000-65535:')

connection_label = tk.Label(content, textvariable=connection_label_text)

save_frame_button = tk.Button(content, text = "CREATE FRAME", padx = 10,
				   pady = 5, fg="white", bg = "#263D42", command=create_color)
send_frame_button = tk.Button(content, text = "SEND FRAME", padx = 10,
				   pady = 5, fg="white", bg = "DimGray", command=send_test)
choose_color_button = tk.Button(content, text = "CHOOSE COLOR and CREATE FRAME", padx = 20,
				   pady = 5, fg="white", bg = "#263D42", command=choose_color)


############################################################
################## APP GRID CONFIFURATION ##################
############################################################

content.grid(column=0, row=0, sticky=(N, S, E, W))
frame.grid(column=0, row=0, columnspan=3, rowspan=4, sticky="n")
color_info.grid(column=0, row=0, columnspan=3, rowspan=4)

frame_status_text.grid(column=3, row=2, columnspan=2, sticky="n", pady = (0,20))

frame_status_image.grid(column=3, row=3, columnspan=2, rowspan=2, pady = (0,0))

r_label.grid(column=0, row=4, pady = (5,0))
g_label.grid(column=1, row=4, pady = (5,0))
b_label.grid(column=2, row=4, pady = (5,0))
connection_label.grid(column=3, row=0, columnspan=3, rowspan=2)

r_entry.grid(column=0, row=5)
g_entry.grid(column=1, row=5)
b_entry.grid(column=2, row=5)

save_frame_button.grid(column=3, row=6, padx = 5, pady = (10 ,0))
send_frame_button.grid(column=4, row=6, padx = 5, pady = (10 ,0))
choose_color_button.grid(column=0, row=6, columnspan=3, pady = (10 ,0))

port_combobox_label.grid(column=3, row=0, columnspan=2, sticky="n")
port_combobox.grid(column=3, row=1, columnspan=2, sticky="n")

content.rowconfigure(1, weight=1)
#end of main loop of GUI
root.mainloop()
