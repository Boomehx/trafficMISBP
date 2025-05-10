import traci
import math
#Getting Lane IDs for the intersection

def getIncomingOutcomingLanes(TLSID):
    """Gets controlled routes for intersection. This is the entry and exit lanes
       of the intersection.
        Args:
            TLSID (str): Traffic Light ID
        Returns:   
            (list): List of routes for the intersection. Each route is a tuple of
            two lanes. The first lane is the entry lane and the second lane is the exit lane.

    """
    routes = []
    lst = traci.trafficlight.getControlledLinks(TLSID)

    for i in range(len(lst)):
        try:
            routes.append([lst[i][0][0], lst[i][0][1]])
        except:
            print("Error: Lane ID not found")
            print(lst[i])
            print("TLSID: ", TLSID)
            print(routes)


    return routes

def getOutcomingLanes(TLSID):
    """Gets the exit lanes of the intersection.
         Args:
            TLSID (str): Traffic Light ID
        Returns:
            (list): List of exit lanes for the intersection.
    
    """
    lst = getIncomingOutcomingLanes(TLSID)
    output = []
    for lane in range(len(lst)):
        if lst[lane][1] not in output:
            output.append(lst[lane][1])
    return output

#-----Mapping Lanes to correct traffic light index

def getStates(reMapList, TLSID):
    """This gets the conflicts and maps the conflict lanes to the
       traffic light sequence.
       Args:
            reMapList (list): List of lanes that are do not conflict with each other
            TLSID (str): Traffic Light ID
        Returns:
            (dict): Dictionary of traffic light states. The key is the lane 
            index and the value is the state.
    """
    laneCount = len(traci.trafficlight.getControlledLanes(TLSID))
    outputDic = {}
    base = ["r"] * laneCount
    for laneC in range(laneCount):
        base = ["r"] * laneCount
        for lane in reMapList:
            if lane[0] == laneC:
                for subLane in lane:
                    base[subLane] = "G"
        outputDic[laneC] = "".join(base)
    outputDic["STOP"] ="".join(["r"] * laneCount)
    return outputDic

def getAngle(laneID, junctionID, TLSID):
    """Gets the clockwise angle of a lane at an intersection
    Output: Float
    Args:   
        laneID (str): Lane ID
        junctionID (str): Junction ID
        TLSID (str): Traffic Light ID
    Returns:
        (float): Angle positon of the lane at the intersection in radians.
    """
    # Get the angle of the lane at the intersection
    incomingLanes = traci.trafficlight.getControlledLanes(TLSID)
    laneShape = traci.lane.getShape(laneID)
    if laneID in  incomingLanes:
        x, y = laneShape[0]
    else:
        x, y = laneShape[-1]
    juncX, juncY, = traci.junction.getPosition(junctionID)
    angle = math.atan2 (y - juncY, x - juncX)
    return angle

def getSortedAngleList(TLSID, junctionID):
    """Orders the lanes of an intersection in a clockwise order.
       Args:
            TLSID (str): Traffic Light ID
            junctionID (str): Junction ID
        Returns:
            (list): List of lanes in a clockwise order. Each lane
            is a tuple of lane ID and angle.
    """
    incomingLanes = list(traci.trafficlight.getControlledLanes(TLSID))
    incomingoutcomingLanes = getOutcomingLanes(TLSID)
    angleList = []
    for i in range(len(incomingLanes)):
        incomingoutcomingLanes.append(incomingLanes[i])
    for i in range(len(incomingoutcomingLanes)):
        angleList.append([incomingoutcomingLanes[i], math.degrees(getAngle(incomingoutcomingLanes[i], junctionID, TLSID))])
    sortedAngleList = sorted(angleList, key=lambda x: x[1])[::-1]
    return sortedAngleList

def newMappingDic(sortedAngleList, startLane):
    """
    This reorders the angle list so that it starts with the first lane
    at the top of the intersection. This is because the traffic light
    lane index always starts at this point.
    Args:   
        sortedAngleList (list): List of lanes in a clockwise order. Each lane
            is a tuple of lane ID and angle.
        startLane (str): Lane ID of the first lane at traffic light index 0.
    Returns:
        (dict): Dictionary of lanes in a clockwise order. The key is the lane
            index and the value is the lane ID.
    """
    count = -1

    sortedStart = []
    output = {}
    for i in range(len(sortedAngleList)):
        
        if sortedAngleList[0][0] == startLane:
            sortedStart = sortedAngleList
        else:
            if sortedAngleList[i][0] != startLane:
                count += 1
            elif sortedAngleList[i][0] == startLane:
                count  += 1
                sortedStart = sortedAngleList[count:] + sortedAngleList[:count]
                break
    for lane in range(len(sortedStart)):
        output[lane] = sortedStart[lane][0]

    return output

def newRouteMappingDic(TLSID, mapDictionary):
    """
    Pre-Conflict Graph. Maps the Lane ID of the traffic light routes
    to the order of the lane. This is not traffic light index which is 
    only the entry lanes that are 
    Args:
        TLSID (str): Traffic Light ID
        mapDictionary (dict): Dictionary of lanes in a clockwise order.
        The key is the lane index and the value is the lane ID.
    Returns:
        (list): List of routes for the intersection. Each route is a tuple of
        two lanes position index. The first lane is the entry lane and the 
        second lane is the exit lane.
   """
    routes = getIncomingOutcomingLanes(TLSID)
    for lane in range(len(routes)):
        for key, val in mapDictionary.items():
            if routes[lane][0] == val:
                routes[lane][0] = key
            if routes[lane][1] == val:
                routes[lane][1] = key

    return routes

def reMapRoute(mappingDict, conflictList, TLSID):
    """Remaps Lane Postions to Lane Traffic Light Index. Will
    Only be Entry Lanes being controlled by traffic light.
    Args:
        mappingDict (dict): Dictionary of lanes in a clockwise order. The key
        is the lane index and the value is the lane ID.
        conflictList (list): List of conflicts.
        TLSID (str): Traffic Light 
    Returns:
        (list): List of lanes that do not conflict with each other. First lane in
        the list is primary lane and the rest are non-conflicting lanes.
        List(List(Primary Traffic Light Index, Non-Conflicting with Primary Index ..., ...))"""
    lanes = traci.trafficlight.getControlledLanes(TLSID)
    convertList = []
    tempList = []
    outputList = []
    for item in conflictList:
        for subItem in item[1]:
            start = mappingDict[item[0]]
            end = mappingDict[subItem]
            convertList.append([start] + [end])
    for lane in convertList:
        for sublane in lane:
            tempList.append(lanes.index(sublane))
        outputList.append(tempList)
        tempList = []
    
    return outputList
        