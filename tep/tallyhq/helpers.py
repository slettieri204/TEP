import os
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
import unicodecsv
from django.http import HttpResponse
import csv
from django.shortcuts import render
from .models import *
import datetime


#Jay im using python3.8 and unicode csv seems to not be supported.
#Im going to put these functions in a try except so that it doesnt fail for me when I use runserver

def ExportOrderSinceLast(request, csv_file_name,model_name,header_list):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+str(csv_file_name)+str(datetime.date.today())+'.csv'
        writer = csv.writer(response)
        header = header_list
        writer = unicodecsv.writer(response, encoding='utf-8')
        #writer.writerow(header)
        for obj in model_name.objects.filter(order__downloaded=False).order_by('-pk'):
            row = [getattr(obj, field)() if callable(getattr(obj, field)) else getattr(obj, field) for field in header]
            qty=Item.objects.filter(name=row[1]).first().qty_per_unit
            print(qty,row[2])
            row= [str(row[0]).split('_')[1].split(' ')[0],str(row[0]).split('_')[1].split(' ')[1], row[1],row[2],int(row[2])*int(qty)]
            writer.writerow(row)
        Order.objects.filter(downloaded=False).update(downloaded=True)
        return response
    except:
        return None

def ExportOrder(request, csv_file_name,model_name,header_list,startdate, enddate):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+str(csv_file_name)+str(startdate)+'-'+str(enddate)+'.csv'
        writer = csv.writer(response)
        header = header_list
        writer = unicodecsv.writer(response, encoding='utf-8')
        #writer.writerow(header)
        for obj in model_name.objects.filter(order__checkout_time__gte=startdate).filter(order__checkout_time__lte=enddate+datetime.timedelta(days=1)).order_by('-pk'):
            row = [getattr(obj, field)() if callable(getattr(obj, field)) else getattr(obj, field) for field in header]
            print(row[1])
            qty=Item.objects.filter(name=row[1]).first().qty_per_unit
            row= [str(row[0]).split('_')[1].split(' ')[0],str(row[0]).split('_')[1].split(' ')[1], row[1], row[2],int(row[2])*int(qty)]
            writer.writerow(row)
        return response
    except:
        return None