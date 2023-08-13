from django.shortcuts import render, redirect
from pymongo import MongoClient
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

# Create your views here.

client = MongoClient('')
db = client.mubadarah_database
video = db.demovideos
user = db.user



@api_view(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate user against Django admin accounts
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:
                return redirect('dashboard')  # Redirect to the 'dashboard' view
            else:
                # User is valid, but is not a staff member
                print('not staff')
        else:
            # User is not valid
            print('not valid')
    else:
        print('not post')

    return render(request, 'index.html')




# I want to retrieve count of comments in video from mubadarah_database in video collection 
# and display it in the dashboard
def dashboard(request):
    pipeline = [
        {
            "$match": {
                "comments": {
                    "$elemMatch": {"IsApproved": "False"}
                }
            }
        },
        {
            "$addFields": {
                "comments": {
                    "$filter": {
                        "input": "$comments",
                        "as": "comment",
                        "cond": {"$eq": ["$$comment.IsApproved", "False"]}
                    }
                }
            }
        }
    ]

    content = list(video.aggregate(pipeline))
    return render(request, 'table.html', {"content": content})

@api_view(['GET'])
def approve(request, video_id, comment_id):
    video.update_one({"_id": video_id, "comments.comment_id": comment_id}, {"$set": {"comments.$.IsApproved": "True"}})
    return redirect('dashboard')  # Redirect to the 'dashboard' view

@api_view(['GET'])
def delete(request, video_id, comment_id):
    video.update_one({"_id": video_id}, {"$pull": {"comments": {"comment_id": comment_id}}})
    return redirect('dashboard')  # Redirect to the 'dashboard' view

@api_view(['GET'])
def user_dashboard(request):
    number_of_users = user.count_documents({})
    number_of_verified_emails = user.count_documents({"email_verified": True})
    number_of_UNverified_emails = user.count_documents({"email_verified": {"$exists": False}})
    number_of_female = user.count_documents({"data.gender": True})
    number_of_male = user.count_documents({"data.gender": False})


    counties_groupby = list(user.aggregate([{'$group': {'_id': '$data.country','count': {'$sum': 1}}}]))
    counties_labels = [entry['_id'] for entry in counties_groupby]
    counties_counts = [entry['count'] for entry in counties_groupby]

    nationality_groupby = list(user.aggregate([{'$group': {'_id': '$data.nationality','count': {'$sum': 1}}}]))
    nationality_labels = [entry['_id'] for entry in nationality_groupby]
    nationality_counts = [entry['count'] for entry in nationality_groupby]


    context = {"number_of_users":number_of_users, "number_of_verified_emails":number_of_verified_emails,
               "number_of_UNverified_emails":number_of_UNverified_emails, "number_of_female":number_of_female, 
               "number_of_male":number_of_male, "counties_labels":counties_labels, "counties_counts":counties_counts, 
               "nationality_labels":nationality_labels, "nationality_counts":nationality_counts}
    
    return render(request, 'Userindex.html',context)
