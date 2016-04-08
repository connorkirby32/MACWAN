#Leach Protocol Simulation 
#Connor Kirby
#CPE 400


import random
import math
import string
import sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.text 

cluster_probability = 30
num_nodes = 0
current_round = 0

#Contains all of the sensors in our network
sensor_list = []
cluster_heads = []

#Seed rand as to generate same random sequence
random.seed(8)

class Sensor: 

	def __init__(self, mac_address, x, y):
	    self.sensor_data = []
	    self.mac_address = mac_address
	    self.current_cluster_head = False
	    self.previous_cluster_head = False
	    self.battery_life = 100
	    self.x_pos = x;
	    self.y_pos = y;
	    self.transmit_mac_address = 'null'
	    self.transmit_sensor = ' '

	def RSSIProtocol(self, signals):
		
		for signal in signals:
			signal_stregnth = distance((self.x_pos,self.y_pos),(signal.x_pos,signal.y_pos))
			if(self.transmit_mac_address == 'null'):
				min =  signal_stregnth;
				self.transmit_mac_address = signal.mac_address
			elif (signal_stregnth < min):
				min =  signal_stregnth;
				self.transmit_mac_address = signal.mac_address
				self.transmit_sensor = signal

		print(str(self) + " is responding to cluster head " + str(self.transmit_mac_address) + "'s advertisement")

	def __str__(self):
		return str("Sensor with MAC Address of " + str(self.mac_address + " and position of (%i, %i)" %(self.x_pos, self.y_pos)))

def SelfElection():
	del cluster_heads[:]
	#Loop so that we are guranteeded at least one cluster head per round
	while len(cluster_heads) < 1:
		#For Each Sensor
		for sensor in sensor_list:
			#Check to make sure sensor is still alive
			if sensor.battery_life > 0:
				#Clear data and previous targeted cluster head from last round
				sensor.transmit_mac_address = 'null'
				del sensor.sensor_data[:]
				#Reset Current Sensor Flags
				if sensor.current_cluster_head:
					sensor.current_cluster_head = False
				else:
					#Calculate current probablity
					t_probablity = random.randint(0,100)
					if t_probablity <= cluster_probability:
						#Check to make sure sensor has not already been a sensor
						if not sensor.previous_cluster_head:
							sensor.current_cluster_head = True
							sensor.previous_cluster_head = True
							cluster_heads.append(sensor)
							#Notify that sensor is cluster head for current round
							print(str(sensor) + " elected as cluster head")
						else:
							sensor.previous_cluster_head = False


def SelfElectionImproved():
	del cluster_heads[:]
	alive_count = 0
	battery_average = 0
	while len(cluster_heads) < 1:
		for sensor in sensor_list:
			if sensor.battery_life > 0:
				battery_average += sensor.battery_life;
				alive_count+= 1
				sensor.transmit_mac_address = 'null'
				sensor.sensor_data.clear()
				if sensor.current_cluster_head:
					sensor.current_cluster_head = False
				else:
					t_probablity = random.randint(0,100)
					if t_probablity <= cluster_probability:
						#Check to make sure sensor has not already been a sensor
						if not sensor.previous_cluster_head:
							sensor.current_cluster_head = True
							sensor.previous_cluster_head = True
							cluster_heads.append(sensor)
							#Notify that sensor is cluster head for current round
							print(str(sensor) + " elected as cluster head")
						else:
							sensor.previous_cluster_head = False

		#"Improvement"
		threshold = battery_average/alive_count
		for heads in cluster_heads:
			if heads.battery_life < threshold :
				cluster_heads.remove(heads)



def Advertisment():
		print('\n'"Cluster heads are advertising"'\n')
		#For each sensor, compare position to determine closest cluster head
		for sensor in sensor_list:
			#Check to make sure sensor is not dead
			if sensor.battery_life > 0:
				if not sensor.current_cluster_head:
					sensor.RSSIProtocol(cluster_heads)
		print('\n''\n')

def Schedule():
	print("Schedule Creation TDMA")
	#For Each head, determine in what time order to allow sensor nodes to send data
	for heads in cluster_heads:
		print("Schedule of: " + str(heads.mac_address))
		for sensor in sensor_list:
			if not sensor.current_cluster_head and sensor.battery_life > 0:
				if sensor.transmit_mac_address == heads.mac_address:
						print (str(sensor.mac_address))
	print('\n''\n')					
				
def SteadyState():
	print("Cluster Heads Collecting Data" '\n')

	#Cluster heads collect data from their sensor nodes
	for heads in cluster_heads:
		for sensor in sensor_list:
			if not sensor.current_cluster_head:
				if sensor.transmit_mac_address == heads.mac_address and sensor.battery_life > 0:

						#Generate Random Data
						sensor.sensor_data.append(str(heads) + " is recieving Data from " + (str(sensor) + " with a value " +str(random.randint(100,200))))
						print(sensor.sensor_data)
						heads.sensor_data.append(sensor.sensor_data)
						sensor.battery_life-=len(sensor.sensor_data) * distance((sensor.x_pos,sensor.y_pos),(heads.x_pos,heads.y_pos)) *.05
		#Cluster head will compress and send the data to the base station
		if(heads.battery_life > 0):
			head_data = (str(heads) + " is generating its own data with a value of " +str(random.randint(100,200)))
			heads.sensor_data.append(head_data)
			print(head_data)
			heads.battery_life-=len(heads.sensor_data) * distance((sensor.x_pos,sensor.y_pos),(130,120)) * .05	
			print(str(heads.mac_address) + " is transmitting to 00:00:00:00:00:00 " '\n')	

#Calculates the distance between two sensor nodes 
def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

#Genereates a random MAC address to assign to a sensor node
def RandomMAC():
	mac = [ 0x00, 0x16, 0x3e,
		random.randint(0x00, 0x7f),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff) ]

	return ':'.join(map(lambda x: "%02x" % x, mac))



num_nodes = int(raw_input("Enter the amount of nodes in the network: "))

for i in range(0, num_nodes):
	sensor_list.append(Sensor(RandomMAC(),(random.randint(0,100)), (random.randint(0,100))))


while(1):
	print('\n''\n')
	if(sys.argv[1] == '-I'):
		SelfElectionImproved()
	else:
		SelfElection()
	SelfElection()
	Advertisment()
	Schedule()
	SteadyState()

	#Display the sensor network
	matplotlib.rcParams['axes.unicode_minus'] = False
	fig, ax = plt.subplots()
	plt.scatter(120, 120, marker='H', color= [0,0,0], s = 500)
	plt.text(130,120,"00:00:00:00")
	alive_count = 0
	for heads in cluster_heads:
		head_color = [random.uniform(0.1, 1.0) ,random.uniform(0.1, 1.0) ,random.uniform(0.1, 1.0)]
		for sensor in sensor_list:
			if not sensor.current_cluster_head:
				if sensor.transmit_mac_address == heads.mac_address and sensor.battery_life > 0:
					plt.scatter(sensor.x_pos, sensor.y_pos, marker='o', color= head_color, s = 10)
					plt.text(sensor.x_pos, sensor.y_pos,str(float("{0:.2f}".format(sensor.battery_life))))
					alive_count+=1
		if(heads.battery_life > 0):
			plt.scatter(heads.x_pos, heads.y_pos, marker='x',color= head_color,s = 400 )
			alive_count+=1
			plt.text(heads.x_pos,heads.y_pos,str(float("{0:.2f}".format(heads.battery_life))))
		else:
			plt.scatter(heads.x_pos, heads.y_pos, marker='x',color= head_color,s = 400 )
			plt.text(heads.x_pos,heads.y_pos,str(0))

		title = str('Leach Protocol: Round ' + str(current_round)+ ' ' + str(alive_count) + '/' +  str(len(sensor_list)) + ' Sensors are alive')
		ax.plot(label='parametric curve')
		ax.legend()
		ax.set_title(title)


	if alive_count == 0:
		print("Simulation Over")
		print("Network lasted " + str(current_round) + " rounds")
		break
	plt.show()


	current_round+=1
			


