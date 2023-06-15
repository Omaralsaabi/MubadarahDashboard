from django.shortcuts import render, redirect
from pymongo import MongoClient
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

# Create your views here.

client = MongoClient('mongodb+srv://test:test@mubadarahcluster.fphpucp.mongodb.net/')
db = client.mubadarah_database
video = db.demovideos




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
