import requests
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .forms import BooksForm
from .models import Books
from .serializers import BooksSerializer
import django_filters
from django_filters import rest_framework as filters

"""Filter used in the listbook view - allows users to filter by Title, Authors or Year of publishing 
(equal and/or greater/lesser than the provided value)"""


class BookFilter(filters.FilterSet):
    acquired = django_filters.BooleanFilter(field_name='acquired_state')

    class Meta:
        model = Books
        fields = {
            "title": ["icontains"],
            "authors": ["icontains"],
            "publishedDate": ["iexact", "gte", "lte"],
        }


"""View responsible for viewing all books"""


class BookList(generics.ListAPIView):
    filter_backends = [filters.DjangoFilterBackend]
    serializer_class = BooksSerializer
    filterset_class = BookFilter
    queryset = Books.objects.all()

    def post(self, request):
        serializer = BooksSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""Single book view"""


class OneBookView(APIView):
    def get_object(self, pk):
        try:
            return Books.objects.get(pk=pk)
        except Books.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        book = self.get_object(pk)
        serializer = BooksSerializer(book, context={"request": request})
        return Response(serializer.data)

    def delete(self, request, pk):
        book = self.get_object(pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        book = self.get_object(pk)
        serializer = BooksSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Wrong parameters")


"""function to check if data in the fields is not empty"""


def is_valid_queryparam(param):
    return param != '' and param is not None


"""Main view - responsible for rendering all books in the DB, filtering it, 
as well as rendering the import and add buttons"""


def index(request):
    queryset = Books.objects.all()
    query = request.GET.get("title")
    querya = request.GET.get("author")
    queryl = request.GET.get("language")
    startyear = request.GET.get("startyear")
    endyear = request.GET.get("endyear")
    if is_valid_queryparam(query):
        queryset = Books.objects.filter(title__icontains=query)
    if is_valid_queryparam(querya):
        queryset = Books.objects.filter(authors__icontains=querya)
    if is_valid_queryparam(queryl):
        queryset = Books.objects.filter(language__icontains=queryl)
    if is_valid_queryparam(startyear):
        queryset = Books.objects.filter(publishedDate__gte=startyear)
    if is_valid_queryparam(endyear):
        queryset = Books.objects.filter(publishedDate__lte=endyear)
    context = {
        "object_list": queryset}
    return render(request, 'book/list.html', context)


"""Function that allows adding a book to the DB manually (by providing all details of a book manually"""


def add_book(request):
    if request.method == "POST":
        form=BooksForm(request.POST)
        if form.is_valid():
            book_item=form.save(commit=False)
            book_item.save()
            return HttpResponseRedirect('/')
    else:
        form=BooksForm()
    return render(request, 'book/book_form.html', {'form': form})


"""View that is responsible for the lookup of the books in Google Books API and saving selected ones to DB"""


def google_import(request):
    list = []
    counter = 0
    query = request.GET.get("title")
    if is_valid_queryparam(query):
        url = 'https://www.googleapis.com/books/v1/volumes?q={}&printType=books'
        url = url.format(query)
        r = requests.get(url)
        results = r.json()['items']
        for result in results:
            try:
                book = {
                        'title': result['volumeInfo']['title'],
                        'authors': result['volumeInfo']['authors'],
                        'publishedDate': result['volumeInfo']['publishedDate'],
                        'industryIdentifiers': result['volumeInfo']['industryIdentifiers'],
                        'pageCount': result['volumeInfo']['pageCount'],
                        'imageLinks': result['volumeInfo']['imageLinks'],
                        'language': result['volumeInfo']['language'],
                        }
                list.append(book)
                counter += 1
            except KeyError:
                pass
    if request.method == "POST":
        number = request.POST.get("number")
        try:
            form = BooksForm(list[int(number)-1])
            if form.is_valid():
                book_item = form.save(commit=False)
                book_item.save()
                counter = "imported book nr:"+number
        except IndexError:
            counter = "wrong index number"
    return render(request, 'book/book_import.html', {'r': list, 'counter': counter})
