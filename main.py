import os
import sys
import traci
import sumolib
from conflictsUtils import *
from algorithmsBP import *
from utils import *
from EQ import *



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


#print(generate_traffic_light_phases("TLS0"))

try:
#------------------------------------------------------
    #This is the main paramters for the simulation C6E30L
    #Uncomment this section to run the C6E30L simulation
    #junctions = ["Junc0"]
    #tls = ["TLS0"]
    #phases = ["SET"]
    #phaseTimes = [150]
    #startLanes = ["NE0_0"]
    #laneNum = [30] #30
    #overallList = [{}]
#------------------------------------------------------
    #This is the main paramters for the simulation CN10EVEN
    junctions = ["Junc0","Junc1","Junc2","Junc3","Junc4","Junc5","Junc6","Junc7","Junc8","Junc9"]
    tls = ["TLS0","TLS1","TLS2","TLS3","TLS4","TLS5","TLS6","TLS7","TLS8","TLS9"]
    phases = ["SET","SET","SET","SET","SET","SET","SET","SET","SET","SET"]
    phaseTimes = [150,150,150,150,150,150,150,150,150,150]
    startLanes = ["EB0_0","EB1_0","EB2_0","EB3_0","EB4_0","NE5_0","SB6_0","NE7_0","SE8_0","SE9_0"]
    laneNum = [12,16,16,12,20,24,16,24,16,12]
    overallList = [{},{},{},{},{},{},{},{},{},{}]
#------------------------------------------------------
    states, mis = newstatesList(tls, junctions,startLanes, laneNum)
    active = 0
   
    while traci.simulation.getMinExpectedNumber() > 0 and traci.simulation.getTime() < 1500:
        traci.simulationStep()

        stuck = 0
        for  i in range(len(tls)):
                removeConnectedCars()
                updateConnectedVehicleHistory()
                overallList[i] = estimateQueueLengths(tls[i])
                print(overallList)

                if phases[i] == "SET":
                    phases[i] = "PROCESSING"
                    #Uncomment the pressure algorithm you want to use then change
                    #the occurance of the pressure variable in the code below to match

                    #pressure = simpleBP(tls[i])
                    #pressure = EQBP(tls[i],overallList[i])
                    #pressure = MISBP(tls[i], mis[i])
                    pressure = MISEQBP(tls[i], overallList[i], mis[i])
                    traci.trafficlight.setRedYellowGreenState(tls[i], states[i][pressure])

                if phases[i] == "PROCESSING":
                    phaseTimes[i] = phaseTimes[i] - 1
                    if phaseTimes[i] <= 0 and  MISEQBP(tls[i], overallList[i], mis[i]) == pressure and active == 0:

                        active = 1
                        phaseTimes[i] = 150
                    
                    elif phaseTimes[i] <= 0 and MISEQBP(tls[i], overallList[i], mis[i])== pressure and active == 1:

                        if MISEQBP(tls[i], overallList[i], mis[i]) == len(states[i] ) - 1:
                            stuck = 0
                        else:
                            stuck = MISEQBP(tls[i], overallList[i], mis[i]) + 1
                            if stuck not in states[i].keys():
                                stuck = 0
                            
                        phaseTimes[i] = 150
                        active = 2
                        traci.trafficlight.setRedYellowGreenState(tls[i], states[i][stuck])
                    
                    elif phaseTimes[i] <= 0 and MISEQBP(tls[i], overallList[i], mis[i]) == pressure and active == 2:
                        if MISEQBP(tls[i], overallList[i], mis[i])+ 2 == len(states[i] ) - 1:
                            stuck = 1
                        else:
                            stuck = MISEQBP(tls[i], overallList[i], mis[i]) + 2
                            if stuck not in states[i].keys(): 
                                stuck = 1
                            
                        phaseTimes[i] = 150
                        active = 3
                        traci.trafficlight.setRedYellowGreenState(tls[i], states[i][stuck])

                    elif  active == 3:
                        phaseTimes[i] = phaseTimes[i] - 1
                        active = 0
                        stuck = random.choice(list(states[i].keys()))
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