import os
import sys
import traci
import sumolib
from conflictsUtils import *
from conflictsUtils import *
from algorithmsBP import *
from utils import *



if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Environment variable SUMO_HOME is not set. Please configure it to point to your SUMO installation.")

sumo_config = [
    'sumo',
    '-c', 'CN10EVEN.sumocfg',  
    '--step-length', '0.1',
    '--start',
    '--delay', '0', 
    '--lateral-resolution', '0.1',
    '--routing-algorithm', 'dijkstra',
    '--queue-output', 'queue_output.xml',
    '--summary-output', 'summary.xml',
    '--quit-on-end',
    '--no-warnings'
]


traci.start(sumo_config)



def generateTrafficLightPhases(TLSID):
    """
    Dynamically generates traffic light phases for a junction based on the number of lanes.
    """
    numLanes = len(traci.trafficlight.getControlledLanes(TLSID))
 
    phases = []
    for i in range(numLanes):
        state = ["r"] * numLanes
        state[i] = "G" 
        phases.append("".join(state))
  
   
     

    return phases

def generateAllPhases(tls):
    """
    Generates traffic light phases for all statsic traffic lights in the network.
    """
    all_phases = []
    for tlsID in tls:
        phases = generateTrafficLightPhases(tlsID)
        all_phases.append(phases)
    return all_phases



try:
#-------------------------------------
#uncomment this section to run the C6E30L simulation
    #junctions = ["Junc0"]
    #tls = ["TLS0"]
    #states = generateAllPhases(tls)
    #phases = ["SET"]
    #phaseTimes = [150]
    #startLanes = ["NE0_0"]
    #laneNum = [30]
    #currentLane = [0]
#------------------------------------------------------
    #This is the main paramters CN10EVEN
    junctions = ["Junc0","Junc1","Junc2","Junc3","Junc4","Junc5","Junc6","Junc7","Junc8","Junc9"]
    tls = ["TLS0","TLS1","TLS2","TLS3","TLS4","TLS5","TLS6","TLS7","TLS8","TLS9"]
    states = generateAllPhases(tls)
    phases = ["SET","SET","SET","SET","SET","SET","SET","SET","SET","SET"]
    phaseTimes = [150,150,150,150,150,150,150,150,150,150]
    startLanes = ["EB0_0","EB1_0","EB2_0","EB3_0","EB4_0","NE5_0","SB6_0","NE7_0","SE8_0","SE9_0"]
    laneNum = [12,16,16,12,20,24,16,24,16,12]
    currentLane = [0,0,0,0,0,0,0,0,0,0,0]


   
    while traci.simulation.getMinExpectedNumber() > 0 and traci.simulation.getTime() < 1500:

        traci.simulationStep()

        for  i in range(len(tls)):

                if phases[i] == "SET":
                    phases[i] = "PROCESSING"

                    if currentLane[i] > len(traci.trafficlight.getControlledLanes(tls[i])) - 1:

                        if currentLane[i] >= len( states[i]):
                            currentLane[i] = 0

                    traci.trafficlight.setRedYellowGreenState(tls[i], states[i][currentLane[i]])

                if phases[i] == "PROCESSING":

                    phaseTimes[i] = phaseTimes[i] - 1
             
                    if phaseTimes[i] <= 0:

                        phaseTimes[i] = 150
                        currentLane[i] = currentLane[i] + 1
                        phases[i] = "SET"

finally:
    traci.close()
                    


      