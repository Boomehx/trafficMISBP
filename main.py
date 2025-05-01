import os
import sys
import traci
import sumolib
from conflictsUtils import *
from algorithmsBP import *
from utils import *



if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Environment variable SUMO_HOME is not set. Please configure it to point to your SUMO installation.")

sumo_config = [
    'sumo-gui',
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


def newstatesList (tlsIDLST, juncList, startLane, laneNum):
    lst = []
    misFullList = []
    for i in range(len(tlsIDLST)):
        #print(str(i) + "--------------------------------------------------------------------------------")
        sortAngleList = getSortedAngleList(tlsIDLST[i], juncList[i])

        mapDic = newMappingDic(sortAngleList, startLane[i])
        preConflictRoutes = newRouteMappingDic(tlsIDLST[i], mapDic)


        conflicts = getConflicts(preConflictRoutes, laneNum[i])
        misList = getMISList(conflicts)
        reMapList = reMapRoute(mapDic, misList, tlsIDLST[i])
        misFullList.append(reMapList)
        states = getStates(reMapList, tlsIDLST[i])
        lst.append(states)
    return lst, misFullList

def generate_traffic_light_phases(traffic_light_id):
    """
    Dynamically generates traffic light phases for a junction based on the number of lanes.
    """
    # Get controlled lanes
    num_lanes = len(traci.trafficlight.getControlledLanes(traffic_light_id))
 
  

    # Generate phases
    phases = []
    for i in range(num_lanes):
        # All red except one lane green
        state = ["r"] * num_lanes
        state[i] = "G"  # Green for one lane
        phases.append("".join(state))# 10 seconds green phase
  
   
     

    return phases

#print(generate_traffic_light_phases("TLS0"))

try:
#-------------------------------------
    #junctions = ["Junc0"]
    #tls = ["TLS0"]
    #phases = ["SET"]
    #phaseTimes = [150]
    #startLanes = ["EB0_0"]
    #laneNum = [16] #30
    #overallList = [{}]
#------------------------------------------------------
    junctions = ["Junc0","Junc1","Junc2","Junc3","Junc4","Junc5","Junc6","Junc7","Junc8","Junc9"]
    tls = ["TLS0","TLS1","TLS2","TLS3","TLS4","TLS5","TLS6","TLS7","TLS8","TLS9"]
    phases = ["SET","SET","SET","SET","SET","SET","SET","SET","SET","SET"]
    phaseTimes = [150,150,150,150,150,150,150,150,150,150]
    startLanes = ["EB0_0","EB1_0","EB2_0","EB3_0","EB4_0","NE5_0","SB6_0","NE7_0","SE8_0","SE9_0"]
    laneNum = [12,16,16,12,20,24,16,24,16,12]
    overallList = [{},{},{},{},{},{},{},{},{},{}]
    #print("Traffic Lights")
    print(traci.trafficlight.getControlledLinks("TLS8"))
    states, mis = newstatesList(tls, junctions,startLanes, laneNum)
    queue = []
    lane_vehicle_entry_time = {}
    lane_vehicle_exit_time = {}
    vehicle_last_lane = {}
    #FREEFLOWSPEED = 20
    #SHOCKWAVESPEED = 5
    #JAMDENSITY = 10
    #TIMESTEP = 1
    #SATURATIONFLOW = 1800
    TURNADJUSTMENT = {"l": 0.7, "r": 0.9, "s": 1.0}

    #connected = []
    #removed = []
    #percentage = 0.4
    active = 0
    
   
    while traci.simulation.getMinExpectedNumber() > 0 and traci.simulation.getTime() < 1500:
        traci.simulationStep()
        #print("Overall")
        #print(overallList)
        #print(createValidRandomRoutes())
        stuck = 0
        print(states)
        for  i in range(len(tls)):
                #overallList[i] = estimateQueueLengths(tls[i])

                #print(removeConnectedCars(connected,removed,0.4))
                #print(traci.vehicle.getIDList())
                #print("The need for speed")
                #print(speed_to_density(25))
                #print("INCOMING")
                #print(traci.junction.getIncomingEdges("Junc0"))
                #overallList[i] = estimateLaneQueue(tls[i])
                #print(tls[i])
                #print(overallList[i])
                if phases[i] == "SET":
                    phases[i] = "PROCESSING"
                    #print(simpleBP(tls[i]))
                            

                    pressure = simpleBP(tls[i])
                    #pressure = EQBP(tls[i],overallList[i])
                    #pressure = MISBP(tls[i], mis[i])
                    #pressure = MISEQBP(tls[i], overallList[i], mis[i])
                    #pressure = MISEQBP(tls[i], overallList[i], mis[i])
                    traci.trafficlight.setRedYellowGreenState(tls[i], states[i][pressure])

                if phases[i] == "PROCESSING":
                    phaseTimes[i] = phaseTimes[i] - 1
                    if phaseTimes[i] <= 0 and  simpleBP(tls[i]) == pressure and active == 0:
                        #print("STILL GOING")
                        active = 1
                        phaseTimes[i] = 150
                    
                    elif phaseTimes[i] <= 0 and simpleBP(tls[i]) == pressure and active == 1:
                        #print("stuck")
                        if simpleBP(tls[i]) == len(states[i] ) - 1:
                            stuck = 0
                        else:
                            stuck = simpleBP(tls[i]) + 1
                            if stuck not in states[i].keys():
                                stuck = 0
                            
                        phaseTimes[i] = 150
                        active = 2
                        traci.trafficlight.setRedYellowGreenState(tls[i], states[i][stuck])
                    
                    elif phaseTimes[i] <= 0 and simpleBP(tls[i]) == pressure and active == 2:
                        #print("stuckAAAA")
                        if simpleBP(tls[i]) + 2 == len(states[i] ) - 1:
                            stuck = 1
                        else:
                            stuck = simpleBP(tls[i]) + 2
                            if stuck not in states[i].keys(): 
                                stuck = 1
                            
                        phaseTimes[i] = 150
                        active = 2
                        traci.trafficlight.setRedYellowGreenState(tls[i], states[i][stuck])
                        

                    elif phaseTimes[i] <= 0:
                        active  = 0
                        phaseTimes[i] = 25
                        traci.trafficlight.setRedYellowGreenState(tls[i], states[i]["STOP"])
                        phases[i] = "BREAK"

                if phases[i] == "BREAK":
                    phaseTimes[i] = phaseTimes[i] - 1
                    if phaseTimes[i] <= 0:
                        phaseTimes[i] = 150
                        phases[i] = "SET"
        
finally:
    traci.close()