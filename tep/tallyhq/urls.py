from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from .views import *

urlpatterns = [
    path('test/', TestView.as_view()),
    path('test2/', TestView2.as_view()),
    path('teacherlogin/', TeacherLogin.as_view()),
    path('teacherwaiver/<int:teacher_id>', TeacherWaiver.as_view()),
    path('teachershoppingreminders/<int:teacher_id>', TeacherShoppingReminders.as_view()),
    path('teachercheckout/<int:teacher_id>', TeacherCheckout.as_view()),
    path('teacherordersuccess/', TeacherOrderSuccess.as_view()),
    path('dashboard/', Dashboard.as_view()),
    path('waiverupload/', WaiverUpload.as_view()),
    path('orderview/', OrderView.as_view()),
    path('orderdetailview/<int:pk>', OrderDetailView),
    path('exportdata/', ExportData.as_view()),
    path('importdata/', ImportData.as_view()),
    path('deletedata/', DeleteData.as_view()),



    #####The following views replicate the full functionality of the django /admin panel
    #####They all use the same gerneric_form.html

    #View & Manage list of model entries views
    path('manageteachers/', ManageTeachers.as_view()),
    path('manageschools/', ManageSchools.as_view()),
    path('manageitems/', ManageItems.as_view()),
    path('manageorders/', ManageOrders.as_view()),

    #Add new model entries views
    path('teacher/add/', TeacherCreate.as_view(), name='teacher-add'),
    path('school/add/', SchoolCreate.as_view(), name='school-add'),
    path('item/add/', ItemCreate.as_view(), name='item-add'),

    #Edit model entries views
    path('school/edit/<int:pk>', SchoolUpdate.as_view(), name='school-edit'),
    path('teacher/edit/<int:pk>', TeacherUpdate.as_view(), name='teacher-edit'),
    path('item/edit/<int:pk>', ItemUpdate.as_view(), name='item-edit'),

    #delete model entries views
    path('teacher/delete/<int:pk>', TeacherDelete.as_view(), name='teacher-delete'),
    path('school/delete/<int:pk>', SchoolDelete.as_view(), name='school-delete'),
    path('item/delete/<int:pk>', ItemDelete.as_view(), name='item-delete'),

    #perge data
    path('teacher/purge/', TeacherPurge.as_view(), name='teacher-purge'),
    path('school/purge/', SchoolPurge.as_view(), name='school-purge'),
    path('item/purge/', ItemPurge.as_view(), name='item-purge'),

    path('orderitem/addmany/', stevecheckout.as_view(), name='orderitem-add'),

     path('tree/', TreeView.as_view()),
      path('timeline/', Timeline.as_view()),
  path('timeline2/', Timeline2.as_view()),
    path('timeline3/', Timeline3.as_view()),
      path('wq/<str:filter>', WorkQueue.as_view(),name="wq"),

]

