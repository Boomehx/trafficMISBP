import random
import math
from utils import *
import traci


connected = []
removed = []
historyBuffer = [] 
MAX_HISTORY_LENGTH = 100
CONNECTED_PERCENTAGE = 0.25

FREEFLOWSPEED = 30.0
SHOCKWAVESPEED = 5.0
JAMDENSITY = 30
SATURATIONFLOW = 7200
TURNADJUSTMENT = {"l": 0.7, "r": 0.9, "s": 1.0}


def removeConnectedCars():

    global connected, removed
    overallVehList = traci.vehicle.getIDList()
    for vehID in overallVehList:
        if vehID not in connected and vehID not in removed:
            if random.random() < CONNECTED_PERCENTAGE:
                removed.append(vehID)
            else:
                connected.append(vehID)
    return connected

def updateConnectedVehicleHistory():
    global connected, historyBuffer
    timestamp = traci.simulation.getTime()
    newRecords = []

    for vehID in connected:
        try:
            speed = traci.vehicle.getSpeed(vehID)
            pos = traci.vehicle.getLanePosition(vehID)
            laneID = traci.vehicle.getLaneID(vehID)

            newRecords.append({
                'vehID': vehID,
                'speed': speed,
                'pos': pos,
                'laneID': laneID,
                'time': timestamp
            })
        except:
            connected.remove(vehID)
    historyBuffer.extend(newRecords)

    if len(historyBuffer) > MAX_HISTORY_LENGTH * len(connected):
        historyBuffer = historyBuffer[-MAX_HISTORY_LENGTH * len(connected):]

def getInterpolatedSpeedAtPosition(laneID, xi, ti, sigma=20, tau=5, maxTimeDiff=40):
    global historyBuffer
    weights = []
    weightedSpeed = []

    for record in historyBuffer:
        if record['laneID'] != laneID:
            continue
        timeDiff = abs(ti - record['time'])
        if timeDiff > maxTimeDiff:
            continue
        space_diff = abs(xi - record['pos'])
        phi = math.exp(-(space_diff / sigma) - (timeDiff / tau))
        weights.append(phi)
        weightedSpeed.append(phi * record['speed'])

    if sum(weights) == 0:
        return FREEFLOWSPEED

    return sum(weightedSpeed) / sum(weights)

def speedDensity(speed):
    if speed >= FREEFLOWSPEED:
        return 0
    if speed <= 0:
        return JAMDENSITY
    try:
        return JAMDENSITY / (1 - (FREEFLOWSPEED / SHOCKWAVESPEED) * math.log(1 - speed / FREEFLOWSPEED))
    except:
        return JAMDENSITY 


def estimateQueueLengths(TLSID, cellLength=10, SpeedThreshold=5):
    queueLengthDic = {}
    junctionRoutes = getIncomingOutcomingLanes(TLSID)
    incomingLanes = []
 

    for i in range(len(junctionRoutes)):
        if junctionRoutes[i][0] not in incomingLanes:
            incomingLanes.append(junctionRoutes[i][0])
        if junctionRoutes[i][1] not in incomingLanes:
            incomingLanes.append(junctionRoutes[i][1])

    currentTime = traci.simulation.getTime()

    for laneID in incomingLanes:
        laneLength = traci.lane.getLength(laneID)
        numCells = int(laneLength // cellLength)
        queueLength = 0

        for i in range(numCells):
            xi = laneLength - (i + 0.5) * cellLength  
            speed = getInterpolatedSpeedAtPosition(laneID, xi, currentTime)
            if speed < SpeedThreshold:
                density = speedDensity(speed)
                queueLength += (density * cellLength) / 1000

        queueLengthDic[laneID] = queueLength


    return queueLengthDic

def MISEQBP(TLSID, QueueLengths, conflicts):
    maxPressure = 0
    maxLane = 0
    routes = getIncomingOutcomingLanes(TLSID)
    entLanes = list(traci.trafficlight.getControlledLanes(TLSID))
    laneCounts = {}
    for i in range(len(routes)):
        direction = str(traci.lane.getLinks(routes[i][0])[0][6]).lower()
        flow = 2 * SATURATIONFLOW * TURNADJUSTMENT[direction] # 2 is the the number of lanes in the moment in this case just the entrance and exit lane of the route
        queue = (QueueLengths[routes[i][0]] - QueueLengths[routes[i][1]])
        count = (queue * flow) 
        laneCounts[entLanes.index(routes[i][0])] = count

    for conflictLane in range(len(conflicts)):
         tempCount = 0
    
         for subConflict in range(len(conflicts[conflictLane])):
             tempCount = tempCount + laneCounts[conflicts[conflictLane][subConflict]]
           
        
         if tempCount  > maxPressure:
             maxPressure = tempCount
             maxLane = conflicts[conflictLane][0]

    return maxLane


inactive_lane_counts = {}





