from django.urls import path
from . import views

app_name = 'nlp'

urlpatterns=[
    path("",views.IndexView.as_view(), name="index"),
    
    path("",views.index, name="home"),
    path("",views.tf_idf, name="tf_idf")
    
    
]


