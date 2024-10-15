from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Book, Transaction
from .serializers import UserSerializer, BookSerializer, TransactionSerializer
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'author', 'isbn']
    filterset_fields = ['copies_available']

    @action(detail=False, methods=['get'])
    def available(self, request):
        available_books = Book.objects.filter(copies_available__gt=0)
        serializer = self.get_serializer(available_books, many=True)
        return Response(serializer.data)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        book_id = request.data.get('book')
        user_id = request.data.get('user')
        
        try:
            book = Book.objects.get(id=book_id)
            user = User.objects.get(id=user_id)
        except (Book.DoesNotExist, User.DoesNotExist):
            return Response({"error": "Book or User not found"}, status=status.HTTP_404_NOT_FOUND)

        if book.copies_available > 0:
            # Check if user already has a copy of this book
            existing_transaction = Transaction.objects.filter(
                book=book, 
                user=user, 
                is_returned=False
            ).first()
            
            if existing_transaction:
                return Response({"error": "User already has a copy of this book"}, status=status.HTTP_400_BAD_REQUEST)
            
            transaction = Transaction.objects.create(book=book, user=user)
            book.copies_available -= 1
            book.save()
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "No copies available"}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        transaction = self.get_object()
        if not transaction.is_returned:
            transaction.is_returned = True
            transaction.return_date = timezone.now()
            transaction.save()
            transaction.book.copies_available += 1
            transaction.book.save()
            return Response(TransactionSerializer(transaction).data)
        else:
            return Response({"error": "Book already returned"}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'])
    def user_history(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        transactions = Transaction.objects.filter(user_id=user_id)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)