from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """BookList serializer"""
    class Meta:
        model = Book
        fields = ('title', 'summary', 'isbn', 'pic', 'author', 'language')
