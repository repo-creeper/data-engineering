# import packages
import pickle
from sklearn.neighbors import NearestNeighbors
import numpy
import json
import pandas as pd
from flask import Blueprint, jsonify, request, render_template

from app.models import db, parse_records, Cabinet

recommend_routes = Blueprint("recommend_routes", __name__)

# open pickle with trained model
with open('./data/model_pickle', 'rb') as f:
    pickle = pickle.load(f)

# nearest neighbor mopdel
nn = NearestNeighbors(metric='cosine', algorithm='brute',
                      n_neighbors=20, n_jobs=-1)

nn.fit(pickle)

negative_list = ['anxious', 'dizzy', 'dry eyes',
                 'dry mouth', 'headache', 'paranoid']
effect_list = ['creative', 'energetic', 'euphoric',
               'focused', 'happy', 'hungry', 'relaxed', 'sleepy']
ailment_list = ['anxiety', 'depression', 'fatigue',
                'headaches', 'lack of appetite', 'pain', 'stress']

columns = [
    'anxious',
    'dizzy',
    'dry eyes',
    'dry mouth',
    'headache',
    'paranoid',
    'creative',
    'energetic',
    'euphoric',
    'focused',
    'happy',
    'hungry',
    'relaxed',
    'sleepy',
    'anxiety',
    'depression',
    'fatigue',
    'headaches',
    'lack of appetite',
    'pain',
    'stress']


@recommend_routes.route("/cabinet")
def cabinet():
    db_cabinet = Cabinet.query.all()
    cabinet_response = parse_records(db_cabinet)
    return jsonify(cabinet_response)

# functional /recommend endpoint as deployed on heroku
@recommend_routes.route("/recommend", methods=['GET', 'POST'])
def recommend():
    """
    creates list with top n recommended strains.

    Paramaters
    __________

    request: dictionary (json object)
        list of user's desired effects listed in order of user ranking.
        {
            "effects":[],
            "negatives":[],
            "ailments":[]
        }
    n: int, optional
        number of recommendations to return, default 10.

    Returns
    _______

    list_strains: python list of n recommended strains.
    """
    desired_dict = request.json
    n = 10
    effects, negatives, ailments = (
        desired_dict.get("effects"),
        desired_dict.get("negatives"),
        desired_dict.get("ailments")
    )
    effects = [effect.lower() for effect in effects]
    negatives = [negative.lower() for negative in negatives]
    ailments = [ailment.lower() for ailment in ailments]



    for index, effect in enumerate(effects):
       if effect in columns:
            effects[index] = columns.index(effect)

    for index, negative in enumerate(negatives):
       if negative in columns:
            negatives[index] = columns.index(negative)

    for index, ailment in enumerate(ailments):
       if ailment in columns:
            ailments[index] = columns.index(ailment)

    vector = [
       0 for _ in range(len(columns))
       ]

    weight = 100

    for index in effects:
       if isinstance(index, int):
            vector[index] = weight
            weight *= .8
            weight = int(weight)

    weight = 100

    for index in negatives:
       if isinstance(index, int):
            vector[index] = weight
            weight *= .8
            weight = int(weight)

    weight = 100

    for index in ailments:
       if isinstance(index, int):
            vector[index] = weight
            weight *= .8
            weight = int(weight)

    data = numpy.array(vector)
    request_series = pd.Series(data, index=columns)
    distance, neighbors = nn.kneighbors([request_series])

    list_strains = []
    for points in neighbors:
        for index in points:
            list_strains.append(index)
    result = [
        {"id": str(val)}
        for val in list_strains[:n]
    ]
    return jsonify(result)


# /recommend clone to test for-loop return error when deployed to heroku
@recommend_routes.route("/testing", methods=['GET', 'POST'])
def recommender():
    """
    creates list with top n recommended strains.
    Paramaters
    __________
    request: dictionary (json object)
        list of user's desired effects listed in order of user ranking.
        {
            "effects":[],
            "negatives":[],
            "ailments":[]
        }
    n: int, optional
        number of recommendations to return, default 10.
    Returns
    _______
    list_strains: python list of n recommended strains.
    """
    desired_dict = request.json
    n = 10
    effects, negatives, ailments = (
        desired_dict.get("effects"),
        desired_dict.get("negatives"),
        desired_dict.get("ailments")
    )

    effects = [effect.lower() for effect in effects]
    negatives = [negative.lower() for negative in negatives]
    ailments = [ailment.lower() for ailment in ailments]
    for index, effect in enumerate(effects):
       if effect in columns:
           effects[index] = columns.index(effect)
    for index, negative in enumerate(negatives):
       if negative in columns:
           negatives[index] = columns.index(negative)
    for index, ailment in enumerate(ailments):
       if ailment in columns:
           ailments[index] = columns.index(ailment)
    vector = [
        0 for _ in range(len(columns))
    ]
    weight = 100
    for index in effects:
       if isinstance(index, int):
           vector[index] = weight
           weight *= .8
           weight = int(weight)
    weight = 100
    for index in negatives:
       if isinstance(index, int):
           vector[index] = weight
           weight *= .8
           weight = int(weight)
    weight = 100
    for index in ailments:
       if isinstance(index, int):
           vector[index] = weight
           weight *= .8
           weight = int(weight)
    data = numpy.array(vector)
    request_series = pd.Series(data, index=columns)
    distance, neighbors = nn.kneighbors([request_series])
    list_strains = []
    for points in neighbors:
        for index in points:
            list_strains.append(index)
    result = [
        {"id": str(val)}
        for val in list_strains[:n]
    ]
    return_list = [
        str(val)
        for val in list_strains[:n]
    ]

    records = parse_records(Cabinet.query.filter(
        Cabinet.model_id.in_(return_list)).all())

    return jsonify(records)


