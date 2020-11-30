from flask import make_response
from werkzeug.exceptions import InternalServerError
from werkzeug.exceptions import HTTPException
from depo_control.exceptions import Error
import sentry_sdk


def register_error_handlers(app):

    @app.errorhandler(HTTPException)
    def handle_HTTPException(e):
        """ Werkzeug implements a bunch of HTTPExceptions that
        flask uses to respond to clients. Since this is an
        API and my clients don't consume it directly, I'm sending
        a short error message to them and at the same time reporting
        it to sentry to be checked later. """

        # sentry doesn't catch these automatically
        sentry_sdk.capture_exception(e)

        return {
            'message': 'Houve um problema com a sua requisição'
        }, 500

    """ Flask Docs: 'After installation, failures leading to an
    Internal Server Error are automatically reported to Sentry
    and from there you can receive error notifications."""
    @app.errorhandler(InternalServerError)
    def handle_InternalServerError(e):
        """ All unhandled exceptions that happens processing
        a request will end up here. The intention of this
        handler is to convert the response to json. In debug
        mode, the original exception will still be shown by
        the debugger. """

        response = make_response(
            {'message': 'Um erro inesperado aconteceu no servidor'},
            500
        )

        return response

    @app.errorhandler(Error)
    def handle_Error(e):
        response = make_response({'message': e.message}, e.status_code)

        sentry_sdk.capture_exception(e)

        if e.headers:
            for header_name in e.headers:
                response.headers[header_name] = e.headers[header_name]

        return response
