from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.category import CategoryTypeModel
from models.item import ItemModel, ExcessModel
from models.request import RequestModel, UnmetModel
from models.queue import QueueItemModel
from models.delivery import DeliveryModel
from models.recommendation import RecommendationModel
from models.user import UserModel
from models.credit import CreditModel
from models.score import ScoreModel
from ortools.linear_solver import pywraplp
from math import radians, cos, sin, asin, sqrt
import gc
import warnings
warnings.filterwarnings("ignore")

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='password', server='localhost', database='fyp')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    categoryTypes = CategoryTypeModel.get_all()
    ExcessModel.clear()
    UnmetModel.clear()
    RecommendationModel.clear()
    for categoryType in categoryTypes:
        items = ItemModel.get_available_items_by_category_type(categoryType.id)
        queueItems = QueueItemModel.find_by_categoryTypeID(categoryType.id)
        queueItems = filter(lambda x : x.allocation > 0, queueItems)
        itemQuantities = []
        queueItemQuantities = []
        distances = {}
        donatedQuantity = 0
        requestedQuantity = 0
        for item, i in enumerate(items):
            itemQuantities.append(item.quantity)
            donatedQuantity += item.quantity
            for queueItem, j in enumerate(queueItems):
                if len(queueItemQuantities) < len(queueItems):
                    queueItemQuantities.append(queueItem.allocation)
                    requestedQuantity += queueItem.allocation
                donor = item.user
                beneficiary = queueItem.user
                distances[i][j] = haversine(donor.lng, donor.lat, beneficiary.lng, beneficiary.lat)
        if donatedQuantity > requestedQuantity:
            queueItemQuantities.append(1000000)
            for item, i in enumerate(items):
                donor = item.user
                distances[i][len(queueItemQuantities) - 1] = haversine(donor.lng, donor.lat, 0, -90)
            allocations = deliveryOptimizer(itemQuantities, queueItemQuantities, distances)
            allocations = filter(lambda x: x['queueItemIndex'] != len(queueItemQuantities) - 1, allocations)
            for allocation in allocations:
                itemQuantities[allocation['itemIndex']] -= allocation['donationQuantity']
                recommendation = RecommendationModel(queueItemID=queueItems[allocation['queueItemIndex']].id,
                itemID=items[allocation['itemIndex']].id,
                categoryTypeID=categoryType.id,
                quantity=allocation['donationQuantity'])
                recommendation.save_to_db()
            for itemQuantity, i in enumerate(itemQuantities):
                if itemQuantity > 0:
                    excess = ExcessModel(items[i].id,itemQuantity)
                    excess.save_to_db()
        elif donatedQuantity == requestedQuantity:
            allocations = deliveryOptimizer(itemQuantities, queueItemQuantities, distances)
            for allocation in allocations:
                recommendation = RecommendationModel(queueItemID=queueItems[allocation['queueItemIndex']].id,
                itemID=items[allocation['itemIndex']].id,
                categoryTypeID=categoryType.id,
                quantity=allocation['donationQuantity'])
                recommendation.save_to_db()
        else:
            allocations = deliveryOptimizer(itemQuantities, queueItemQuantities, distances)
            for allocation in allocations:
                queueItemQuantities[allocation['queueItemIndex']] -= allocation['donationQuantity']
                recommendation = RecommendationModel(queueItemID=queueItems[allocation['queueItemIndex']].id,
                itemID=items[allocation['itemIndex']].id,
                categoryTypeID=categoryType.id,
                quantity=allocation['donationQuantity'])
                recommendation.save_to_db()
            for queueItemQuantity, i in enumerate(queueItemQuantities):
                if queueItemQuantity > 0:
                    unmet = UnmetModel(requestID=queueItems[i].requestID,quantity=queueItemQuantity)
                    unmet.save_to_db()

def haversine(lng1, lat1, lng2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])

    # haversine formula 
    dlng = lng2 - lng1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def deliveryOptimizer(donatedQuantities, requestedQuantities, distances):
	'''
	Variables:
		- donatedQuantities = [5,1,1,1,2]
		- requestedQuantities = [5,5]
        - distances = {0:{0:234,1:127},1:{0:329,1:653},2:{0:98,1:472},3:{0:343,1:872},4:{0:463,1:782}}
	'''
	# --
	solver = pywraplp.Solver('CommunitySelfHelpDeliveryOptimizer', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
	# --
	# Creating the optimization variables
	optimizationVariables = []
	for i,d in enumerate(donatedQuantities):
		donorRecipients = []
		for j,r in enumerate(requestedQuantities):
			# Create the variables and let them take on any non-negative value.
			donorRecipients.append(solver.NumVar(0, solver.infinity(), 'x'+str(i)+str(j)))
		optimizationVariables.append(donorRecipients)
	# --
	# Constaint 1: sum(optimizationVariables[all][j]) <=requestedQuantities[j])
	for j,r in enumerate(requestedQuantities):
		constraint1 = solver.Constraint(0, r)
		for i,d in enumerate(donatedQuantities):
			constraint1.SetCoefficient(optimizationVariables[i][j], 1)
	# --
	# Constaint 2: sum(optimizationVariables[i][all]) == donatedQuantities[i])
	for i,d in enumerate(donatedQuantities):
		constraint2 = solver.Constraint(d, d)
		for j,r in enumerate(requestedQuantities):
			constraint2.SetCoefficient(optimizationVariables[i][j], 1)
	# --
	# Objective function: min(sum(d * optimizationVariables[all][all]))
	objective = solver.Objective()
	for i,d in enumerate(donatedQuantities):
		for j,r in enumerate(requestedQuantities):
			objective.SetCoefficient(optimizationVariables[i][j], distances[i][j])
	#Set to find minimum
	objective.SetMinimization()
	# --
	status = solver.Solve()
	output = list()
	if status == solver.OPTIMAL:
		print("- Status: Found Optimal Solution")
		for i,d in enumerate(donatedQuantities):
			for j,r in enumerate(requestedQuantities):
				donationQuantity = optimizationVariables[i][j].solution_value()
				if donationQuantity > 0:
					output.append({'itemIndex':i,'queueItemIndex':j,'donationQuantity':donationQuantity})
	elif status == solver.FEASIBLE:
		print('- Status: A potentially suboptimal solution was found.')
		for i,d in enumerate(donatedQuantities):
			for j,r in enumerate(requestedQuantities):
				donationQuantity = optimizationVariables[i][j].solution_value()
				if donationQuantity > 0:
					output.append({'itemIndex':i,'queueItemIndex':j,'donationQuantity':donationQuantity})
	else:
		print('- Status: The solver could not solve the problem. Please check your data')
	return output