import random
import math
import collections
import copy

householdStatus = {
    0 : 1,
    1 : 2,
    2 : 3,
    3 : 4,
    4 : 5
}

volunteerWork = {
    0 : 1,
    1 : 2,
    2 : 3,
    3 : 4,
    4 : 5
}

def generateSimulationData():
    donations = []
    requests = []
    arr = [j for j in range(5)]
    # 52 weeks
    for i in range(1, 53):
        # 5 beneficiaries
        r = []
        # Shuffle order at which beneficiary is picked as the time when beneficiaries
        # submit requests throughout the week is random
        random.shuffle(arr)
        for j in arr:
            quantityRequested = random.randint(0, 10)
            if quantityRequested > 0:
                r.append({'beneficiary': j, 'time': i, 'quantity': quantityRequested})
        requests.append(r)
        donations.append(random.randint(10, 50))
    return donations, requests

donations, requests = generateSimulationData()

def getUtility(quantity, timePassed, status, volunteer):
    return quantity * math.exp(-1 * timePassed) * status * volunteer

def getUtilityByQuantity(quantity, timePassed):
    return quantity * math.exp(-1 * timePassed)

#Random Allocation
def randomAllocationSimulation():
    totalUtility = 0
    individualUtilities = [0 for _ in range(5)]
    # Create one requests queue for each beneficiary
    queues = [collections.deque([]) for i in range(5)]
    requestsInQueue = 0
    global donations
    global requests
    tempDonations = copy.deepcopy(donations)
    tempRequests = copy.deepcopy(requests)
    for i in range(1, 53):
        r = tempRequests[i-1]
        d = tempDonations[i-1]
        for request in r:
            queues[request['beneficiary']].append(request)
            requestsInQueue += 1
        while d > 0 and requestsInQueue > 0:
            # Randomly pick a beneficiary to give the donation
            index = random.randint(0,4)
            if len(queues[index]) > 0:
                allocatedQuantity = min(d, queues[index][0]['quantity'])
                d -= allocatedQuantity
                queues[index][0]['quantity'] -= allocatedQuantity
                utility = getUtility(allocatedQuantity, i - queues[index][0]['time'], householdStatus[queues[index][0]['beneficiary']], volunteerWork[queues[index][0]['beneficiary']])
                # utility = getUtilityByQuantity(allocatedQuantity, i - queues[index][0]['time'])
                totalUtility += utility
                individualUtilities[queues[index][0]['beneficiary']] += utility
                if queues[index][0]['quantity'] == 0:
                    queues[index].popleft()
                    requestsInQueue -= 1
    return totalUtility, individualUtilities

def FCFSAllocationSimulation():
    totalUtility = 0
    individualUtilities = [0 for _ in range(5)]
    # Create one queue for all requests
    queue = collections.deque([])
    global donations
    global requests
    tempDonations = copy.deepcopy(donations)
    tempRequests = copy.deepcopy(requests)
    for i in range(1, 53):
        r = tempRequests[i-1]
        d = tempDonations[i-1]
        for request in r:
            queue.append(request)
        while d > 0 and len(queue) > 0:
            #Always allocate to the first request in the queue first
            allocatedQuantity = min(d, queue[0]['quantity'])
            d -= allocatedQuantity
            queue[0]['quantity'] -= allocatedQuantity
            utility = getUtility(allocatedQuantity, i - queue[0]['time'], householdStatus[queue[0]['beneficiary']], volunteerWork[queue[0]['beneficiary']])
            # utility = getUtilityByQuantity(allocatedQuantity, i - queue[0]['time'])
            totalUtility += utility
            individualUtilities[queue[0]['beneficiary']] += utility
            if queue[0]['quantity'] == 0:
                queue.popleft()
    return totalUtility, individualUtilities

def lyapunovSimulation():
    price = 1.00
    urgency = 7.00
    totalUtility = 0
    individualUtilities = [0 for _ in range(5)]
    # Create one requests queue for each beneficiary
    queues = [collections.deque([]) for i in range(5)]
    # Keep track of regret for each beneficiary
    regretScores = [0 for i in range(5)]
    # Keep track of temporal regret for each beneficiary
    temporalRegretScores = [0 for i in range(5)]
    # Keep track of all unfulfilled quantity for each beneficiary
    unfulfilledQuantities = [0 for i in range(5)]
    # Keep track of total number of requests in the queue to keep track of whether it is empty or not
    requestsInQueue = 0
    # Keep track of total quantity unfulfilled out of all beneficiaries
    totalUnfulfilledQuantity = 0
    global donations
    global requests
    tempDonations = copy.deepcopy(donations)
    tempRequests = copy.deepcopy(requests)
    for i in range(1,53):
        r = tempRequests[i-1]
        d = tempDonations[i-1]
        requestedQuantities = [0 for _ in range(5)]
        uScores = [0 for _ in range(5)]
        for request in r:
            queues[request['beneficiary']].append(request)
            requestsInQueue += 1
            unfulfilledQuantities[request['beneficiary']] += request['quantity']
            requestedQuantities[request['beneficiary']] += request['quantity']
            totalUnfulfilledQuantity += request['quantity']
        for j in range(5):
            # Calculate u
            requestCost = price * requestedQuantities[j]
            unsatisfiedRequestCost = price * unfulfilledQuantities[j] * urgency * householdStatus[j]
            w0 = 0.5
            w1 = 0.5
            w2 = 0.5
            w3 = 0.5
            u = 0.5*(w0*(w1*householdStatus[j]+w2*requestCost+w3*volunteerWork[j])+regretScores[j]+requestCost+temporalRegretScores[j]+unsatisfiedRequestCost)
            uScores[j] = u
            # Calculate regret for next round
            regretScores[j] = max(regretScores[j]+requestCost-u,0)
        # Determine allocation
        if d >= totalUnfulfilledQuantity:
            allocation = list(unfulfilledQuantities)
        else:
            uSum = 0
            for u in uScores:
                uSum += u
            for k in range(len(uScores)):
                uScores[k] /= uSum
            allocation = determineAllocation(d, uScores)
        for j in range(5):
            quantityAllocated = allocation[j]
            beneficiaryQueue = queues[j]
            unsatisfiedRequestCost = price * unfulfilledQuantities[j] * urgency * householdStatus[j]
            temporalRegretCostCompensated = 0
            while len(beneficiaryQueue) > 0 and quantityAllocated > 0:
                q = min(beneficiaryQueue[0]['quantity'], quantityAllocated)
                quantityAllocated -= q
                beneficiaryQueue[0]['quantity'] -= q
                unfulfilledQuantities[j] -= q
                totalUnfulfilledQuantity -= q
                temporalRegretCostCompensated += ((i-beneficiaryQueue[0]['time']+1)*price*q*urgency*householdStatus[j])
                utility = getUtility(q,i-beneficiaryQueue[0]['time'],householdStatus[j],volunteerWork[j])
                # utility = getUtilityByQuantity(q,i-beneficiaryQueue[0]['time'])
                totalUtility += utility
                individualUtilities[j] += utility
                if beneficiaryQueue[0]['quantity'] == 0:
                    beneficiaryQueue.popleft()
                    requestsInQueue -= 1
            # Calculate temporal regret for next round
            if regretScores[j] > 0:
                temporalRegretScores[j] = max(temporalRegretScores[j]+unsatisfiedRequestCost-temporalRegretCostCompensated,0)
            else:
                temporalRegretScores[j] = 0
    return totalUtility, individualUtilities

def determineAllocation(quantity, points):
    if len(points) == 0:
        return []
    allocations = [0 for _ in range(len(points))]
    n = 0
    while n != quantity:
        scores = [0 for _ in range(len(points))]
        for i in range(len(scores)):
            scores[i] = points[i]*(n+1) - (allocations[i]+1)
        maxIndex = 0
        for i in range(1,len(scores)):
            if scores[i] > scores[maxIndex]:
                maxIndex = i
        allocations[maxIndex] += 1
        n += 1
    return allocations

randomUtility, randomIndividualUtilities = randomAllocationSimulation()
print(randomUtility, randomIndividualUtilities)
FCFSUtility, FCFSIndividualUtilities = FCFSAllocationSimulation()
print(FCFSUtility, FCFSIndividualUtilities)
lyapunovUtility, lyapunovIndividualUtilities = lyapunovSimulation()
print(lyapunovUtility, lyapunovIndividualUtilities)
