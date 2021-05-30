from django.http import HttpResponse
import json

from .utility.lexer import lexer
from .utility.parseTreeTraversal import traverse
from .utility.parser import parse
from .utility.repl import interpretCode
from .utility.repl import get_filters
from .utility.repl import delete_filter

from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from braces.views import CsrfExemptMixin


@csrf_exempt
def home(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['content']

    breakpoint()

    token_list = lexer(content)
    content = None
    parse_tree = parse(token_list)
    statements = traverse(parse_tree)

    print(statements)

    res = interpretCode(statements)

    breakpoint()

    return HttpResponse(json.dumps(res), content_type="application/json")


@csrf_exempt
def filters(request):
    if request.method == 'GET':
        filter_list = get_filters()
        return HttpResponse(json.dumps(filter_list), content_type="application/json")
    elif request.method == 'DELETE':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        filter_name = body['filterName']

        delete_filter(filter_name)

        res = ('succesfully deleted')

        return HttpResponse(json.dumps(res), content_type="application/json")


