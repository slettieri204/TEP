from django.shortcuts import render
from .models import *
from .forms import *
from django.views.generic import FormView,TemplateView,CreateView,ListView,UpdateView,DetailView
from datatableview.views import XEditableDatatableView, DatatableView
from datatableview import helpers, Datatable, columns
import csv
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import CreateView, DeleteView, UpdateView,View
from django import template
from django.contrib.auth.mixins import LoginRequiredMixin
from .helpers import *
from django.http import HttpResponseRedirect
from django.core import serializers
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, timedelta, timezone

class TreeView(TemplateView):
    template_name = 'tallyhq/tree.html'


class AjaxableResponseMixin:
    """
    Mixin to add AJAX support to a form.   Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            print("FORM ERRORS ARE:",str(form.errors))
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        if self.request.is_ajax():
            print("AjaxableResponseMixin REQUEST WAS AJAX**")
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response

#Any TEP Staff protected views will inherit this class
#TEP Staff need to be logged in with a django admin account
class TEPStaffRequired(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser: #TEPStaff must ne logged in as superuser
            print("IM HERE")
            return render(request, template_name="tallyhq/permission_denied.html")
        return super().dispatch(request, *args, **kwargs)

class TeacherLogin(FormView):
    template_name = 'tallyhq/teacherLogin.html'
    #template_name = 'tallyhq/generic_form.html'
    model = Teacher
    form_class = TeacherLoginForm
    exclude = ['phone','address']
    #success_url = '/tallyhq/teacherwaiver/?teacher'

    def post(self,request,*args,**kwargs):
        print ("in post")
        print (request.POST)
        form = self.get_form()
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email').strip()
        school = request.POST.get('school')
        print (first_name,last_name,email,school)

        if school=='':
            print("no school selected")
            return self.form_invalid(form)
        
        school_obj=School.objects.get(pk=int(school))
        school_active=school_obj.active
        print('school_obj',school_obj,school_active)
        if school_active==False:
            print("Inactive school!")
            return self.form_invalid(form) 

        num_records = Teacher.objects.filter(first_name__iexact=first_name,last_name__iexact=last_name,email__iexact=email,school=school).count()
        if num_records != 1 :
            print("NO SUCH RECORD EXISTS")
            return self.form_invalid(form) 

        else:
            print("I HAVE FOUND YOUR RECORD")
            teacher = list(Teacher.objects.filter(first_name__iexact=first_name,last_name__iexact=last_name,email__iexact=email,school=school).values_list('pk', flat=True))[0]
            request.teacher_pk = teacher
            return super().form_valid(form)


    def get_success_url(self):
        a = self.request.teacher_pk
        url = '/tallyhq/teacherwaiver/'+str(a)
        return url

class TeacherWaiver(TemplateView):
    template_name = 'tallyhq/teacherSignPDF.html'
    def get_context_data(self, **kwargs):
        #Get the last object uploaded to the waiver model
        context = super(TeacherWaiver, self).get_context_data(**kwargs)
        try:
            last_waiver = Waiver.objects.latest('id')
            last_waiver_url = last_waiver.file.url
            print("last_waiver_url",last_waiver_url)
            context['last_waiver_url']=last_waiver_url
        except:
            print("Failed to get the last waiver object, does it exist?")
            pass
        return context

class TeacherShoppingReminders(TemplateView):
    template_name = 'tallyhq/teacherShoppingReminders.html'

class TeacherCheckout(CreateView):
    template_name = 'tallyhq/teacherCheckout.html'
    model = OrderItem
    form_class = OrderItemForm

    def get_context_data(self, **kwargs):
        data=super(TeacherCheckout,self).get_context_data(**kwargs)
        if self.request.POST:
            data['titles'] = formset(self.request.POST)
        else:
            data['titles'] = formset()
            data['stuff'] = Item.objects.all().filter(active=True).order_by('rank')
            data['password'] = ValidationPassword.objects.all().values_list('digest',flat=True).filter().first()
        return data

    def post(self, request, teacher_id, *args, **kwargs):
        t = Teacher.objects.all().filter(pk=teacher_id).first()
        o = Order(teacher=t)
        o.save()
        print(request.POST)
        for item in request.POST:
            if 'password' not in item:
                if 'csrfmiddlewaretoken' not in item:
                    i = Item.objects.all().filter(active=True, name=item).first()
                    units_taken = request.POST.get(item)
                    print("units_taken",units_taken)
                    if units_taken!='' and str(units_taken)!='0':
                        oi = OrderItem(order=o,units_taken=units_taken,item=i)
                        oi.save()
        return redirect('/tallyhq/teacherordersuccess/')

class TeacherOrderSuccess(TemplateView):
    template_name = 'tallyhq/teacherOrderSuccess.html'


class ManageOrders(TEPStaffRequired,DatatableView):
    model=Order
    template_name = 'tallyhq/manageorders.html'
    class datatable_class(Datatable):
        action = columns.TextColumn("Details",sources=None,processor='make_action_column')
        formatted_datetime = columns.TextColumn("Checkout Date",sources='checkout_time',processor='format_datetime')
        def format_datetime(self,instance,**kwargs):
            loc = instance.checkout_time - timedelta(hours=5, minutes=0) #format & localize the time manually
            return loc.strftime("%b %d %Y, %I:%M %p")

        def make_action_column(self,instance,**kwargs):
            the_pk = instance.pk
            my_list = """<a onclick="inject_url_in_detailmodal('/tallyhq/orderdetailview/%d')"><button class="ui button"><i class="green list ol icon"></i></button></a>""" % (the_pk)
            return my_list
        class Meta:
            structure_template = 'tallyhq/bootstrap_structure.html'
            footer=False
            columns=['id','formatted_datetime','teacher','downloaded']
            exclude=['password_hash','checkout_time']
            ordering=['-pk']
    def get_datatable_kwargs(self):
        kwargs = super(ManageOrders, self).get_datatable_kwargs()
        kwargs['url'] = '/tallyhq/manageorders/'
        return kwargs


class Dashboard(TEPStaffRequired,UpdateView):
    template_name = 'tallyhq/dashboard.html'
    model = ValidationPassword
    form_class = ValidationPasswordForm
    success_url = '/tallyhq/dashboard/'

    def get_object(self):
        return ValidationPassword.objects.get(pk=1)

    def get_context_data(self, **kwargs):
        context = super(Dashboard,self).get_context_data(**kwargs)
        try:
            last_waiver = Waiver.objects.latest('id')
            last_waiver_url = last_waiver.file.url
        except:
            last_waiver = None
            last_waiver_url = None 
        recent_orders = Order.objects.order_by('-pk')
        context['waiver_info'] = last_waiver
        context['last_waiver_url'] = last_waiver_url
        context['datatable'] = ManageOrders().get_datatable()  #Get the datatable from ManageOrders. Embed it in the dashboard.html
        time_diff_hours = ((datetime.now(timezone.utc)-self.get_object().uploaded_date).total_seconds())/3600.
        if time_diff_hours < 1:
            context['time_diff']='< 1 hour'
        else:
            context['time_diff']=str(int(time_diff_hours))+ ' hours'
        print (context)
        return context

    def form_valid(self, form):
        post = super().form_valid(form)
        record = ValidationPassword.objects.get(pk=1)
        record.uploaded_date = datetime.now()
        record.save()
        print(record)
        return (post)

class OrderView(TEPStaffRequired,TemplateView):
    template_name = 'tallyhq/orderview.html'



class ExportData(TEPStaffRequired,TemplateView):
    template_name = 'tallyhq/exportdata.html'
    def post(self,request,*args,**kwargs):

        if 'exportsincelast' in request.POST:
            return ExportOrderSinceLast(request, 'Orders_since_last_export',OrderItem,['order','item','units_taken'])
        if 'customexport' in request.POST:
   
            try:

                startdate =  datetime.strptime(request.POST.get('startdate'), '%m/%d/%Y').date()
                enddate =  datetime.strptime(request.POST.get('enddate'), '%m/%d/%Y').date()
            except Exception as e:
                startdate =  datetime.strptime(request.POST.get('startdate'), '%Y-%m-%d').date()
                enddate =  datetime.strptime(request.POST.get('enddate'), '%Y-%m-%d').date()
                print(str(e))
            return ExportOrder(request, 'Orders_between',OrderItem,['order','item','units_taken'],startdate,enddate)

class ImportData(TEPStaffRequired,TemplateView):
    template_name = 'tallyhq/importdata.html'

class DeleteData(TEPStaffRequired,TemplateView):
    template_name = 'tallyhq/deletedata.html'


class ManageTeachers(TEPStaffRequired,DatatableView):
    model = Teacher
    template_name = 'tallyhq/manageteachers.html'

    def post(self,request,*args,**kwargs):
        print("im posting")
        context={}
        context['datatable']=self.get_datatable()
        context['error'] =''
        the_file = self.request.FILES['file']
        print("fn",str(the_file))
        if str(the_file)!="Teacher Upload.csv":
            context['error']="The file name must be called Teacher Upload.csv!   You gave me " + str(the_file)            
        else:
            data_list = the_file.read().decode('utf-8').splitlines()
            for elem in data_list:
                r = elem.split(',')
                first,last,email,school = r[0].strip(),r[1].strip(),r[2].strip(),r[-1].strip()
                #lookup the school pk in the school model
                try:
                    the_school = School.objects.get(name=school)
                except Exception as e:
                    context['error'] +='<br>'+ "The record: <b>" + elem+ "</b> contains a school that does not exist in TallyHQ, please add the school " + str(school)  + " and then try again."
                    
                new_row = Teacher(first_name=first,last_name=last,email=email,school=the_school)
                try:
                    new_row.save()
                except Exception as e:
                    context['error']+='<br>'+str(e)
                
        print(context)
        return render(self.request,template_name = self.template_name,context=context)

    class datatable_class(Datatable):
        school = columns.TextColumn("School",sources="school__name")  #since school is foreign key in the teacher model, make it searchable by using source = school__name
        action = columns.TextColumn("Actions",sources=None,processor='make_action_column')
        def make_action_column(self,instance,**kwargs):
            the_pk = instance.pk
            my_trashcan = """<a onclick="inject_url_in_modal('/tallyhq/teacher/delete/%d')"><button class="ui button"><i class="large red trash icon"></i></button></a>""" % (the_pk)
            my_pencil = """<a onclick="inject_url_in_modal('/tallyhq/teacher/edit/%d')"><button class="ui button"><i class="large blue pencil icon"></i></button></a>""" % (the_pk)
            button_pair = """<div class="ui medium buttons">   %s   <div class="or" style="z-index:0"></div>     %s     </div>""" % (my_pencil,my_trashcan)
            return button_pair
        class Meta:
            structure_template = 'tallyhq/bootstrap_structure.html'
            footer=False
            columns= [
            'first_name',
            'last_name',
            'email',
            'school'
            ]


class ManageSchools(TEPStaffRequired,DatatableView):
    model = School
    template_name = 'tallyhq/manageschools.html'

    def post(self,request,*args,**kwargs):
        print("im posting")
        context={}
        context['datatable']=self.get_datatable()
        context['error']=''
        the_file = self.request.FILES['file']
        print("fn",str(the_file))
        if str(the_file)!="schools.csv":
            context['error']="The file name must be called schools.csv!   You gave me " + str(the_file)            
        else:
            data_list = the_file.read().decode('utf-8').splitlines()
            for elem in data_list:
                new_row = School(name= elem.strip(),active=True)
                try:
                    new_row.save()
                except Exception as e:
                    context['error']+='<br>'+str(e)
                    pass 
        print(context)
        return render(self.request,template_name = self.template_name,context=context)

    class datatable_class(Datatable):
        action = columns.TextColumn("Actions",sources=None,processor='make_action_column')
        def make_action_column(self,instance,**kwargs):
            the_pk = instance.pk
            my_trashcan = """<a onclick="inject_url_in_modal('/tallyhq/school/delete/%d')"><button class="ui button"><i class="large red trash icon"></i></button></a>""" % (the_pk)
            my_pencil = """<a onclick="inject_url_in_modal('/tallyhq/school/edit/%d')"><button class="ui button"><i class="large blue pencil icon"></i></button></a>""" % (the_pk)
            button_pair = """<div class="ui medium buttons">   %s   <div class="or" style="z-index:0"></div>     %s     </div>""" % (my_pencil,my_trashcan)
            return button_pair
        class Meta:
            structure_template = 'tallyhq/bootstrap_structure.html'
            footer=False
            labels={
            'name':'School'
            }
            columns= [
            'name',
            'active',
            'action'
            ]


class ManageItems(TEPStaffRequired,DatatableView):
    model=Item
    template_name = 'tallyhq/manageitems.html'
    class datatable_class(Datatable):
        action = columns.TextColumn("Actions",sources=None,processor='make_action_column')
        def make_action_column(self,instance,**kwargs):
            the_pk = instance.pk
            my_trashcan = """<a onclick="inject_url_in_modal('/tallyhq/item/delete/%d')"><button class="ui button"><i class="large red trash icon"></i></button></a>""" % (the_pk)
            my_pencil = """<a onclick="inject_url_in_modal('/tallyhq/item/edit/%d')"><button class="ui button"><i class="large blue pencil icon"></i></button></a>""" % (the_pk)
            button_pair = """<div class="ui medium buttons">   %s   <div class="or" style="z-index:0"></div>     %s     </div>""" % (my_pencil,my_trashcan)
            return button_pair
        class Meta:
            structure_template = 'tallyhq/bootstrap_structure.html'
            footer=False
            ordering=['rank']
            exclude=['id']


class TestView(TEPStaffRequired,DatatableView):
    model = Teacher
    template_name = 'tallyhq/datatable_example_1.html'

    class datatable_class(Datatable):
        class Meta:
            structure_template = 'tallyhq/bootstrap_structure.html'
            footer=True

class TestView2(TEPStaffRequired,XEditableDatatableView):
    model = Teacher
    template_name = 'tallyhq/datatable_example_2.html'

    class datatable_class(Datatable):
        class Meta:
            structure_template = 'tallyhq/bootstrap_structure.html'
            footer=True
            columns= [
            'id',
            'first_name',
            'last_name',
            ]
            processors={
            'first_name':helpers.make_xeditable,
            'last_name':helpers.make_xeditable,

            }

#Any common logic in the basic CRUD views should go here in CommonView
#This helper class allows me to customize the crud views a little bit by creating a form_header attribute & point them all to the same template   
#All my basic CRUD views will use this generic_form.html template  or a generic_form_for_modal.html template  
class CommonView(View):
    template_name = "tallyhq/generic_form_for_modal_ajax.html" #Use this one when you want all modal forms
    #template_name = "tallyhq/generic_form.html"  #Use this one when you want all normal (non-modal) forms
    def get_context_data(self,*args,**kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self,'form_header'):
            context['form_header'] = self.form_header
        else:
            context['form_header'] = "Please fill out the form below" #default value if the user doesnt specify a form_header
        return context

##########################################
############ BASIC CRUD VIEWS ############
##########################################

class TeacherCreate(AjaxableResponseMixin,TEPStaffRequired,CommonView,CreateView):
    model = Teacher
    success_url = "/tallyhq/manageteachers/"
    fields = ['first_name','last_name','email','school']
    form_header = "Create a new teacher by filling out the form below"

class SchoolCreate(AjaxableResponseMixin,TEPStaffRequired,CommonView,CreateView):
    model = School
    success_url = "/tallyhq/manageschools/"
    fields = ['name','active']
    form_header = "Create a new school by filling out the form below"


class ItemCreate(AjaxableResponseMixin,TEPStaffRequired,CommonView,CreateView):
    model = Item
    success_url = "/tallyhq/manageitems/"
    fields = ['name','unit_label_name','max_units','qty_per_unit','rank','active']
    form_header = "Create a new item by filling out the form below"

class TeacherUpdate(AjaxableResponseMixin,TEPStaffRequired,CommonView,UpdateView):
    model = Teacher
    success_url = "/tallyhq/manageteachers/"
    fields = ['first_name','last_name','email','school']
    form_header = "Update the teacher information in the form below"

class SchoolUpdate(AjaxableResponseMixin,TEPStaffRequired,CommonView,UpdateView):
    model = School
    success_url = "/tallyhq/manageschools/"
    fields = ['name','active']
    form_header = "Update the school information in the form below"

class ItemUpdate(AjaxableResponseMixin,TEPStaffRequired,CommonView,UpdateView):
    model = Item
    success_url = "/tallyhq/manageitems/"
    fields = ['name','unit_label_name','max_units','qty_per_unit','rank','active']
    form_header = "Update the item information in the form below"

class TeacherDelete(AjaxableResponseMixin,TEPStaffRequired,CommonView,DeleteView):
    model = Teacher
    success_url = "/tallyhq/manageteachers/"
    form_header = "Are you sure you want to delete this teacher?"

class SchoolDelete(AjaxableResponseMixin,TEPStaffRequired,CommonView,DeleteView):
    model = School
    success_url = "/tallyhq/manageschools/"
    form_header = "Are you sure you want to delete this school?"

class ItemDelete(AjaxableResponseMixin,TEPStaffRequired,CommonView,DeleteView):
    model = Item
    success_url = "/tallyhq/manageitems/"
    form_header = "Are you sure you want to delete this item?"

class TeacherPurge(AjaxableResponseMixin, TEPStaffRequired,CommonView,DeleteView):
    model = Teacher
    success_url = "/tallyhq/manageteachers/"
    form_header = "Are you sure you want to delete all the teachers?"

    def get_object(self, queryset=None):
        obj=Teacher.objects.all()
        return obj

class SchoolPurge(AjaxableResponseMixin, TEPStaffRequired,CommonView,DeleteView):
    model = School
    success_url = "/tallyhq/manageschools/"
    form_header = "Are you sure you want to delete all the schools?"

    def get_object(self, queryset=None):
        obj=School.objects.all()
        return obj

class ItemPurge(AjaxableResponseMixin,TEPStaffRequired,CommonView,DeleteView):
    model = Item
    success_url = "/tallyhq/manageitems/"
    form_header = "Are you sure you want to delete all the items?"

    def get_object(self, queryset=None):
        obj=Item.objects.all()
        return obj

def OrderDetailView(request, pk):
    print(pk)
    obj = OrderItem.objects.filter(order__pk=pk).values('units_taken', 'item__name','order__pk','item__rank')
    lst = list(obj)
    sorted_list = sorted(lst, key = lambda i: i['item__rank'])
    data=json.dumps(sorted_list, cls=DjangoJSONEncoder)
    print("data",data)
    return HttpResponse(data, content_type='applicaiton/json')

class WaiverUpload(TEPStaffRequired,CommonView,CreateView):
    success_url = "/tallyhq/dashboard/"
    model = Waiver
    fields = ['file']

 
def custom_404_handler(request, exception=None):
    return render(request,template_name='tallyhq/404.html', status=404)



class stevecheckout(CreateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = "tallyhq/generic_form_many.html"

    def get_context_data(self, **kwargs):
        context = super(stevecheckout, self).get_context_data(**kwargs)
        all_items = Item.objects.all()
        cnt = all_items.count()
        some_order = Order.objects.first()
        #LETS SET SOME INITIAL DATA FOR EACH FORM, ITS A LIST OF DICTS
        my_init =[ {'units_taken': '23','item':elem,'order':some_order} for elem in all_items ]
        print("my_init",my_init)
        OrderItemFormFactory = modelformset_factory(OrderItem, fields=("order", "item","units_taken"),extra=cnt)
        context['formset'] = OrderItemFormFactory(queryset=OrderItem.objects.none(),initial=my_init) 
        return context

    def post(self, request, *args, **kwargs):
        print("here a")
        all_items = Item.objects.all()
        cnt = all_items.count()
        OrderItemFormFactory = modelformset_factory(OrderItem, fields=("order", "item","units_taken"),extra=cnt)
        formset = OrderItemFormFactory(request.POST)
        if formset.is_valid():
            print("here b")
            return self.form_valid(formset)

    def form_valid(self, formset):
        for form in formset:
            print("form",form)
            #form.save()
        #formset.save()
        return HttpResponseRedirect('/tallyhq/manageteachers')

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))

class Timeline(TemplateView):
    template_name="tallyhq/timeline.html"
    def get_context_data(self, **kwargs):
        context = super(Timeline, self).get_context_data(**kwargs)
        context['me'] = str(Teacher.objects.first())
        context['me2'] = 's'
        context['me3'] = model_to_dict(Teacher.objects.last())
        context['me4'] =get_current_user()
        return context


class Timeline2(TemplateView):
    template_name="tallyhq/timeline2.html"

class Timeline3(TemplateView):
    template_name="tallyhq/timeline3.html"

#path('wq/<str:filter>', WorkQueue.as_view(),name="wq"),
class WorkQueue(DatatableView):
    model = Teacher
    template_name = 'tallyhq/workqueue.html'

    #Filter the model based on the tab url parameter
    def get_queryset(self,*args,**kwargs):
        filter_value=self.kwargs['filter']
        return Teacher.objects.filter(first_name__icontains=filter_value)

    def get_context_data(self, **kwargs):
        context = super(WorkQueue, self).get_context_data(**kwargs)
        filter_value=self.kwargs['filter']
        context['active_tab'] = str(filter_value) #send back the active tab to the template (no js solution)
        #Pass the tab information here, the template is abstract to handle arbitrary number of tabs
        tab_list= [

        {'filter_value':'x','tab_name':"Pending"},
        {'filter_value':'y','tab_name':"Approved"},
        {'filter_value':'z','tab_name':"Rejected"},

        ]
        context['tab_list']  = tab_list
        return context

    class datatable_class(Datatable):
        school = columns.TextColumn("School",sources="school__name")  #since school is foreign key in the teacher model, make it searchable by using source = school__name
        class Meta:
            structure_template = 'tallyhq/bootstrap_structure.html'
            footer=False
            columns= ['first_name', 'last_name', 'email', 'school' ]
