from rest_framework import serializers
from .models import User, Book, Transaction
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'date_of_membership', 'is_active']
        read_only_fields = ['date_of_membership', 'is_active']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)

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