import serial
import time
import pylab
import crc8
import numpy
import scipy
import matplotlib.pyplot as plt
from scipy import interpolate

# Read file
def readFile(i): 
	file = open('../../data/'+ str(i) +'.txt', 'r')
	say = []
	col_list = []
	for line in file:
		say = line.split(' ')
		if len(say) == 3:
			if len(say)>0:
				col_list.append(say[0])
				col_list.append(say[1])
	file.close()
	return col_list

# Build graph
def build_graph():
	print ("\n" + "-------------------------") 
	print ("write number file")
	file_number = raw_input()
	numberPin = int(file_number)
	col_list = readFile(file_number)
	xlist = []
	ylist = []
	xlistNew = []
	ylistNew = []
	i=0
	while i<len(col_list):
		xlist.append(float(col_list[i]))
		i=i+2
	i=1
	while i<len(col_list):
		ylist.append(float(col_list[i]))
		i=i+2
	plt.axis([minElement(xlist)-10, maxElement(xlist)+10, minElement(ylist)-200, maxElement(ylist)+200])
	plt.plot(xlist, ylist, color = 'blue')
	plt.plot([-55, 125], [2927, 47], color = 'red')
	plt.show()
	pass

# READ FILE SET.TXT AND FORM LIST COEF
#not optimized!!
def read_file_in_coef(ser):
	print("Enter number file = ")
	port_number = give_number_port(ser)
	#port_number = input()
	file = open('../../data/set.txt', 'r')
	list_coef_k_b_m = []
	flag = False
	for line in file:
		if flag == False:
			if line==('PIN = '+ str(port_number)+ '\n'):
				flag = True
		else:
			if "-------" in line:
				flag = False
				continue
			line = line.replace('\n','')
			status = line.split(" ")
			test_status = []
			for i in status:
				test_status.append(float(i))
			list_coef_k_b_m.append(test_status)
	file.close()		
	return list_coef_k_b_m
	
# Write K, B and M in one chip. Arduino 22 pin.
#not optimized!!
def write_coef_k_b_m_in_one_chip(ser, port):
	coefB = []
	coefK = []
	y_new_list = []
	full_coef_in_number_port = []
	
	full_coef_in_number_port = read_file_in_coef(ser)
	print(full_coef_in_number_port[0])
	print(full_coef_in_number_port[1])
	print(full_coef_in_number_port[2])
	y_new_list = full_coef_in_number_port[0]
	coefK = full_coef_in_number_port[1]
	coefB = full_coef_in_number_port[2]

	print ("\n" + "BINARY BLOCK")
	#
	#block sending data
	#
	binCodeCorfB = []
	binCodeCorfK = []
	binCodeCorfM = []
	for i in range(1,7):
		binCodeEleM = [0,0,0,0,0,0,0,0,0,0,0,0]
		x = int(y_new_list[i])
		i=0
		while i<12:
			y = str(x % 2)
			binCodeEleM[i] = int(y)
			i=i+1
			x = int(x / 2)
		coefmm = ""
		for i in binCodeEleM:
			coefmm = coefmm + str(i)
			binCodeCorfM.append(i)		
		print ("m = " + coefmm)
	for ele in coefB:
		x = int(ele)
		binCodeEleB=[0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		i=0
		if ele<0:
			binCodeEleB[13] = 1
			x = x*(-1)
		else:
			binCodeEleB[13] = 0
		n = ""
		while x > 0:
			y = str(x % 2)
			if i<13:
				binCodeEleB[i] = int(y)
				i=i+1
			else:
				break
			x = int(x / 2)
		coefbb = ""
		for z in binCodeEleB:
			binCodeCorfB.append(z)
			coefbb = coefbb + str(z)
		print ("b = " + coefbb)
	for ele in coefK:
		x = float(ele)
		binCodeEleK=[0,0,0,0,0,0,0,0,0,0,0,0,0]
		intX = int(x)
		i = 10
		while i < 13:
			y = str(intX % 2)
			binCodeEleK[i] = int(y)
			i=i+1
			intX = int(intX / 2)
		intY = float(ele) - int(ele)
		i=9
		while i>=0:
			z = intY * 2
			binCodeEleK[i] = int(z)
			intY = float(z) - int(z)
			i=i-1
		coefkk = ""
		for ele in binCodeEleK:
			coefkk = coefkk + str(ele)
			binCodeCorfK.append(ele)
		print ("k = " + coefkk)
	step = 0
	stepK = 0
	stepB = 0
	stepM = 0
	pacet = []
	while step<6:
		text = ""
		for i in range(stepK, stepK+13):
			pacet.append(binCodeCorfK[i])
		stepK = stepK + 13
		for i in range(stepB, stepB+14):
			pacet.append(binCodeCorfB[i])
		stepB = stepB + 14
		for i in range(stepM, stepM+12):
			pacet.append(binCodeCorfM[i])
		stepM = stepM + 12
		step = step + 1
	for i in range(stepK, stepK+13):
		pacet.append(binCodeCorfK[i])
		stepK = stepK + 13
	for i in range(stepB, stepB+14):
		pacet.append(binCodeCorfB[i])
		stepB = stepB + 14
	text = ""
	iterat = 0
	win_test = []
	for i in range(258):
		if iterat < 8:
			text = text + str(pacet[i])
			iterat +=1
		else:
			not_Invers = list(text)
			nul = 7
			invers = ""
			for j in range(8):
				invers = invers + not_Invers[nul]
				nul-=1
			win_test.append(chr(int(invers,2)))
			test =  hex(int(invers,2))
			text = ""
			text = text + str(pacet[i])
			iterat =1
	text = ""
	for i in range (256, 261):
		text = text + str(pacet[i])
	not_Invers = list(text)
	nul = 4
	invers = ""
	for j in range(5):
		invers = invers + not_Invers[nul]
		nul-=1
	win_test.append(chr(int(invers,2)))
	test =  hex(int(invers,2))
	print ("-------------------------" + "\n")

	ser.write('1')	
	ser.write('1')	
	number_p = chr(int(port) - 22)
	ser.write(number_p)	
	for i in win_test:
		ser.write(i)
	print("Please wait 4 seconds. " + '\n')
	time.sleep(4)

	print("Apply high voltage to write coefficients.")
	print('\n' + "Check temperature?" + '\n' + "1 - Yes;" + '\n' + "2 - No")
	command_Set_ENTER = input()
	if command_Set_ENTER == 1: 
		check_Temperature(ser, port)
	pass
	
# WRITE FILE TEMPERATURE
#not optimized!!
def writeFile(ser):
	temperature = input()
	ser.write('3')
	time.sleep(4)
	ser.write('0')
	time.sleep(8)
	colBits = []
	lineBinary = ser.readlines()
	if len(lineBinary) != 32:
		print ("What the chip not works!!!")
		pass
	port_arduino = 22
	for elem in lineBinary:
		elem = elem[:16]
		number = elem[4:len(elem)]
		fileText = open('../../data/'+str(port_arduino)+'.txt', 'a')
		fileText.write(str(temperature) + " " + str(int(number,2)) + " " + str(elem) + '\n')
		fileText.close()
		port_arduino += 1
	write_File_All_In_One_File()
	pass

# Check chip REZ, read temperature code.	
def check_REZ(ser, number_file, flag):
	ser.write('3')
	time.sleep(4)
	ser.write('0')
	time.sleep(4)
	number_file = int(number_file-22)
	lineBinary = ser.readlines()
	list_check_rez = list(lineBinary[number_file])
	list_check_rez.remove('\r')
	list_check_rez.remove('\n')
	if flag == True:
		if int(list_check_rez[5])==1:
			print ("\n" + "-------------------------") 
			print("Setup REZ was successful.")
		else:
			print ("\n" + "-------------------------") 
			print("Setup REZ was not successful.")
	print("Received code = " + str(list_check_rez))
	print ("-------------------------" + "\n")
	pass

# Write address
def write_adres(ser, pin):
	print ("\n" + "-------------------------") 
	print ("MENU ADDRESS:")
	print ("1 - BMK_GEN (0x28);" + "\n" + "2 - BMK_DIODS (0x29);" + "\n" + "3 - CUSTOM_GEN (0x06);" + "\n" + "4 - CUSTOM_DIODS (0x07)" + "\n" + "5 - TEST_SAMPLE (0xAD)" + "\n" + "6 - EXIT") 
	print ("-------------------------" + "\n")
	number_family = input()
	crc1 = ""
	bin_name = -1
	pin = pin-22
	if number_family == 1:
		print ("Enter the type of party chips (4-bit):")
		type_of_party = raw_input()
		print ("\n" + "RESULT")
		bin_name = form_ADDRESS_SN(0)
		crc1 = write_CRC(0, pin, type_of_party)
		fileText = open('c:/micros/listing_address/BMK_GEN.list', 'a')
		fileText.write("40" + " " + str(type_of_party) + " " + str(bin_name) + " " + str(crc1) + "\n")
		print ("-------------------------" + "\n")
		fileText.close()
	elif number_family == 2:
		print ("Enter the type of party chips (4-bit):")
		type_of_party = raw_input()
		print ("\n" + "RESULT")
		bin_name = form_ADDRESS_SN(1)
		crc1 = write_CRC(1, pin, type_of_party)
		fileText = open('c:/micros/listing_address/BMK_DIODS.list', 'a')
		fileText.write("41" + " " + type_of_party + " " + str(bin_name) + " " + str(crc1) + "\n")
		print ("-------------------------" + "\n")
		fileText.close()
	elif number_family == 3:
		print ("Enter the type of party chips (4-bit):")
		type_of_party = raw_input()
		print ("\n" + "RESULT")
		bin_name = form_ADDRESS_SN(2)
		crc1 = write_CRC(2, pin, type_of_party)
		fileText = open('c:/micros/listing_address/CUSTOM_GEN.list', 'a')
		fileText.write("6" + " " + type_of_party + " " + str(bin_name) + " " + str(crc1) + "\n")
		print ("-------------------------" + "\n")
		fileText.close()
	elif number_family == 4:
		print ("Enter the type of party chips (4-bit):")
		print ("\n" + "RESULT")
		type_of_party = raw_input()
		bin_name = form_ADDRESS_SN(3)
		crc1 = write_CRC(3, pin, type_of_party)
		fileText = open('c:/micros/listing_address/CUSTOM_DIODS.list', 'a')
		fileText.write("7" + " " + type_of_party + " " + str(bin_name) + " " + str(crc1) + "\n")
		print ("-------------------------" + "\n")
		fileText.close()
	elif number_family == 5:
		print ("Enter the type of party chips (4-bit):")
		type_of_party = raw_input()
		print ("\n" + "RESULT")
		bin_name = form_ADDRESS_SN(4)
		crc1 = write_CRC(4, pin, type_of_party)
		fileText = open('c:/micros/listing_address/TEST_SAMPLE.list', 'a')
		fileText.write("173" + " " + type_of_party + " " + str(bin_name) + " " + str(crc1) + "\n")
		print ("-------------------------" + "\n")
		fileText.close()
	elif number_family == 6:
		return
	else:
		print ("incorrect value entered")
		write_adres(ser, pin)
	pass

# This block need write address.
def form_ADDRESS_SN(number_file):
	bin_name = 0
	address = []
	name_file = ["BMK_GEN","BMK_DIODS","CUSTOM_GEN","CUSTOM_DIODS","TEST_SAMPLE"]
	fileText = open('c:/micros/listing_address/'+name_file[number_file]+'.list', 'r')
	all_lines = fileText.readlines()
	fileText.close()
	if len(all_lines) == 0:
		return bin_name
	else:
		last_line = all_lines[-1].split(" ")
		bin_name = int(last_line[2])+1
	return bin_name

# This block need write address.
def write_CRC(number_file, pin, type_of_party):
	crc = [0,0,0,0,0,0,0,0]
	ishod = ""
	code = []
	FAM = []
	SN = []
	PARTY = []
	for i in range(56):
		code.append(0)
	name_file = ["BMK_GEN","BMK_DIODS","CUSTOM_GEN","CUSTOM_DIODS","TEST_SAMPLE"]
	colection_DEC_code_in_File = [40,41,6,7,173]
	fileText = open('c:/micros/listing_address/'+name_file[number_file]+'.list', 'r')
	all_lines = fileText.readlines()
	fileText.close()
	if len(all_lines) == 0:
		FAM = list(bin(int(colection_DEC_code_in_File[number_file])))
		SN = list(bin(int(0)))
		PARTY = list(type_of_party)
	else:
		last_line = all_lines[-1].split(" ")
		FAM = list(bin(int(colection_DEC_code_in_File[number_file])))
		SN = list(bin(int(last_line[2])+1))
		PARTY = list(type_of_party)
	pacet_address_str = ""
	pacet_address = 0;
	number_bit = -1
	x = -1
	number_bit = 7 + 2 #0 and 1 bit ("0b") 7+2
	one = ""
	for i in range(2, len(FAM)):
		code[number_bit - i] = int(FAM[int(len(FAM))+1-i])
		one = one + str(code[number_bit - i])
	number_bit = 11
	for i in range(4):
		code[number_bit - i] = int(PARTY[3-i])
		one = one + str(code[number_bit - i])
	number_bit = 55 + 2
	one = one + " "
	for i in range(2, len(SN)):
		code[number_bit - i] = int(SN[int(len(SN))+1-i])
		one = one + str(code[number_bit - i])
	one = one + " "
	step_i = [7,15,23,31,39,47,55]
	flag = True
	for i in step_i:
		number_i = i
		for j in range(8):
			one = one + str(code[number_i-j])
			if crc[0]==code[number_i-j]:
				x = 0
			else:
				x = 1
			crc[0] = crc[1]
			crc[1] = crc[2]
			if crc[3]==x:
				crc[2] = 0
			else: 
				crc[2] = 1
			if crc[4]==x:
				crc[3] = 0
			else:
				crc[3] = 1
			crc[4] = crc[5]
			crc[5] = crc[6]
			crc[6] = crc[7]
			crc[7] = x	
	for i in crc:
		pacet_address_str = pacet_address_str + str(i)
		ishod = ishod + str(i)
	for i in range(56):
		pacet_address_str = pacet_address_str + str(code[55-i])
	iterator = 0
	pacet_list = list(pacet_address_str)
	pacet = ""
	full_pacet_chr = []
	col_pacet_data = 0
	number_element_list = 62
	pacet = pacet + str(pacet_list[63])
	while True:
		iterator = iterator + 1
		if iterator>7:
			pacet_address = chr(int(pacet,2))
			full_pacet_chr.append(pacet_address)
			col_pacet_data = col_pacet_data + 1
			print (pacet)
			if col_pacet_data == 8:
				break
			pacet = ""
			iterator=0
			pacet = pacet + str(pacet_list[number_element_list])
			number_element_list =number_element_list-1
		else:
			pacet = pacet + str(pacet_list[number_element_list])
			number_element_list =number_element_list-1
	ser.write('4')
	ser.write(chr(pin))
	for i in range(len(full_pacet_chr)):
		ser.write(full_pacet_chr[i])
	time.sleep(5)
	return ishod

# Check address.
def check_CRC8(ser, port):
	ser.write('5')
	pin = chr(int(port) - 22)
	ser.write(pin)
	time.sleep(2)
	line = ser.readlines()
	result = int(line[0])
	if result == 1:
		print ("crc8 - true")
	elif result ==0:
		print("crc8 - false")
	#print ("FAM = " + str(line[1]))
	full_address = "\n" + " "
	for i in range(1,9):
		full_address = full_address + line[i] + " "
	print ("Full address = " + full_address)
	pass

# Initial setup of the chip
def initial_setup_of_the_chip(ser):
	print("Enter port number in arduino.")
	arduino_port = input()
	print ("\n" + "-------------------------") 
	flag = False
	print ("\n"+"Place wait")
	check_REZ(ser, arduino_port, flag)
	print("To configure REZ?"+ "\n" + "1 - Yes;" + "\n" + "2 - No;" + "\n" + "3 - Exit")
	print ("\n"+"-------------------------" + "\n")
	commands_control = input()
	if commands_control == 1:
		ser.write('3')
		time.sleep(4)		
		ser.write('2')
		time.sleep(1)
	elif commands_control == 3:
		return
	print ("\n" + "-------------------------") 
	print("\n" + "Apply high voltage to write REZ.")
	print("\n" + "Check REZ?" + "\n" + "1 - Yes;" + "\n" + "2 - No;" + "\n" + "3 - Exit")
	print ("-------------------------" + "\n")
	commands_control = input()
	if commands_control == 1:
		flag = True
		check_REZ(ser, arduino_port, flag)
	elif commands_control==3:
		return
	print ("\n" + "-------------------------") 
	print("Write address?" + "\n" + "1 - Yes;" + "\n" + "2 - No;" + "\n" + "3 - Exit")
	print ("-------------------------" + "\n")
	commands_control = input()
	if commands_control == 1:
		write_adres(ser, arduino_port)
	elif commands_control == 3:
		return
	print ("\n" + "-------------------------") 
	print("\n" + "Apply high voltage to write ADDERSS.")
	print("\n" + "Check address?" + "\n" + "1 - Yes;" + "\n" + "2 - No.")
	print ("-------------------------" + "\n")
	commands_control = input()
	if commands_control==1:
		check_CRC8(ser, arduino_port)
	
	pass

# Form file all data
def write_File_All_In_One_File():
	list = []
	for i in range(22, 54):
		list.append(readFile(i))

	fileText = open('../../data/All.txt', 'w')
	fileText.write(" -- | ")
	test = list[0]
	i=0
	while True:
		if (i>=len(test)):
			fileText.write('\n')
			break
		fileText.write(str(test[i]) + " | ")
		i=i+2
	k=0
	for i in range(22, 54):
		fileText.write(" " + str(i) + " |  ")
		test = list[k]
		k=k+1
		j=1
		while True:
			if (j>=len(test)):
				fileText.write('\n')
				break
			if (int(float(test[j])/1000)==0):
				fileText.write(" ")
			fileText.write(str(test[j]) + " |  ")
			j=j+2
	fileText.close()
	pass

	
# Gived 2 byte and * 0.0625
# print temperature
def check_Temperature(ser, port):
	pin = chr(int(port) - 22)
	ser.write('6')
	ser.write(pin)
	time.sleep(4)
	print(ser.readlines())	
	pass

# Main read address and form file in all adderss on chip
def main_read_address_and_form_file_in_all_adderss_on_chip(ser):
	fileText = open('../../data/All_address.txt', 'w')
	fileText.close()
	time.sleep(2)
	for port in range(22,54):
		address_str = ""
		address_str = check_address(ser, port)
		read_address_on_all_chip_and_write_file(port, address_str)
	pass
	
# This block need write main_read_address_and_form_file_in_all_adderss_on_chip.
def read_address_on_all_chip_and_write_file(port, address):
	fileText = open('../../data/All_address.txt', 'a')
	address_pin = str(port) + "|" + address
	fileText.write(address_pin + '\n')
	print(address_pin)
	fileText.close()
	pass

# Check address in chip and return "173_16_0_0_0_0_9_135".
def check_address(ser, number_pin_arduino):
	ser.write('5')
	pin = chr(int(number_pin_arduino) - 22)
	ser.write(pin)
	time.sleep(2)
	line = ser.readlines()
	#print(line)
	full_address = []
	if len(line) == 9:
		for i in range(1,9):
			address = str(line[i])
			full_address.append(address[0:len(address)-2])
	address_str_list = '_'.join(full_address)
	return address_str_list

#
def give_number_port(ser):
	port = 22
	file = -1
	address = check_address(ser, port)
	fileText = open('../../data/All_address.txt', 'r')
	for line in fileText:
		port_and_address = line.split("|")
		address_in_file = port_and_address[1]
		print(address_in_file[:len(address_in_file)-1] + " __ " + address)
		if address_in_file[:len(address_in_file)-1] == address:
			file = int(port_and_address[0])
			break
	fileText.close()
	print(file)
	return file
	
	
# MAIN FUNCTION
print ("Enter the number?" + "\n" + "1 - Yes;" +"\n" + "2 - No (use COM6)")	
commands_control = input()
if commands_control == 1:
	print ("Enter the number port")	
	number_COM_port = input()
else:
	number_COM_port = 6
ser = serial.Serial('COM' + str(number_COM_port), 9600, timeout=0)
ser.close()
ser.open()
ser.isOpen()
flag=True
col_list = []
print ("\n" + "-------------------------")
print ("menu commands:" + "\n" + "1 - measure temperature and write to file;" + "\n" + "2 - calculate the coefficients; 22 arduino port" + "\n" + "3 - function REZ")
print ("4 - set address;" + "\n" + "5 - build a graph;" + "\n" + "6 - check REZ and CRC8;" + "\n" + "7 - Initial setup of the chip;" + "\n" + 
"8 - Form File;" + "\n" + "9 - Check temperature;" + "\n" + "10 - Form file in all address on chip;" + "\n" + "0 - exit;")
print ("-------------------------" + "\n")
while True:
	print ("enter the commands ")
	commands = str(input())
	if commands=="1":
		print("\n"+"enter the temperature ")
		writeFile(ser)
		break
	elif commands == "2":
		while True:
			print ("\n"+ "-------------------------")
			print ("\n"+"1 - working with 1 chip;" + "\n" + "2 - exit.")
			print ("-------------------------" + "\n")
			set = input()
			if set == 1:
				print ("enter the arduino port - 22")
				#Need?
				port_arduino="22"
				#port_arduino=raw_input()
				flag_switch = True
				write_coef_k_b_m_in_one_chip(ser, port_arduino);
				break
			elif set == 2:
				break
			else:
				print (" Incorrect command! ")
		
		break
	elif commands == "3":
		flag = False
		print ("write number pin:")
		number_file = input()
		print ("\n"+"Place wait there is a check REZ")
		check_REZ(ser, number_file, flag)
		print ("\n" + "To set up?" + "\n" + "1 - Yes;" + "\n" + "2 - No.")
		commands_REZ = input()
		if commands_REZ == 1:
			ser.write('3')
			time.sleep(4)		
			ser.write('2')
			time.sleep(2)
			#Used Yokogawa?
		else:
			break
		print ("\n" + "Check the result?" + "\n" + "1 - Yes;" + "\n" + "2 - No.")
		commands_REZ = input()
		if commands_REZ == 1:
			check_REZ(ser, number_file, flag)
		break
	elif commands == "4":
		print ("write number pin:")
		pin = input()
		write_adres(ser, pin)
		break
	elif commands == "5":
		build_graph()
		break
	elif commands == "6":
		commands_check = 0;
		print ("\n" + "-------------------------")
		print ("1 - check CRC8;" + "\n" + "2 - check REZ;" + "\n" + "3 - exit.")
		print ("-------------------------" + "\n")
		commands_check = input()
		print ("enter the arduino port:")
		arduino_port = input()
		if commands_check==1:
			check_CRC8(ser, arduino_port)
		elif commands_check==2:
			flag = True
			check_REZ(ser, arduino_port, flag)
		break
	elif commands =="7":
		initial_setup_of_the_chip(ser)
		break
	elif commands =="8":
		write_File_All_In_One_File()
		break
	elif commands =="9":
		print("Write arduino port")
		port = input()
		check_Temperature(ser, port)
		break
	elif commands =="10":
		main_read_address_and_form_file_in_all_adderss_on_chip(ser)
		break
	elif commands =="11":
		give_number_port(ser)
		break
	elif commands =="0":
		break
	else:
		print ("Wrong command entered!")