from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.category import CategoryTypeModel, CategoryModel
from models.item import ItemModel
from models.request import RequestModel
from models.queue import QueueItemModel
from models.delivery import DeliveryModel
from models.recommendation import RecommendationModel
from models.user import UserModel
from models.credit import CreditModel
from models.score import ScoreModel
import datetime

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='password', server='localhost', database='fyp')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def getPreviousWeekDateTime():
    today = datetime.date.today()
    weekday = today.weekday()
    start_delta = datetime.timedelta(days=weekday, weeks=1)
    start_of_previous_week = today - start_delta
    start = start_of_previous_week + datetime.timedelta(days=0)
    end = start_of_previous_week + datetime.timedelta(days=6)
    return start, end

with app.app_context():
    previousWeekStart, previousWeekEnd = getPreviousWeekDateTime()
    categories = CategoryModel.get_all()
    for category in categories:
        categoryTypes = CategoryTypeModel.find_by_categoryID(category.id)
        for categoryType in categoryTypes:
            items = ItemModel.find_by_category_type(categoryType.id)
            availableItemQuantity = 0
            for item in items:
                availableItemQuantity += item.quantity
            queueItems = QueueItemModel.find_by_categoryTypeID(categoryType.id)
            userQueueItems = {}
            requestedQuantity = 0
            for queueItem in queueItems:
                requestedQuantity += queueItem.request.quantity
                if queueItem.userID not in userQueueItems:
                    userQueueItems[queueItem.userID] = [queueItem]
                else:
                    userQueueItems[queueItem.userID].append(queueItem)
                queueItem.allocation = 0
                queueItem.save_to_db()
            if availableItemQuantity >= requestedQuantity:
                for queueItem in queueItems:
                    queueItem.allocation = queueItem.request.quantity
                    queueItem.save_to_db()
                scores = ScoreModel.find_by_categoryType(categoryType.id)
                for score in scores:
                    score.regret = 0
                    score.temporalRegret = 0
                    score.save_to_db()
            else:
                utilities = {}
                requested = {}
                for userID in userQueueItems.keys():
                    if userID not in requested:
                        requested[userID] = 0
                    newQueueItems = filter(lambda x : previousWeekStart <= x.timeRequested <= previousWeekEnd,userQueueItems[userID])
                    previousQueueItems = filter(lambda x: x.timeRequested < previousWeekStart,userQueueItems[userID])
                    currentQuantity = 0
                    unfulfilledQuantity = 0
                    for queueItem in newQueueItems:
                        currentQuantity += queueItem.request.quantity
                    for queueItem in previousQueueItems:
                        unfulfilledQuantity += queueItem.quantity
                    unfulfilledQuantity += currentQuantity
                    requested[userID] += unfulfilledQuantity
                    score = ScoreModel.find_by_user_and_categoryType(userID, categoryTypeID)
                    if not score:
                        score = ScoreModel(userID, categoryTypeID)
                        score.save_to_db()
                    alpha = categoryType.price * currentQuantity
                    beta = categoryType.price * unfulfilledQuantity * category.urgency
                    u = 0.5 * (0.5*currentQuantity*categoryType.price + score.regret + alpha + score.temporalRegret + beta)
                    newRegret = max(score.regret+alpha-u,0)
                    newTemporalRegret = max(score.temporalRegret+beta-u,0)
                    score.regret = newRegret
                    score.temporalRegret = newTemporalRegret
                    score.save_to_db()
                    utilities[userID] = u
                userArr = []
                requestedQuantitiesArr = []
                uArr = []
                for userID in utilities.keys():
                    if utilities[userID] > 0:
                        userArr.append(userID)
                        requestedQuantitiesArr.append(requested[userID])
                        uArr.append(utilities[userID])
                allocations = allocationOptimizer(availableItemQuantity, requestedQuantitiesArr, uArr)
                for i, allocation in enumerate(allocations):
                    if allocation > 0:
                        userID = userArr[i]
                        userQueueItems = QueueItemModel.find_by_user(userID)
                        temp = allocation
                        j = 0
                        while temp > 0 and j < len(userQueueItems):
                            allocateAmount = min(temp, userQueueItems[j].request.quantity)
                            userQueueItems[j].allocation = allocateAmount
                            userQueueItems[j].save_to_db()
                            temp -= allocateAmount
                            j += 1
                
def allocationOptimizer(availableQuantity, requestedQuantities, utilities):
    solver = pywraplp.Solver('CommunitySelfHelpAllocationOptimizer', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    
    optimizationVariables = [[]]
    for i, r in enumerate(requestedQuantities):
        optimizationVariables[0].append(solver.NumVar(0, solver.infinity(), 'x'+str(i)))
    
    for i, r in enumerate(requestedQuantities):
        constraint1 = solver.Constraint(0, r)
        constraint1.SetCoefficient(optimizationVariables[0][i],1)
    
    constraint2 = solver.Constraint(availableQuantity, availableQuantity)
    for i, r in enumerate(requestedQuantities):
        constraint2.SetCoefficient(optimizationVariables[0][i],1)
    
    objective = solver.Objective()
    for i, r in enumerate(requestedQuantities):
        objective.SetCoefficient(optimizationVariables[0][i], utilities[i])
    
    objective.setMaximization()

    status = solver.Solve()
    output = [0 for _ in range(len(requestedQuantities))]
    if status == solver.OPTIMAL:
        print("- Status: Found Optimal Solution")
        for i, r in enumerate(requestedQuantities):
            output[i] = optimizationVariables[0][i].solution_value()
    elif status == solver.FEASIBLE:
        print('- Status: A potentially suboptimal solution was found.')
        for i, r in enumerate(requestedQuantities):
            output[i] = optimizationVariables[0][i].solution_value()
    else:
        print('- Status: The solver could not solve the problem. Please check your data')
    return output
