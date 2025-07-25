# Django imports
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import IntegrityError
from django.contrib.auth import login as auth_login, logout, authenticate


# Third-party imports
import base64
import face_recognition
import os
import cv2
import numpy as np
import pickle

# Local imports
from .models import UserImages, Attendance


# Create your views here.
@login_required
def register(request):
    # User registration with facial recognition
    if request.method == 'POST':
        username = request.POST.get('username')
        face_image_data = request.POST.get('face_image')
        identification_number = request.POST.get('identification_number')
        user_type = request.POST.get('user_type')

        # Validate that all required fields are provided
        if not username or not face_image_data or not identification_number or not user_type:
            return JsonResponse({'status': 'error', 'message': 'All fields are required!'})

        # Check if identification number or username already exists in the system
        if UserImages.objects.filter(identification_number=identification_number).exists():
            return JsonResponse({'status': 'error', 'message': 'Identification number already registered!'})

        if User.objects.filter(username__iexact=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already exists!'})

        # Process and validate the facial image data
        try:
            face_image_data = face_image_data.split(',')[1]
            face_image_binary = base64.b64decode(face_image_data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid facial image data!'})

        try:
            nparr = np.frombuffer(face_image_binary, np.uint8)
            face_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            face_encoding = face_recognition.face_encodings(face_image)
            if not face_encoding:
                return JsonResponse({'status': 'error', 'message': 'No face detected!'})
            face_encoding = face_encoding[0]
            face_encoding_serialized = pickle.dumps(face_encoding)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Error processing facial image!'})

        # Create a new user in the Django authentication system
        user = User(username=username)
        user.save()

        UserImages.objects.create(
            user=user,
            face_image=face_image_binary,
            identification_number=identification_number,
            user_type=user_type,
            face_encoding=face_encoding_serialized
        )

        return JsonResponse({'status': 'success', 'message': 'User created successfully!', 'redirect': '/users/'})

    return render(request, 'register.html')


@login_required
def signup(request):
    # Display the registration form to the user
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        # Check if the passwords match
        if request.POST['password1'] == request.POST['password2']:
            try:
                # Save the new user
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                auth_login(request, user)
                return redirect('main')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Username already exists.'
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Passwords do not match.'
        })


def login(request):
    # Get the data sent from the form
    if request.method == 'POST':
        face_image_data = request.POST.get('face_image')
        attendance_type = request.POST.get('attendance_type')

        # Validate that a face image was provided
        if not face_image_data:
            return JsonResponse({'status': 'error', 'message': 'Face image is required!'})

        try:
            # Decode the uploaded face image from base64
            face_image_data = face_image_data.split(',')[1]
            uploaded_image = base64.b64decode(face_image_data)
            nparr = np.frombuffer(uploaded_image, np.uint8)
            uploaded_face_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid facial image data!'})

        # Facial encoding with face_recognition
        try:
            uploaded_face_encoding = face_recognition.face_encodings(uploaded_face_image)
            if not uploaded_face_encoding:
                return JsonResponse({'status': 'error', 'message': 'Face not detected!'})
            uploaded_face_encoding = uploaded_face_encoding[0]
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Error processing facial image!'})

        # Attempt to match the uploaded face with existing users using stored encodings
        identified_user = None
        all_user_images = UserImages.objects.exclude(face_encoding__isnull=True)

        for user_image in all_user_images:
            try:
                if not user_image.face_encoding:
                    continue
                stored_face_encoding = pickle.loads(user_image.face_encoding)
                match = face_recognition.compare_faces(
                    [stored_face_encoding], uploaded_face_encoding, tolerance=0.5)
                if match[0]:
                    identified_user = user_image.user
                    break  # Stop searching if a match is found
            except Exception:
                continue  # Skip this user if there is any error processing their encoding

        if not identified_user:
            return JsonResponse({'status': 'error', 'message': 'No matching user found!'})

        # Register attendance if requested
        if attendance_type in [Attendance.ENTRY, Attendance.EXIT]:
            try:
                # Create a new attendance record for identified user
                attendance = Attendance.objects.create(
                    user=identified_user,
                    attendance_type=attendance_type
                )
                return JsonResponse({
                    'status': 'success',
                    'message': 'Attendance successfully registered!',
                    'username': identified_user.username
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error recording attendance: {str(e)}'
                })
        # If no attendance registration, just return a successful login
        return JsonResponse({
            'status': 'success',
            'message': f'Welcome {identified_user.username}!',
            'username': identified_user.username
        })

    return render(request, 'login.html')


def signin(request):
    # Display the login form to the user
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        # Authenticate the user
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect.'
            })
        else:
            auth_login(request, user)
            return redirect('main')


@login_required
def main(request):
    # Consult attendance data
    attendance_data = Attendance.objects.select_related('user').all().order_by('-timestamp')
    # Data processing
    attendance_list = []
    for attendance in attendance_data:
        try:
            user_image = UserImages.objects.get(user=attendance.user)
            number_identification = user_image.identification_number
            user_type = user_image.user_type
        except UserImages.DoesNotExist:
            number_identification = "N/A"
            user_type = "student"
        # Converting to local timezone
        local_timestamp = timezone.localtime(attendance.timestamp, timezone=timezone.get_default_timezone())
        # Building the data dictionary
        attendance_list.append({
            'id': attendance.id,
            'number_identification': number_identification,
            'fullname': attendance.user.username,
            'type_register': attendance.attendance_type,
            'timestamp': local_timestamp,
            'user_type': user_type
        })
    # Context preparetion redering
    context = {
        'attendance_list': attendance_list
    }
    return render(request, 'main.html', context)


@login_required
def users(request):
    # Get all users with related user data
    users = UserImages.objects.select_related('user').all()
    for user in users:
        if user.face_image:
            user.face_image_base64 = base64.b64encode(user.face_image).decode('utf-8')
        else:
            user.face_image_base64 = None    
    return render(request, 'users.html', {'users': users})


@login_required
def delete(request, pk):
    # Get user extended data by primary key
    user_img = get_object_or_404(UserImages, pk=pk)
    user = user_img.user

    # Delete user data
    user_img.delete()
    user.delete()

    return redirect('users')


@login_required
def remove(request, pk):
    # Get attendance data by primary key
    attendance_data = get_object_or_404(Attendance, pk=pk)
    
    # Delete attendance data
    attendance_data.delete()

    return redirect('main')


@login_required
def update(request, pk):
    # Get user extended data by primary key
    user_img = get_object_or_404(UserImages, pk=pk)
    user = user_img.user

    if request.method == 'POST':
        # Get the data sent from the form
        username = request.POST.get('username')
        identification_number = request.POST.get('identification_number')
        user_type = request.POST.get('user_type')
        face_image_data = request.POST.get('face_image')

        # Validate that all required text fields are provided
        if not username or not identification_number or not user_type:
            return JsonResponse({'status': 'error', 'message': 'All text fields are required!'})

        # Check if identification number or username already exists for another user
        if UserImages.objects.filter(identification_number=identification_number).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': 'This identification number is already registered to another user!'})

        if User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
            return JsonResponse({'status': 'error', 'message': 'This username is already taken by another user!'})

        # Update text data
        user.username = username
        user_img.identification_number = identification_number
        user_img.user_type = user_type

        # If a new face image was sent, update it
        if face_image_data:
            try:
                # Process and validate the facial image data
                face_image_data = face_image_data.split(',')[1]
                face_image_binary = base64.b64decode(face_image_data)
                user_img.face_image = face_image_binary
            except (IndexError, ValueError, TypeError) as e:
                return JsonResponse({'status': 'error', 'message': 'Invalid facial image data!'})

        # Save updated user data
        user.save()
        user_img.save()

        return JsonResponse({'status': 'success', 'message': 'User updated successfully!', 'redirect': '/users/'})

    return render(request, 'update.html', {'user_img': user_img})

def gen_frame():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 4)
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    cap.release()

def video(request):
    return StreamingHttpResponse(gen_frame(), content_type='multipart/x-mixed-replace; boundary=frame')

@login_required
def signout(request):
    # Log out the user
    logout(request)
    return redirect('login')