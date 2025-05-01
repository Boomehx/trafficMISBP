import traci
from utils import *
import random

lane_vehicle_entry_time = {}
lane_vehicle_exit_time = {}
vehicle_last_lane = {}
overallList = []
connected = []
removed  = []
def simpleBP(TLSID):
    """Simple Backpressure Algorithm that calculates the queue differences 
    between the two lanes for the intersection route. Also add the waiting
    time for the entry lane. Calculates the highest weight for the lanes 
    at an intersection. 
    Output: Traffic Light Lane Index """
    maxPressure = 0
    maxLane = 0
    count = 0
    routes = getIncomingOutcomingLanes(TLSID)

    for lanes in range(len(routes)):
        count = (traci.lane.getLastStepVehicleNumber(routes[lanes][0]) - traci.lane.getLastStepVehicleNumber(routes[lanes][1])) + traci.lane.getWaitingTime(routes[lanes][0])

        if count > maxPressure:
            maxPressure = count
            maxLane = lanes
        
    return maxLane

def MISBP(TLSID, conflicts):
    """Maxiumum Indepdent Set BackPressure Algorithm"""
    routes = getIncomingOutcomingLanes(TLSID)
    entLanes = list(traci.trafficlight.getControlledLanes(TLSID))
    laneCounts = {}
    maxPressure = 0
    maxLane = 0
    count = 0
    for laneCount in range(len(routes)):
        
        count = (traci.lane.getLastStepVehicleNumber(routes[laneCount][0]) - traci.lane.getLastStepVehicleNumber(routes[laneCount][1])) + traci.lane.getWaitingTime(routes[laneCount][0])
        count = count * (traci.lane.getLastStepMeanSpeed(routes[laneCount][0]) + 1)
        laneCounts[entLanes.index(routes[laneCount][0])] = count

    for conflictLane in range(len(conflicts)):
        tempCount = 0
    
        for subConflict in range(len(conflicts[conflictLane])):
            tempCount = tempCount + laneCounts[conflicts[conflictLane][subConflict]]
           
        
        if tempCount  > maxPressure:
            maxPressure = tempCount
            maxLane = conflicts[conflictLane][0]
    return maxLane

def EQBP(TLSID, QueueLengths):
    maxPressure = 0
    maxLane = 0
    count = 0
    routes = getIncomingOutcomingLanes(TLSID)

    for lanes in range(len(routes)):
        direction = traci.lane.getLinks(routes[lanes][0])[0][6]


        flow = 2 * SATURATIONFLOW * TURNADJUSTMENT
        queue = (QueueLengths[routes[lanes][0]] - QueueLengths[routes[lanes][1]]) 
        count = (queue * flow) + traci.lane.getWaitingTime(routes[lanes][0])
        if count > maxPressure:
            maxPressure = count
            maxLane = lanes

    return maxLane

def MISEQBP(TLSID, QueueLengths, conflicts):
    maxPressure = 0
    maxLane = 0
    count = 0
    routes = getIncomingOutcomingLanes(TLSID)
    entLanes = list(traci.trafficlight.getControlledLanes(TLSID))
    laneCounts = {}

    for lanes in range(len(routes)):
        direction = str(traci.lane.getLinks(routes[lanes][0])[0][6]).lower()
        #print("DIRECTION")
        #print(direction)
        flow = 2 * SATURATIONFLOW * TURNADJUSTMENT[direction]
        queue = (QueueLengths[routes[lanes][0]] - QueueLengths[routes[lanes][1]]) 
        count = (queue * flow) + traci.lane.getWaitingTime(routes[lanes][0])
        laneCounts[entLanes.index(routes[lanes][0])] = count
    for conflictLane in range(len(conflicts)):
        tempCount = 0
    
        for subConflict in range(len(conflicts[conflictLane])):
            tempCount = tempCount + laneCounts[conflicts[conflictLane][subConflict]]
           
        
        if tempCount  > maxPressure:
            maxPressure = tempCount
            maxLane = conflicts[conflictLane][0]


    return maxLane




FREEFLOWSPEED = 30.0
SHOCKWAVESPEED = 5.0
JAMDENSITY = 20
TIMESTEP = 1
SATURATIONFLOW = 7200
TURNADJUSTMENT = {"l": 0.7, "r": 0.9, "s": 1.0}

def speed_to_density(speed):
    if speed == 0:
        return JAMDENSITY
    return JAMDENSITY / (1 - (FREEFLOWSPEED / SHOCKWAVESPEED) * math.log(1 - speed / FREEFLOWSPEED))

def estimateQueueLengths(TLSID):
    queueLengthDic = {}
    junctionRoutes = getIncomingOutcomingLanes(TLSID)
    junctionLanes = []
    for lane in range(len(junctionRoutes)):
        junctionLanes.append(junctionRoutes[lane][0])
        if junctionRoutes[lane][1] not in junctionLanes:
            junctionLanes.append(junctionRoutes[lane][1])


    for laneID in range(len(junctionLanes)):
        laneLength = traci.lane.getLength(junctionLanes[laneID])
        connectedVehicles = removeConnectedCars(connected, removed, 0.75)
       
        vehicleIDs = []
        fulllanevehicleIDs = traci.lane.getLastStepVehicleIDs(junctionLanes[laneID])
        for  laneVeh in range(len(fulllanevehicleIDs)):

            if fulllanevehicleIDs[laneVeh] in connectedVehicles:
                vehicleIDs.append(fulllanevehicleIDs[laneVeh])

        estimatedDensity = 0
        for vehicle in range(len(vehicleIDs)):

            speed = traci.vehicle.getSpeed(vehicleIDs[vehicle])
            density = speed_to_density(speed)
            estimatedDensity += density / len(vehicleIDs)

        queueLength = estimatedDensity * laneLength / 1000

        queueLengthDic[junctionLanes[laneID]] = queueLength
    return queueLengthDic






def removeConnectedCars(connected, removed, percentage):
    overallVehList = traci.vehicle.getIDList()

    for veh in range(len(overallVehList)):
        if overallVehList[veh] not in connected and overallVehList[veh] not in removed:    
            if random.random() < percentage:
                removed.append(overallVehList[veh])
            else:
                connected.append(overallVehList[veh])
    return connected

def averageSpeedOfCars (connected):

    totalSpeed = 0
    if len(connected) == 0:
        return 0
    for veh in range(len(connected)):
        try:
            totalSpeed += traci.vehicle.getSpeed(connected[veh])
        except:
            totalSpeed += 0
    return totalSpeed / len(connected)