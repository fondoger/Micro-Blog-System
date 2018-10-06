from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('post/<int:id>', views.post_view, name='post_view'),
    path('post/edit', views.post_edit, name='post_edit'),
    path('post/edit/<int:id>', views.post_edit, name='post_edit'),
    path('post/delete/<int:id>', views.post_delete, name='post_delete')
]
