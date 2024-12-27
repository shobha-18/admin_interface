from django.shortcuts import render,redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions,status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser, AndroidApp, UserTask
from .serializers import UserSerializer, AndroidAppSerializer, UserTaskSerializer,MyTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import JsonResponse
from django.views import View
from rest_framework.decorators import action,api_view
from django.shortcuts import get_object_or_404


# Admin Views
# class AdminAndroidAppViewSet(viewsets.ModelViewSet):
#     queryset = AndroidApp.objects.all()
#     serializer_class = AndroidAppSerializer
#     permission_classes = [permissions.IsAdminUser]
class AndroidAppViewSet(viewsets.ViewSet):
    def get_permissions(self):
       if self.action in ['list','retrieve''create','update','delete']:  # Check explicitly for 'create' action
        return [AllowAny()]
       return [IsAuthenticated()]  # Actions without authentication
            

    def list(self, request):
        apps = AndroidApp.objects.all()
        serializer = AndroidAppSerializer(apps, many=True)
        return Response(serializer.data)
    def create(self,request):
        if request.method == 'POST':
            serializer = AndroidAppSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def create(self, request):
    #     serializer = AndroidAppSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def retrieve(self, request, pk=None):
    #     app = get_object_or_404(AndroidApp, pk=pk)
    #     serializer = AndroidAppSerializer(app)
    #     return Response(serializer.data)

    # def update(self, request, pk=None):
    #     app = get_object_or_404(AndroidApp, pk=pk)
    #     serializer = AndroidAppSerializer(app, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def destroy(self, request, pk=None):
    #     app = get_object_or_404(AndroidApp, pk=pk)
    #     app.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def add_points(self, request, pk=None):
        app = get_object_or_404(AndroidApp, pk=pk)
        points = request.data.get('points')
        if points is not None:
            try:
                app.points += int(points)  # Increment the points
                app.save()
                return Response({"status": "Points updated", "points": app.points})
            except ValueError:
                return Response({"error": "Invalid points value"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Points not provided"}, status=status.HTTP_400_BAD_REQUEST)

# Render HTML Views
def app_list(request):
    return render(request, 'app_list.html')

def app_detail(request, pk):
    # Retrieve the app by its primary key (pk)
    app = get_object_or_404(AndroidApp, pk=pk)

    # Render the index.html template with the app data
    return render(request, 'index.html', {'app': app})
class User_detailsView(View):
    def get(self, request):
        apps = AndroidApp.objects.all()
        return render(request, 'user_profile.html', {'apps': apps})
class add_app(View):
    def get(self, request):
        # Ensure the view returns an HttpResponse
        return render(request, 'add_app.html')

# @api_view(['POST'])
# def create(request):
#     if request.method == 'POST':
#         serializer = AndroidAppSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# User Views
@csrf_exempt
def SignupView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        retype_password = request.POST.get('password')
        is_admin = request.POST.get('is_admin') == 'on'  

        user = CustomUser.objects.create_user(username=username, password=password)
        if is_admin:
            user.is_admin = True  
            user.is_staff = True  
            user.save()

        return redirect('logindata')
    return render(request, 'signup.html')


# Login View: Authenticate a user and return a token
class token_view(APIView):
    def post(self, request):
        user = CustomUser.objects.get(username=request.data['username'])
        if user.check_password(request.data['password']):
            refresh = RefreshToken.for_user(user)
            return Response({"refresh": str(refresh), "access": str(refresh.access_token)})
        return Response({"detail": "Invalid credentials"}, status=400)
@csrf_exempt
def logindata(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)  # Log the user in

            # Debugging
            print(f"Username: {user.username}, is_admin: {getattr(user, 'is_admin', None)}")

            if getattr(user, 'is_admin', False):  # Check if the user is admin
                return redirect('android')  # Redirect to /api/android/ directly
            else:
                return redirect('user-tasks')  # Redirect to user page
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


# class UserProfileView(View):
#     # permission_classes = [IsAuthenticated]

#       def get(self, request):
#         user = request.user  # Get the current logged-in user
#         serializer = UserSerializer(user)  # Serialize the user data
#         return Response(serializer.data) 
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user  # Get the current logged-in user
        serializer = UserSerializer(user)  # Serialize the user data
        return JsonResponse(serializer.data)




class UserTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Fetch the CustomUser instance
            custom_user = CustomUser.objects.get(username=request.user.username)  # Use the authenticated user's username
            
            # Fetch the AndroidApp instance dynamically from the request payload
            app_name = request.data.get('app_name')  # Ensure 'app_name' is sent in the request data
            if not app_name:
                return Response({'error': 'App name is required'}, status=400)
            
            android_app = AndroidApp.objects.get(name=app_name)  # Query dynamically using app_name
            
            # Create the UserTask object
            task = UserTask.objects.create(
                user=custom_user,
                app=android_app,
                screenshot=request.data['screenshot'],  # Assuming screenshot is passed in the request
            )
            
            return Response(UserTaskSerializer(task).data, status=201)
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except AndroidApp.DoesNotExist:
            return Response({'error': f'AndroidApp with name "{app_name}" not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "Successfully logged out."})

    def get(self, request):  # Allow GET method as well (not recommended for logout)
        logout(request)
        return Response({"detail": "Successfully logged out."})


