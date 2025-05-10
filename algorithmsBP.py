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
    Args:
        TLSID (str): Traffic Light ID
    Returns: 
        (int): The lane index of the traffic light with the highest weight
    """
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
    """Maxiumum Indepdent Set BackPressure Algorithm that calculates the queue
       differences between the two lanes for the intersection route. Also add 
       the waiting time and the speed of the entry lane to reduce stop-start
       bahaviour. Indepdently cacluates the weights for each lane then using
       the conflict list it then will find the maximum indepdent set of lanes
       with the highest wight and will return that MIS traffic light phase.
        Args:
            TLSID (str): Traffic Light ID
            conflicts (list): List of MIS lanes with no conflicts
        Returns:
            (int): The lane index of the traffic light with the 
            MIS weight

    """
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

