import time


from django.http import HttpRequest, HttpResponse


def set_useragent_on_request_middleware(get_response):
    print("initial call")

    def middleware(request: HttpRequest):
        print("before get response")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        print("after get response")
        return response

    return middleware


class CountRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_count = 0
        self.response_count = 0
        self.exception_count = 0
        self.user_call = {}

    def __call__(self, request: HttpRequest):
        self.request_count += 1
        print("request count", self.request_count)
        ip = request.META["REMOTE_ADDR"]
        """добавление нового ip пользователя со временем последнего ответа и количеством запросов"""
        if ip not in self.user_call:
            response = self.get_response(request)
            self.response_count += 1
            print("response count", self.response_count)
            self.user_call[ip] = [time.time()] + [0]
            return response
        """ Обнуление количества запросов пользователя """
        if self.user_call[ip][0] < time.time() - 2:
            self.user_call[ip][1] = 0
        """ Ограничение по количеству запросов"""
        if self.user_call[ip][1] <= 3:
            response = self.get_response(request)
            self.response_count += 1
            print("response count", self.response_count)
            self.user_call[ip][0] = time.time()
            self.user_call[ip][1] += 1
            return response
        else:
            self.exception_count += 1
            return HttpResponse("Too many requests, hold on for a while", status=429)

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exception_count += 1
        print("got", self.exception_count, "exceptions")

