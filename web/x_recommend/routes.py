import traceback
from flask import Blueprint, app, request, jsonify, current_app
from sqlalchemy import func

from web.models import User, Interaction, Course, Lesson, Topic, Enrollment

x_recommend_bp = Blueprint('x_recommend_api', __name__)

import pandas as pd
import numpy as np
import implicit

x_recommend_bp = Blueprint('x_recommend_api', __name__)

# Load user-item interactions data from MySQL
""" def load_interactions_data():
    interactions_data = Interaction.query.all()

    # Check column names
    print(interactions_data.columns)

    # Inspect first few rows of the DataFrame
    print(interactions_data.head())

    # Check for missing values
    print(interactions_data.isnull().sum())

    # Check data types
    print(interactions_data.dtypes)

    return interactions_data """

def load_interactions_data():
    # Assuming Interaction is the model representing your interactions table
    interactions = Interaction.query.all()
    
    # Convert the list of Interaction objects to a DataFrame
    interactions_data = pd.DataFrame([{
                                        'id': interaction.id,
                                        'user_id': interaction.user_id,
                                       'course_id': interaction.course_id,
                                       'rating': interaction.rating,
                                       'views': interaction.views,
                                       'purchase': interaction.purchase,
                                       'like': interaction.like,
                                       'is_enrolled': interaction.is_enrolled} 
                                      for interaction in interactions])
    
    return interactions_data


def create_interaction_matrix(interactions_data):
    # Create a pivot table with all relevant interaction attributes
    interaction_matrix = pd.pivot_table(
        interactions_data, 
        values=['rating', 'views', 'purchase', 'like', 'is_enrolled'], 
        index='user_id', 
        #columns='course_id', 
        columns='id', 
        fill_value=0
        )
    return interaction_matrix


from scipy.sparse import csr_matrix
def convert_to_sparse_matrix(interaction_matrix):
    # Convert interaction matrix to CSR sparse matrix, to curtail the errors: AttributeError: 'numpy.ndarray' object has no attribute 'tocsr'
    sparse_interaction_matrix = csr_matrix(interaction_matrix.values)
    return sparse_interaction_matrix

""" # Convert interaction matrix to sparse matrix
def convert_to_sparse_matrix(interaction_matrix):
    sparse_interaction_matrix = interaction_matrix.values
    print(sparse_interaction_matrix)
    return sparse_interaction_matrix """

# Build the implicit feedback model using ALS (Alternating Least Squares)
def build_model(sparse_interaction_matrix):
    model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.01, iterations=50)
    model.fit(sparse_interaction_matrix.T)
    return model

# Get item details from item ID
def get_item_details(item_id):
    item = Course.query.get(item_id)
    if item:
        return {
            'category_id': item.category_id,
            'comment': item.comment,
            'created': item.created.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'desc': item.desc,
            'duration': item.duration,
            'fee': item.fee,
            'id': item.id,
            'image': item.image,
            'level': item.level,
            'rating': item.rating,
            'slug': item.slug,
            'title': item.title,
            'views': item.views
        }
    return None

@x_recommend_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    user_id = int(request.args.get('user_id'))

    # Load interactions data
    interactions_data = load_interactions_data()
    
    # Create interaction matrix
    interaction_matrix = create_interaction_matrix(interactions_data)
    
    # Convert interaction matrix to sparse matrix
    sparse_interaction_matrix = convert_to_sparse_matrix(interaction_matrix)
    
    # Build the model
    model = build_model(sparse_interaction_matrix)
    
    # Get recommendations
    recommendations = model.recommend(user_id, sparse_interaction_matrix, N=10)
    
    # Convert recommendation IDs to item details
    recommendation_items = [get_item_details(item_id) for item_id, _ in recommendations]
    
    return jsonify({'recommendations': recommendation_items})















from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from implicit.als import AlternatingLeastSquares
import numpy as np


from scipy.sparse import csr_matrix
from scipy.sparse import lil_matrix

from web.models import db, User, Course, Interaction

# Initialize recommendation model outside of the route function
model = AlternatingLeastSquares(factors=50)
# Or you can use CosineRecommender if ALS doesn't suit your needs
# model = CosineRecommender()

@x_recommend_bp.route('/recommend/<int:user_id>')
def recommend_courses(user_id):
    try:
        Session = sessionmaker(bind=db.engine)
        session = Session()

        # Fetch interaction data from the database and train the model
        interactions = session.query(Interaction).all()
        user_items = {}
        for interaction in interactions:
            user_items.setdefault(interaction.user_id, []).append(interaction.course_id)
            
        #data = model.fit(np.array(list( user_items.values())))
        data = model.fit( csr_matrix(np.array(list(user_items.values()) )) )

        # Get recommendations for the user
        recommendations = model.recommend(user_id, user_items, N=10)
        recommended_course_ids = [recommendation[0] for recommendation in recommendations]
        
        # Fetch course titles from the database
        recommended_courses = session.query(Course).filter(Course.id.in_(recommended_course_ids)).all()
        recommended_courses_data = [{'id': course.id, 'title': course.title} for course in recommended_courses]

        return jsonify(recommended_courses_data)
    
    except SQLAlchemyError as e:
        # Log the error for debugging purposes
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request. Please try again later.'}), 500
    
    except Exception as e:
        # Log the error for debugging purposes
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred. Please try again later. ({str(e)})'}), 500

@x_recommend_bp.route('/recommend_0/<int:user_id>')
def recommend_courses_0(user_id):
    try:
        Session = sessionmaker(bind=db.engine)
        session = Session()

        # Fetch interaction data from the database
        interactions = session.query(Interaction).all()
        user_items = {}
        for interaction in interactions:
            user_items.setdefault(interaction.user_id, []).append(interaction.course_id)
        
        # Convert user_items to CSR format
        user_item_matrix = csr_matrix((1, max(max(course_ids) for course_ids in user_items.values()) + 1), dtype=np.float32)
        for user_id, course_ids in user_items.items():
            user_item_matrix[user_id, course_ids] = 1

        # Train the model
        model.fit(user_item_matrix)

        # Get recommendations for the user
        recommendations = model.recommend(user_id, user_item_matrix, N=10)
        recommended_course_ids = [recommendation[0] for recommendation in recommendations]
        
        # Fetch course titles from the database
        recommended_courses = session.query(Course).filter(Course.id.in_(recommended_course_ids)).all()
        recommended_courses_data = [{'id': course.id, 'title': course.title} for course in recommended_courses]

        return jsonify(recommended_courses_data)
    
    except SQLAlchemyError as e:
        # Log the error for debugging purposes
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request. Please try again later.'}), 500
    
    except Exception as e:
        traceback.print_exc()
        # Log the error for debugging purposes
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred. Please try again later. ({str(e)})'}), 500
    
@x_recommend_bp.route('/recommend_1/<int:user_id>')
def recommend_courses_1(user_id):
    try:
        Session = sessionmaker(bind=db.engine)
        session = Session()

        # Fetch interaction data from the database
        interactions = session.query(Interaction).all()
        max_user_id = session.query(func.max(Interaction.user_id)).scalar()
        max_course_id = session.query(func.max(Interaction.course_id)).scalar()

        # Convert interaction data to a sparse matrix
        user_item_matrix = lil_matrix((max_user_id + 1, max_course_id + 1), dtype=np.float32)
        for interaction in interactions:
            user_item_matrix[interaction.user_id, interaction.course_id] = 1

        # Convert the lil_matrix to csr_matrix for efficient computation
        user_item_matrix = user_item_matrix.tocsr()

        # Train the model
        model.fit(user_item_matrix)

        # Get recommendations for the user
        user_ids = np.arange(max_user_id + 1)
        recommendations = model.recommend(user_id, user_item_matrix, N=10, filter_already_liked_items=True)

        recommended_course_ids = [recommendation[0] for recommendation in recommendations]
        
        # Fetch course titles from the database
        recommended_courses = session.query(Course).filter(Course.id.in_(recommended_course_ids)).all()
        recommended_courses_data = [{'id': course.id, 'title': course.title} for course in recommended_courses]

        return jsonify(recommended_courses_data)
    
    except SQLAlchemyError as e:
        # Log the error for debugging purposes
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request. Please try again later.'}), 500
    
    except Exception as e:
        traceback.print_exc()
        # Log the error for debugging purposes
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred. Please try again later. ({str(e)})'}), 500
    
@x_recommend_bp.route('/recommend_2/<int:user_id>')
def recommend_courses_2(user_id):
    try:
        Session = sessionmaker(bind=db.engine)
        session = Session()

        # Fetch interaction data from the database
        interactions = session.query(Interaction).all()
        max_user_id = session.query(func.max(Interaction.user_id)).scalar()
        max_course_id = session.query(func.max(Interaction.course_id)).scalar()

        # Initialize a dictionary to hold user-item interaction data
        user_items = {}
        for interaction in interactions:
            user_items.setdefault(interaction.user_id, []).append(interaction.course_id)

        # Ensure all user IDs are present in user_items
        for user_id in range(max_user_id + 1):
            user_items.setdefault(user_id, [])

        # Print debugging information
        print("Max User ID:", max_user_id)
        print("User Items Dictionary:", user_items)

        # Construct the user-item matrix from the user_items dictionary
        user_item_matrix = csr_matrix((max_user_id + 1, max_course_id + 1), dtype=np.float32)
        for user_id, item_ids in user_items.items():
            user_item_matrix[user_id, item_ids] = 1

        # Print additional debugging information about the matrix
        print("Matrix Shape:", user_item_matrix.shape)
        print("Number of Non-Zero Elements per Row:")
        print(user_item_matrix.getnnz(axis=1))

        # Train the model
        model.fit(user_item_matrix)

        # Get recommendations for the user
        user_ids = np.arange(max_user_id + 1)
        print("User IDs:", user_ids)
        recommendations = model.recommend(user_id, user_item_matrix, N=10, filter_already_liked_items=True)

        recommended_course_ids = [recommendation[0] for recommendation in recommendations]
        
        # Fetch course titles from the database
        recommended_courses = session.query(Course).filter(Course.id.in_(recommended_course_ids)).all()
        recommended_courses_data = [{'id': course.id, 'title': course.title} for course in recommended_courses]

        return jsonify(recommended_courses_data)
    
    except SQLAlchemyError as e:
        # Log the error for debugging purposes
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request. Please try again later.'}), 500
    
    except Exception as e:
        traceback.print_exc()
        # Log the error for debugging purposes
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred. Please try again later. ({str(e)})'}), 500