from rest_framework import serializers
from .models import User, Book, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_of_membership', 'is_active']
        read_only_fields = ['date_of_membership']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'published_date', 'copies_available']

class TransactionSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Transaction
        fields = ['id', 'book', 'book_title', 'user', 'user_username', 'checkout_date', 'return_date', 'is_returned']
        read_only_fields = ['checkout_date', 'return_date', 'is_returned']