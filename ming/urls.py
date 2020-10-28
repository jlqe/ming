"""ming URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.views import *
from web.views import *

from rest_framework.schemas import get_schema_view

from django.views.generic import TemplateView

from django.conf.urls import (
	handler400, handler403, handler404, handler500
)

handler404 = 'web.views.handler404'
handler500 = 'web.views.handler500'

urlpatterns = [
	#path('admin/', admin.site.urls),
	path('json-rpc/', jsonrpc.JsonRpc),
	path('blocks/', block.BlockList.as_view()),
	path('blocks/<int:pk>/', block.BlockDetail.as_view()),
	path('blocksigner/<int:pk>/', block.BlockSignerDetail.as_view()),
    path('openapi', get_schema_view(
        title="Ming",
        description="API for everything Tao",
        version="1.0.0"
    ), name='openapi-schema'),
    path('', TemplateView.as_view(
        template_name='redoc.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='redoc'),

]

urlpatterns = format_suffix_patterns(urlpatterns)