from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import *


# @login_required(login_url='/identity/login')
def index_view(request):
    my_list = Transaction.objects.all().order_by('-creation_date')[:7]
    context = {
        'my_list': my_list,
        'user': request.user,       
    }
    return render(request, 'index.html', context)
