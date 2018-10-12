from django.contrib import admin
from catalog.models import Author, Genre, Book, BookInstance, Language, Profile
from django.contrib.auth.models import User

admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Profile)


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 1


class BookInline(admin.StackedInline):
    model = Book
    extra = 1


class UserInline(admin.StackedInline):
    model = User
    extra = 1


# Register the Admin classes for Author using the decorator
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]


# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]


# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')
    
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

