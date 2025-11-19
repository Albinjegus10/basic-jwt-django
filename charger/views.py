from django.shortcuts import render
from rest_framework.permissions import AllowAny


def hello(request):
    return render(request,"index.html")

from django.shortcuts import render
from .forms import SimpleForm

def simple_form(request):
    form = SimpleForm()
    if request.method == 'POST':
        form = SimpleForm(request.POST)
        if form.is_valid():
            #save data in db
            return render(request, 'form_success.html')
        else:
            form = SimpleForm()
    return render(request, 'simple_form.html', {'form': form})



from django.shortcuts import render, redirect
from .models import Task
from .forms import TaskForm


def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('task_list')  # Redirect only after saving
    else:
        form = TaskForm()
    return render(request, 'add_task.html', {'form': form})


def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'task_list.html', {'tasks': tasks})


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Book2
from .serializers import BookSerializer

class BookListCreateAPIView(APIView):

    def get(self, request):
        books = Book2.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailAPIView(APIView):
    permission_classes = [AllowAny]
    def get_object(self, pk):
        try:
            return Book2.objects.get(pk=pk)
        except Book2.DoesNotExist:
            return None

    def get(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookSerializer(book, data=request.data)  # full update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        book.delete()
        return Response({"message": "Book deleted"}, status=status.HTTP_204_NO_CONTENT)


from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []


    def post(self, request):
        """
        Authenticate user and return JWT tokens
        """
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Please provide both username and password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'kirubaname': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """
        Create a new user and return JWT tokens
        """
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'user': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        # Simply accept the refresh token and return success
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token required"},
                            status=status.HTTP_400_BAD_REQUEST)

        # No actual blacklisting — just pretend logout succeeded
        return Response({"message": "Successfully logged out"}, status=200)



class RefreshTokenView(APIView):
    permission_classes = [AllowAny]  # Allows anyone to call
    authentication_classes = []

    def post(self, request):
        """
        Refresh access token
        """
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {'error': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

from .models import Item
from .serializers import ItemSerializer


class ItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """
        Retrieve a single item by pk or list all items.
        Requires valid JWT token.
        """
        try:
            if pk is not None:
                item = get_object_or_404(Item, pk=pk)
                serializer = ItemSerializer(item)
                return Response(serializer.data)

            items = Item.objects.all()
            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Create a new item.
        Requires valid JWT token.
        """
        try:
            serializer = ItemSerializer(data=request.data)

            # Check for existing item
            unique_fields = ['name', 'identifier']  # Adjust based on your Item model
            filter_kwargs = {
                field: request.data.get(field)
                for field in unique_fields
                if field in request.data
            }

            if filter_kwargs and Item.objects.filter(**filter_kwargs).exists():
                return Response(
                    {'error': 'An item with these details already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        """
        Update an existing item.
        Requires valid JWT token.
        """
        try:
            item = get_object_or_404(Item, pk=pk)
            serializer = ItemSerializer(
                instance=item,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        """
        Delete an item.
        Requires valid JWT token.
        """
        try:
            item = get_object_or_404(Item, pk=pk)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



