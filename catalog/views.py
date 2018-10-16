from django.shortcuts import render, get_object_or_404, redirect
from catalog.models import Genre, Book, BookInstance, Author, Profile
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import datetime
import os
from catalog.forms import RenewBookForm, RenewBookModelForm, RegistrationForm, BorrowBookModelForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
from catalog.serializers import BookSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # counts for genres
    num_genres = Genre.objects.count()

    num_books_expanse = Book.objects.filter(title__icontains='expanse').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Get response from geolocation API
    ip = get_client_ip(request)
    response = requests.get('http://api.ipstack.com/' + ip + '?access_key=' + os.environ["ipAPIKey"])
    geodata = response.json()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_books_expanse': num_books_expanse,
        'num_genres': num_genres,
        'num_visits': num_visits,
        'ip': geodata['ip'],
        'country': geodata['country_name'],
        'city': geodata['city']
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'catalog/index.html', context=context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Replaced by book_list_view to add search functionality
# class BookListView(generic.ListView):
#     model = Book
#     template_name = 'catalog/book_list.html'  # Specify your own template name/location
#     paginate_by = 10
#
#     def get_queryset(self):
#         # return Book.objects.filter(title__icontains='expanse')[:5]
#         return Book.objects.filter()[:5]
#
#     # def get_context_data(self, **kwargs):
#     #     # Call the base implementation first to get the context
#     #     context = super(BookListView, self).get_context_data(**kwargs)
#     #     # Create any data and add it to the context
#     #     context['some_data'] = 'This is just some data'
#     #     return context


def book_list_view(request):
    """Book ListView with search functionality"""
    # find the latest five entries
    book_list = Book.objects.filter()[:5]
    # Search by input
    search_term = request.GET.get("search", None)
    if search_term is not None:
        book_list = Book.objects.filter(title__icontains=search_term)

    # Pagination
    page = request.GET.get('page', 1)

    paginator = Paginator(book_list, 10)
    try:
        book_list = paginator.page(page)
    except PageNotAnInteger:
        book_list = paginator.page(1)
    except EmptyPage:
        book_list = paginator.page(paginator.num_pages)

    context = {
        "book_list": book_list,
    }

    return render(request, 'catalog/book_list.html', context=context)


class BookListViewAPI(APIView):
    """Return API of Book model"""

    def get(self, request):
        book_list = Book.objects.all()
        serializer = BookSerializer(book_list, many=True)
        return Response(serializer.data)


class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, primary_key):
        book = get_object_or_404(Book, pk=primary_key)
        return render(request, 'catalog/book_detail.html', context={'book': book})


class AuthorListView(generic.ListView):
    model = Author
    template_name = 'catalog/author_list.html'
    paginate_by = 5

    def get_queryset(self):
        return Author.objects.all()


class AuthorDetailView(generic.DetailView):
    model = Author

    def author_detail_view(request, primary_key):
        author = get_object_or_404(Author, pk=primary_key)

        return render(request, 'catalog/author_detail.html', context={'author': author})


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user. """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = ['book', 'imprint', 'status']
    initial = {'status': 'a'}
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'


class BookInstanceReturn(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    fields = ['status', ]
    initial = {'status': 'a', 'due_back': '', }
    success_url = reverse_lazy('all-borrowed')
    permission_required = 'catalog.can_mark_returned'

# Replaced with function based view as practice
# class BookInstanceBorrow(PermissionRequiredMixin, UpdateView):
#     proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
#
#     model = BookInstance
#     fields = ['due_back', ]
#     initial = {'status': 'o', 'due_back': proposed_renewal_date, }
#     success_url = reverse_lazy('all-borrowed')
#     permission_required = 'catalog.can_mark_returned'
#     template_name = "catalog/book_borrow.html"


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        book_renewal_form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if book_renewal_form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = book_renewal_form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        book_renewal_form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': book_renewal_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


# This is a function based view for my practice
@permission_required('catalog.can_mark_returned')
def book_borrow(request, pk):
    """View function for changing status of a specific BookInstance by user."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        book_borrow_form = BorrowBookModelForm(request.POST)

        # Check if the form is valid:
        if book_borrow_form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = book_borrow_form.cleaned_data['due_back']
            book_instance.borrower = request.user
            book_instance.status = 'o'
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        book_borrow_form = BorrowBookModelForm(initial={'due_back': proposed_renewal_date,
                                                        })

    context = {
        'form': book_borrow_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_borrow.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'pic']
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/book_update.html'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'


class RegistrationView(generic.View):
    """View for creating user with portrait"""
    form_class = RegistrationForm
    template_name = 'registration/registration.html'

    # blank form
    def get(self, request):
        form = self.form_class(None)

        return render(request, self.template_name, {'form': form})

    # request.method == 'post'
    def post(self, request):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.portrait = form.cleaned_data.get('portrait')
            # get default group(Library Members) and add user to the group
            user.groups.add(Group.objects.get(name="Library Members"))
            user.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    messages.success(request, 'Your account has been created. Welcome!')
                    return self.dispatch(request)

        return render(request, self.template_name, {'form': form})

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            # messages.error(request, 'You need to logout first!')
            return redirect('/')

        return super().dispatch(request, *args, **kwargs)


# This has security breach - url.
@login_required()
def get_user_profile(request, username):
    """Return user's profile"""
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    context = {
        "user": user,
        'profile': profile,
    }

    return render(request, 'catalog/user_detail.html', context=context)

