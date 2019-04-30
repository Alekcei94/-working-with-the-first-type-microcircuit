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
	try:
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
	except:
		pass
	
def form_interval(xlist, x_list_interval_data, y_list_interval_data, i, k):
	x_list_interval_data1 = []
	y_list_interval_data1 = []
	interval_data1 = []
	interval_delete = 0
	start = xlist[i]
	stop = xlist[k]
	#print ("start = " + str(start) + " stop = " + str(stop))
	test_flag = False
	for f in range(len(x_list_interval_data)):
		interval_delete += 1
		if test_flag == True:
			x_list_interval_data1.append(round(x_list_interval_data[f], 2))
			y_list_interval_data1.append(round(y_list_interval_data[f],3)) # !!!!!!!!!!
			if round(x_list_interval_data[f], 2) == stop:
				break
		if round(x_list_interval_data[f], 2) >= round(start, 2):
			#print(x_list_interval_data[f])
			test_flag = True
	print (str(interval_delete))
	interval_data1.append(x_list_interval_data1)
	interval_data1.append(y_list_interval_data1)
	interval_data1.append(interval_delete)
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
		print ("step = " + str(i+1) + " in " + str(7))
		interval = form_interval(xlist_test, x_list_interval_data, y_list_interval_data, i, i+1)
		del x_list_interval_data[0:interval[2]]
		del y_list_interval_data[0:interval[2]]
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
	
	#x_list_interval = 0
	#y_list_interval = 0
	'''
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
	step = 0.01
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
	new_list = minimum(xlist, ylist)
	x_new_list = new_list[0]
	y_new_list = new_list[1]
	test_k = []
	test_b = []
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
	#plt.axis([minElement(test_x)-10, maxElement(test_x)+10, minElement(test_y)-200, maxElement(test_y)+200])
	#plt.plot(test_x, test_y, color = 'blue')
	#plt.plot([-55, 125], [2927, 47], color = 'red')
	#plt.show()
	
	#y_new_list = [1460, 1404, 1350, 1258, 1231, 1165, 1099, 1035]
	#coefK = [6.0, 5.4815, 5.7739, 6.4593, 6.4, 7.2, 6.825]
	#coefB = [-5857, -5129, -5524, -6386, -6313, -7245, -6833]
	fileText = open('c:/micros/data/Set.txt', 'a')
	fileText.write("PIN = " + str(k) + "\n")
	#fileText.write("y_new_list = [ ")
	for j in range(len(y_new_list)):
		fileText.write(str(y_new_list[j]))
		if j<len(y_new_list)-1:
			fileText.write(" ")
		#print ("M = " + str(j))
	#fileText.write("]")
	fileText.write("\n")
	for j in range(len(coefK)):
		fileText.write(str(coefK[j]) )
		if j<len(coefK)-1:
			fileText.write(" ")
		#print ("K = " + str(j))
	#fileText.write("]")
	fileText.write("\n")
	for j in range(len(coefB)):
		fileText.write(str(coefB[j]))
		if j<len(coefK)-1:
			fileText.write(" ")
		#print ("B = " + str(j))
	#fileText.write("]")
	fileText.write("\n" +"----------------------------------------------------------------------" + "\n" + "\n")
	fileText.close()
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
		x = ele
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
		#ser.write('1')	
		#ser.write('1')	
		number_p = chr(k - 22)
		#ser.write(number_p)	
		#for i in win_test:
		#	ser.write(i)
		#print("Please wait 4 seconds. " + '\n')
		#time.sleep(4)
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
	try: 
		file = open('c:/micros/data/'+ i +'.txt', 'r')
		say = []
		col_list = []
		for line in file:
			say = line.split(' ')
			if len(say)>0:
				col_list.append(say[0])
				col_list.append(say[1])
		file.close()
		print(col_list)
		return col_list
	except:
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


flag=True
col_list = []
print ("\n" + "-------------------------")
print ("menu commands:" + "\n" + "1 - calculate the coefficients;")
print ("2 - build a graph;" + "\n" + "3 - exit;")
print ("-------------------------" + "\n")
while True:
	print ("enter the commands ")
	commands = str(input())
	if commands == "1":
		while True:
			print ("\n"+ "-------------------------")
			print ("\n"+"1 - working with 1 chip;" + "\n" + "2 - working with 32 chips;" + "\n" + "3 - exit.")
			print ("-------------------------" + "\n")
			set = input()
			if set == 1:
				print ("enter the file number")
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
					#for j in list_byte_one_chip:
					#	list_byte_all_chipa.append(j)
				#for i in range(22,54):
				#	ser.write('1')
				#	ser.write('2')
				#	for j in list_byte_all_chipa:
				#		ser.write(j)
				print("-----FINISH-----")
				break
			elif set == 3:
				break
			else:
				print (" Incorrect command! ")
		break
	elif commands == "2":
		build_graph()
		break
	elif commands =="3":
		break
	else:
		print ("Wrong command entered!")