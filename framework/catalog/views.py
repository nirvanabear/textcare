from django.shortcuts import render

from .models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_genres = Genre.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Books with 'the' in the title.
    num_books_with_the = Book.objects.filter(title__icontains='the').count()


    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_with_the': num_books_with_the,
    }

    ## TODO ##
    ## Creating a WebSocket in a separate process. 
    ## Needs imports: environ, websocket
    
    # def on_open(wsapp):
    #     wsapp.send("Hello")
    #     logger.debug("PID:")
    #     logger.debug(os.getpid())

    # def on_message(wsapp, message):
    #     logger.debug(message)

    # def on_ping(wsapp, message):
    #     logger.debug("Got a ping! A pong reply has already been automatically sent.")

    # def on_pong(wsapp, message):
    #     logger.debug("Got a pong! No need to respond")
    #     logger.debug("PID:")
    #     logger.debug(os.getpid())
    #     wsapp.ping_count += 1
    #     if wsapp.ping_count > 5:
    #         wsapp.close()
    #     logger.debug(f"Ping count: {wsapp.ping_count}")


    # websocket.enableTrace(True)
    # wsapp = websocket.WebSocketApp("wss://" + f"{env('EC2_DNS_NAME')}" + "/ws/chat/torture/", on_message=on_message, on_ping=on_ping, on_pong=on_pong)
    
    # logger.debug("wss://" + f"{env('EC2_DNS_NAME')}" + "/ws/chat/torture/")

    # wsapp.ping_count = 0

    # wsapp.run_forever(ping_interval=6, ping_timeout=5, ping_payload="This is an optional ping payload")  

    # wsapp.close()

    #######
    

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'home.html', context=context)



from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

    ## Option 1 (return top 5):
    # context_object_name = 'book_list'   # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    # template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location

    ## Option 2 (return top 5):
    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war

    ## Option 3 (create any data):
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context    


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author

    
    
