import serial
import time
import pylab
import crc8
import numpy
import scipy
#from matplotlib import mlab
import matplotlib.pyplot as plt
from scipy import interpolate
#from scipy.interpolate import interp1d
	
def coefficients(g, flag_write):
	#enter the file number
	numberPin = int(g)
	col_list = readFile(g)
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
	if flag_write == False:
		xlistNew.append(xlist[0])
		ylistNew.append(ylist[0])
		flag_start=True
		for i in range(6):
			ylistNew.append(ylist[i+1])
			xlistNew.append(xlist[i+1])
		xlistNew.append(xlist[-1])
		ylistNew.append(ylist[-1])
		print(xlistNew)
		print(ylistNew)
		list_byte_one_chip = calculationOfCoefficients(xlistNew, ylistNew, numberPin, flag_write)
		return list_byte_one_chip
	else:
		flag_start = False
		while flag_start == False:
			print ("\n" + "-------------------------")
			print ("\n" + "Select mode:" + "\n" + "1 - automatic data entry;" + "\n" + "2 - manual data entry;" + "\n" + "3 - exit.")
			print ("-------------------------" + "\n")
			setting = str(input())
			if setting == "1":
				xlistNew.append(xlist[0])
				ylistNew.append(ylist[0])
				flag_start=True
				for i in range(6):
					ylistNew.append(ylist[i+1])
					xlistNew.append(xlist[i+1])
				xlistNew.append(xlist[-1])
				ylistNew.append(ylist[-1])
				calculationOfCoefficients(xlistNew, ylistNew, numberPin, flag_write)
			elif setting == "2":
				xlistNew.append(xlist[0])
				ylistNew.append(ylist[0])
				flag_start = True
				for i in range(6):
					y = input()
					ylistNew.append(y)
					x= searchForCoordinats(ylist, xlist , y)
					xlistNew.append(x)
				xlistNew.append(xlist[-1])
				ylistNew.append(ylist[-1])
				calculationOfCoefficients(xlistNew, ylistNew, numberPin, flag_write)
			elif setting == "3":
				pass
			else:
				print ("Invalid command entered!")
	pass
	
def form_interval(xlist, x_list_interval_data, y_list_interval_data, i, k):
	x_list_interval_data1 = []
	y_list_interval_data1 = []
	interval_data1 = []
	start = xlist[i]
	stop = xlist[k]
	print ("start = " + str(start) + " stop = " + str(stop))
	test_flag = False
	for f in range(len(x_list_interval_data)):
		if test_flag == True:
			x_list_interval_data1.append(round(x_list_interval_data[f], 1))
			y_list_interval_data1.append(round(y_list_interval_data[f],3))
			if round(x_list_interval_data[f], 1) >= stop:
				break
		if round(x_list_interval_data[f], 1) == round(start, 1):
			#print(x_list_interval_data[f])
			test_flag = True
	interval_data1.append(x_list_interval_data1)
	interval_data1.append(y_list_interval_data1)
	return interval_data1
	
def minimum(xlist, ylist):
	xlist_test = xlist
	ylist_test = ylist
	new_list = []
	interval_data = interpol(xlist, ylist)
	x_list_interval_data = interval_data[0]
	y_list_interval_data = interval_data[1]
	
	for i in range(7):

		print(xlist_test)
		print(ylist_test)
		print ("test = " + str(i) + " i " + str(i+1))
		interval = form_interval(xlist_test, x_list_interval_data, y_list_interval_data, i, i+1)
		x_list_interval = interval[0]
		y_list_interval = interval[1]
		#print (y_list_interval)
		y_real = 0
		x_real = 0
		for j in range(len(x_list_interval)-1):
			k_real=float((ylist_test[i]-ylist_test[i+1])/(xlist_test[i]-xlist_test[i+1]))
			b_real = int(ylist_test[i+1] - k_real*xlist_test[i+1])
			difference = []
			x_list_test = []
			for k in range(len(y_list_interval)-1):
				x_list_test.append(k)
				kv_sum = abs(x_list_interval[k]*k_real + b_real) - abs(y_list_interval[k])
				difference.append(pow(kv_sum, 2))
			sum = 0
			for k in difference:
				sum = sum + abs(k)
			if j!=0:
				if sum < sum_last:
					y_real=int(ylist_test[i+1])
					x_real=round(xlist_test[i+1], 1)
					sum_last = sum
			else:
				sum_last = sum

			ylist_test[i+1]=y_list_interval[j]
			xlist_test[i+1]=x_list_interval[j]
			
		ylist_test[i+1]=y_real
		xlist_test[i+1]=x_real
	'''	
	x_list_interval = 0
	y_list_interval = 0

	for i in range(7):
		print(xlist_test)
		print(ylist_test)
		print ("test = " + str(i) + " i " + str(i+1))
		interval = form_interval(xlist, x_list_interval_data, y_list_interval_data, i, i+1)
		x_list_interval = interval[0]
		y_list_interval = interval[1]
		
		y_real = 0
		x_real = 0
		for j in range(len(x_list_interval)):
			k_real=float((ylist_test[i]-ylist_test[i+1])/(xlist_test[i]-xlist_test[i+1]))
			b_real = int(ylist_test[i+1] - k_real*xlist_test[i+1])
			difference = []
			x_list_test = []
			for k in range(len(y_list_interval)-1):
				x_list_test.append(k)
				difference.append((abs(x_list_interval[k]*k_real + b_real) - abs(y_list_interval[k]))**2)
			sum = 0
			for k in difference:
				sum = sum + abs(k)

			if j!=0:
				if sum < sum_last:
					y_real=int(ylist_test[i])
					x_real=round(xlist_test[i], 1)
					sum_last = sum
			else:
				sum_last = sum

			ylist_test[i]=y_list_interval[j]
			xlist_test[i]=x_list_interval[j]

		ylist_test[i]=y_real
		xlist_test[i]=x_real
	'''
	new_list.append(xlist_test)
	new_list.append(ylist_test)
	print ("New X = " + str(xlist_test))
	print ("New Y = " + str(ylist_test))
	
	return new_list
	
def min_kv(xlist, ylist, interval_left, interval_right):

	interval = interpol(xlist, ylist)
	x_list_interval = interval[0]
	y_list_interval = interval[1]
	
	summa_x = 0
	kv_summ_x = 0
	summa_y = 0
	summ_x_y_proizv = 0
	for i in range(len(x_list_interval)):
		summa_x = summa_x + x_list_interval[i]
		kv_summ_x = kv_summ_x + (x_list_interval[i]*x_list_interval[i])
		summa_y = summa_y + y_list_interval[i]
		summ_x_y_proizv = summ_x_y_proizv + (x_list_interval[i]*y_list_interval[i])
	delta = (kv_summ_x * len(x_list_interval)) - (summa_x * summa_x)
	delta_k = (summ_x_y_proizv*len(x_list_interval)) - (summa_y*summa_x)
	delta_b = (kv_summ_x*summa_y) - (summ_x_y_proizv*summa_x)

	coef_k = delta_k/delta
	coef_b = delta_b/delta

	coef_all = [coef_k, coef_b]
	
	return coef_all
	
def interpol(xlist_test, ylist_test):
	tck = interpolate.splrep(xlist_test, ylist_test)
	temperaturerite = xlist_test[0]
	stop_step = xlist_test[len(xlist_test)-1]
	step = 0.1
	interval_y = []
	interval_x = []
	interval = []
	while temperaturerite < stop_step:
		interval_x.append(temperaturerite)
		interval_y.append(interpolate.splev(temperaturerite, tck))
		temperaturerite = temperaturerite + step
	interval.append(interval_x)
	interval.append(interval_y)
	return interval
	
def read_file_in_coef():
	print("Enter number file:")
	port_number = input()
	file = open('c:/micros/data/set.txt', 'r')
	say = []
	col_list = []
	flag = False
	for line in file:
		#print (line)
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
			say.append(test_status)
	file.close()		
	return say
	
def calculationOfCoefficients (xlist, ylist, k, flag_write):
	coefB = []
	coefK = []
	kIdeal = -16
	bIdeal = 2047
	xMinIdeal = -60
	yMinIdeal = -16*xMinIdeal+2047
	xMaxIdeal = 125
	yMaxIdeal = -16*xMaxIdeal+2047
	i=1
	
	print("\n" + "-------------------------" + "\n" + "RESULT:")
	x_new_list = []
	y_new_list = []
	#new_list = minimum(xlist, ylist)
	#x_new_list = new_list[0]
	#y_new_list = new_list[1]
	#test_k = []
	#test_b = []
	'''
	while i<len(x_new_list):
		k_real = 0
		b_real = 0
		k_ideal = 0
		b_ideal = 0
		k_real=float((y_new_list[i-1]-y_new_list[i])/(x_new_list[i-1]-x_new_list[i]))
		b_real = y_new_list[i] - k_real*x_new_list[i]
		k_ideal = round(float(kIdeal/k_real), 4)
		b_ideal = int(-1*((kIdeal/k_real)*b_real)+bIdeal)
		print (" delta_k1 = " + str(k_ideal))
		print (" delta_b1 = " + str(b_ideal))
		i=i+1
		test_k.append(k_real)
		test_b.append(b_real)
		coefK.append(k_ideal)
		coefB.append(b_ideal)
	
	sttt_temperature = -60
	step_test = 0.01
	test_x = []
	test_y = []
	while True:
		if sttt_temperature>125:
			break
		test_x.append(sttt_temperature)
		if sttt_temperature<x_new_list[1]:
			sett = sttt_temperature*test_k[0] + test_b[0]
			test_y.append(sett*coefK[0]+coefB[0])
		elif sttt_temperature<x_new_list[2]:
			sett = sttt_temperature*test_k[1] + test_b[1]
			test_y.append(sett*coefK[1]+coefB[1])
		elif sttt_temperature<x_new_list[3]:
			sett = sttt_temperature*test_k[2] + test_b[2]
			test_y.append(sett*coefK[2]+coefB[2])
		elif sttt_temperature<x_new_list[4]:
			sett = sttt_temperature*test_k[3] + test_b[3]
			test_y.append(sett*coefK[3]+coefB[3])
		elif sttt_temperature<x_new_list[5]:
			sett = sttt_temperature*test_k[4] + test_b[4]
			test_y.append(sett*coefK[4]+coefB[4])
		elif sttt_temperature<x_new_list[6]:
			sett = sttt_temperature*test_k[5] + test_b[5]
			test_y.append(sett*coefK[5]+coefB[5])
		elif sttt_temperature>x_new_list[6]:
			sett = sttt_temperature*test_k[6] + test_b[6]
			test_y.append(sett*coefK[6]+coefB[6])
		sttt_temperature = sttt_temperature + step_test
	'''
	#plt.axis([minElement(test_x)-10, maxElement(test_x)+10, minElement(test_y)-200, maxElement(test_y)+200])
	#plt.plot(test_x, test_y, color = 'blue')
	#plt.plot([-55, 125], [2927, 47], color = 'red')
	#plt.show()
	
	full_coef_in_number_port = read_file_in_coef()
	print(full_coef_in_number_port[0])
	print(full_coef_in_number_port[1])
	print(full_coef_in_number_port[2])
	y_new_list = full_coef_in_number_port[0]
	coefK = full_coef_in_number_port[1]
	coefB = full_coef_in_number_port[2]
	'''
	fileText = open('c:/micros/data/Set.txt', 'a')
	fileText.write("PIN = " + str(k) + "\n")
	fileText.write("coef M:" + "\n")
	for j in y_new_list:
		fileText.write(str(j) + ", ")
		#print ("M = " + str(j))
	fileText.write("\n"+"coef K:" + "\n")
	for j in coefK:
		fileText.write(str(j) + ", ")
		#print ("K = " + str(j))
	fileText.write("\n"+"coef B:" + "\n")
	for j in coefB:
		fileText.write(str(j) + ", ")
		#print ("B = " + str(j))
	fileText.write("\n" +"----------------------------------------------------------------------" + "\n" + "\n")
	fileText.close()
	'''
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
	if flag_write == True:
		ser.write('1')	
		ser.write('1')	
		number_p = chr(k - 22)
		ser.write(number_p)	
		for i in win_test:
			ser.write(i)
		print("Please wait 4 seconds. " + '\n')
		time.sleep(4)
		#print("Apply high voltage to write coefficients." + '\n' + "Successfully?" + '\n' + "Please click ENTER")
		#command_Set_ENTER = input()
		#ser.write('6')	
		#number_p = chr(k - 22)
		#ser.write(number_p)
		#time.sleep(4)
		#ine_Temperatyre = ser.readlines()
		#print("Temperature = " + line_Temperatyre)
	else: 
		return win_test
	pass
	
def searchForCoordinats(y_list, x_list, y):
	x=-10000
	f=True
	i=0
	while f:
		if (y<y_list[i]) and (y>=y_list[i+1]):
			y1 = y_list[i]
			y2 = y_list[i+1]
			x1 = x_list[y_list.index(y1)]
			x2 = x_list[y_list.index(y2)]
			x = (((y-y1)*(x2-x1))/(y2-y1))+x1
			break;
		i=i+1
	return x


def binaryKey(list, size): 
	number = 0
	iterator = size
	for element in list:
		number = number + int(element)*(2**iterator)
		iterator = iterator-1
	print number
	return number

def minElement(list):
	min = 10000
	for element in list:
		if int(element) < min:
			min=int(element)
	return min

def maxElement(list):
	max = -10000
	for element in list:
		if int(element) > max:
			max=int(element)
	return max

def readFile(i): 
	file = open('c:/micros/data/'+ str(i) +'.txt', 'r')
	say = []
	col_list = []
	for line in file:
		say = line.split(' ')
		if len(say)>0:
			col_list.append(say[0])
			col_list.append(say[1])
	file.close()
	#print(col_list)
	return col_list

def writeFileAllInOneFile():
	list = []
	for i in range(22, 53):
		list.append(readFile(i))

	fileText = open('c:/micros/data/All.txt', 'w')
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
	for i in range(22, 53):
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

def writeFile(ser):
	inline = input()
	ser.write('3')
	time.sleep(4)
	ser.write('0')
	time.sleep(10)
	colBits = []
	lineBinary = ser.readlines()
	if len(lineBinary) != 32:
		print ("What the chip not works!!!")
		pass
	plata = 1
	sxema = 1
	pin = [22,23,38,39]
	list = []
	j=0
	i=1 
	for elem in lineBinary:
		if sxema >8:
			plata=plata+1
			sxema=1
			#j=j+1
		numberElment = 0
		number = ""
		for bit in elem:	
			if (numberElment>=4) and (numberElment<16):
				number = number + str(bit)
			numberElment = numberElment + 1
		fileText = open('c:/micros/data/'+str(pin[j])+'.txt', 'a')
		fileText.write(str(inline) + " " + str(int(number,2)) + " " + str(elem))
		fileText.close()
		pin[j]=pin[j]+1
		i=i+1
	pass
	
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
	
def build_graph():
	print ("\n" + "-------------------------") 
	print ("write number file")
	g = raw_input()
	numberPin = int(g)
	col_list = readFile(g)
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

def check_CRC8(ser):
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
	
def check_temprice(ser, number_file):
	ser.write('3')
	time.sleep(4)
	ser.write('0')
	time.sleep(4)
	number_file = int(number_file-22)
	lineBinary = ser.readlines()
	list_check_rez = lineBinary[number_file]
	list_check_rez.replace("\r","")
	list_check_rez.replace("\n","")
	return list_check_rez
	
def initial_setting(ser):
	print("Enter port number in arduino.")
	number_file = input()
	print ("\n" + "-------------------------") 
	flag = False
	print ("\n"+"Place wait")
	check_REZ(ser, number_file, flag)
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
	print("Check REZ?" + "\n" + "1 - Yes;" + "\n" + "2 - No;" + "\n" + "3 - Exit")
	print ("-------------------------" + "\n")
	commands_control = input()
	if commands_control == 1:
		flag = True
		check_REZ(ser, number_file, flag)
	elif commands_control==3:
		return
	print ("\n" + "-------------------------") 
	print("Record address?" + "\n" + "1 - Yes;" + "\n" + "2 - No;" + "\n" + "3 - Exit")
	print ("-------------------------" + "\n")
	commands_control = input()
	if commands_control == 1:
		write_adres(ser, number_file)
	elif commands_control == 3:
		return
	print ("\n" + "-------------------------") 
	print("\n" + "Apply high voltage to write ADDERSS.")
	print("Check address?" + "\n" + "1 - Yes;" + "\n" + "2 - No.")
	print ("-------------------------" + "\n")
	commands_control = input()
	if commands_control==1:
		ser.write('5')
		pin = chr(number_file - 22)
		ser.write(pin)
		check_CRC8(ser)
	
	pass

print ("Enter the number?" + "\n" + "1 - Yes;" +"\n" + "2 - No (use COM7)")	
commands_control = input()
if commands_control == 1:
	print ("Enter the number port")	
	number_COM_port = input()
else:
	number_COM_port = 7
ser = serial.Serial('COM' + str(number_COM_port), 9600, timeout=0)
ser.close()
ser.open()
ser.isOpen()
flag=True
col_list = []
print ("\n" + "-------------------------")
print ("menu commands:" + "\n" + "1 - measure temperature and write to file;" + "\n" + "2 - calculate the coefficients;" + "\n" + "3 - function REZ")
print ("4 - set address;" + "\n" + "5 - build a graph;" + "\n" + "6 - check REZ and CRC8;" + "\n" + "7 - initial setting;"  + "\n" + "8 - exit;" + "\n" + "9 - Form File;")
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
			print ("\n"+"1 - working with 1 chip;" + "\n" + "2 - working with 32 chips;" + "\n" + "3 - exit.")
			print ("-------------------------" + "\n")
			set = input()
			if set == 1:
				print ("enter the arduino port:")
				g=""
				g=raw_input()
				flag_switch = True
				coefficients(g, flag_switch);
				break
			elif set == 2:
				
				flag_switch = False
				list_byte_all_chipa = []
				for i in range(22, 54):
					list_byte_one_chip = []
					flag_list_file = False
					g = str(i)
					print(g)
					list_byte_one_chip = coefficients(g, flag_switch);
					for j in list_byte_one_chip:
						list_byte_all_chipa.append(j)
				for i in range(22,54):
					ser.write('1')	
					ser.write('2')
					for j in list_byte_all_chipa:
						ser.write(j)
				break
			elif set == 3:
				break
			else:
				print (" Incorrect command! ")
		
		break
	elif commands == "3":
		flag = False
		print ("write number pin:")
		number_file = input()
		print ("\n"+"Place wait")
		check_REZ(ser, number_file, flag)
		print ("\n" + "To set up?" + "\n" + "1 - Yes;" + "\n" + "2 - No.")
		commands_REZ = input()
		if commands_REZ == 1:
			ser.write('3')
			time.sleep(4)		
			ser.write('2')
		break
	elif commands == "5":
		build_graph()
		break
	elif commands == "4":
		print ("write number pin:")
		pin = input()
		write_adres(ser, pin)
		break
	elif commands == "6":
		commands_check = 0;
		print ("\n" + "-------------------------")
		print ("1 - check CRC8;" + "\n" + "2 - check REZ;" + "\n" + "3 - exit.")
		print ("-------------------------" + "\n")
		commands_check = input()
		print ("enter the file number:")
		number_file = input()
		pin = chr(number_file - 22)
		if commands_check==1:
			ser.write('5')
			ser.write(pin)
			check_CRC8(ser)
		elif commands_check==2:
			flag = True
			check_REZ(ser, number_file, flag)
		elif commands_check==0:
			break
		break
	elif commands =="7":
		initial_setting(ser)
		break
	elif commands =="8":
		break
	elif commands =="9":
		writeFileAllInOneFile()
		break
	elif commands =="10":
		resultat = []
		resultat = read_file_in_coef()
		print (resultat[0])
		print (resultat[1])
		print (resultat[2])
		break
	elif commands =="11":
		number_file = 22
		pin = chr(number_file - 22)
		number = check_temprice(ser, number_file)
		print("BIN = " + number + "DEC = " + str(int(number,2)) + " T = " + str(int(number,2)*0.0625))
		break
	else:
		print ("Wrong command entered!")