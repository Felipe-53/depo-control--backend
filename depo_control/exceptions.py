"""
These custom exceptions should be raised when a message
needs to be fowarded to the client because of an error that
originated from him/her not using the application appropriatly.
For errors that were caused by the application itself, a Werkezeug
InternalServerError exception should be raise [werkezeug.exceptions].

All of this applies when an exception effectively NEEDS to be raised.
Code that may trow an exception shold not be wrapped by try...except
blocks because flask will automatically convert them in InternalServerErros.
(you can verify this by looking for `handle_exception` method in the app.py
flask file. Or do InternalServerError search in it.)
An error handler is registered for these and the client will get a simple
message with a 500 status code. For tracking these errors, Sentry got us
covered. From the flask documentation:

"...failures leading to an Internal Server Error are automatically
reported to Sentry (...)"

That's it.
"""


class Error(Exception):
    """ This is the base class for all custom Exceptions.
    It is istantiated with a 'message', a 'status_code' and optional
    'headers'. 'headers', when used, should be a dictionary.
    An error handler is registered at the application level to
    handle all exceptions of this class or those that inherit from
    it. Specifically, when this exception is raised, a JSON response
    is returned to the user with 'message' as its json body.
    The ideia is that all subclasses define specific 'status_code'
    and, optionally, 'headers' that will be incorporated with the
    response. Check 'error_handling.py' """

    # headers is either None (default or a dict)
    def __init__(self, message: str, status_code: int, headers=None):
        self.message = message
        self.status_code = status_code
        self.headers = headers


class AuthError(Error):
    """ To be raised when there are problems with Authentication """
    def __init__(self, message):

        headers = {'WWW-Authenticate': 'Bearer realm="Login Required"'}

        super().__init__(message, 401, headers=headers)


class PermissionError(Error):
    """To be raised when the user is Authenticated but has no
    permission to acess the resource. """
    def __init__(self, message):
        super().__init__(message, 403)


class DatabaseError(Error):
    """To be raised when a Database problem is found
    while handling a request. """
    def __init__(self, message):
        super().__init__(message, 500)


class BadRequestError(Error):
    """To be raised when the client data sent in the
    request is in inappropriate format. """
    def __init__(self, message):
        super().__init__(message, 400)


class SocketError(Error):
    """To be raised when the request was sucessful, but
    the server was unable to notify one or more of the
    clients in real time because of some kind of problem
    concerning messaging via Web Sockets.
    THE RESPONSE STATUS IS STILL 200 """
    def __init__(self, message):
        super().__init__(message, 200)


class LoginError(Error):
    """ Fired when login fails. Already comes
    with a message. """
    def __init__(self):
        message = "Login ou senha inválidos"
        super().__init__(message, 500)
