from .models import *
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.forms.models import modelformset_factory, inlineformset_factory, formset_factory
from django.db.models import Count
from django.forms import modelform_factory

class TeacherLoginForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude = ('active','phone','address')

    def clean(self):
        cleaned_data = super(TeacherLoginForm,self).clean()
        try:
            email = cleaned_data['email'].strip()
            first_name = cleaned_data['first_name'].strip()
            last_name = cleaned_data['last_name'].strip()
            school = cleaned_data['school']
        except:
            message = format_html('<div class="header">Please select and fill all fields.  Make sure a valid email address & school is given.</div>')
            raise ValidationError(message)         
        num_records = Teacher.objects.filter(first_name__iexact=first_name,last_name__iexact=last_name,email__iexact=email,school=school).count()
        if num_records == 0:
            message = format_html('<div class="header">You are not a registered user</div><p>The first name, last name, email and school combination does not match a registered user.<br>'
                                  'Please see TEP staff to assist you with teacher registration.</p></div>')
            raise ValidationError(message)
        print('form school',school)
        school_obj=School.objects.filter(name=school).first()
        school_active=school_obj.active
        print('school_obj',school_obj,school_active)
        if school_active==False:
            message = format_html('<div class="header">This school appears to be inactive</div><br>'
                                  'Please see TEP staff to assist you with teacher registration.</div>')
            raise ValidationError(message)
        return cleaned_data

class ValidationPasswordForm(forms.ModelForm):
    class Meta:
        model = ValidationPassword
        exclude = []

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        exclude = []

# Extra will be the count of active items
#https://stackoverflow.com/questions/29726538/modelformset-in-django-generic-createview-and-updateview
count = Item.objects.all().filter(active=True).values_list('name', flat=True).distinct()
formset = inlineformset_factory(Order,OrderItem, form=OrderItemForm, extra=len(count),max_num=1)
