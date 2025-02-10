import logging

class ExceptionLoggingMiddleware:

    # def process_exception(self, request, exception):
    #     logging.exception('Exception handling request for ' + request.path)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            logging.exception(str(e))
        return response