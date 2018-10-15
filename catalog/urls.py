from django.urls import path
from catalog import views
from django.views.generic import TemplateView


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', TemplateView.as_view(template_name='catalog/about.html'), name='about'),
    path('registration', views.RegistrationView.as_view(), name='registration'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('all-borrowed/', views.AllLoanedBooksListView.as_view(), name='all-borrowed'),
    path('bookinstance/create/', views.BookInstanceCreate.as_view(), name='bookinstance_create'),
    # path('bookinstance/<uuid:pk>/borrow/', views.BookInstanceBorrow.as_view(), name='bookinstance_borrow'),
    path('bookinstance/<uuid:pk>/borrow/', views.book_borrow, name='bookinstance_borrow'),
    path('bookinstance/<uuid:pk>/return/', views.BookInstanceReturn.as_view(), name='bookinstance_return'),
    path('bookinstance/<uuid:pk>/delete/', views.BookInstanceDelete.as_view(), name='bookinstance_delete'),
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('book/create/', views.BookCreate.as_view(), name='book_create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book_update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book_delete'),
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),
    path('account/profile/<username>', views.get_user_profile, name='profile'),
]
