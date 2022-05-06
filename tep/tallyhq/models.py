from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime

from django.db.models.fields.related import ManyToManyField
from django.forms.models import model_to_dict
from tep.middleware import get_current_user
from django.contrib.auth.models import User
from django.forms.models import model_to_dict




def dict_diff(curr_dict,new_dict): 
    return {k: curr_dict[k] for k in curr_dict if k in new_dict and new_dict[k] != curr_dict[k] and k!='last_changed_by' and k!='last_changed_time'}

class ModelChangeLogger(models.Model):
    last_changed_by = models.ForeignKey(User,on_delete=models.CASCADE)
    last_changed_time = models.DateTimeField(default=datetime.now)
    def save(self, *args, **kwargs):
        model_name = self._meta.model_name
        model_pk = self.pk
        curr_user = get_current_user()
        curr_time = datetime.now()
        self.last_changed_by = curr_user
        self.last_changed_time = curr_time
        dict_before_change = model_to_dict(self._meta.model.objects.get(pk=self.pk)) if self.pk is not None else {}
        
        #Save the model normally
        super(ModelChangeLogger, self).save(*args, **kwargs)

        curr_dict = model_to_dict(self)

        model_delta_as_dict = dict_diff(dict_before_change,curr_dict) 
        print("OLD VALUES THAT CHANGED",model_delta_as_dict  )
        print("curr_user",curr_user  )
        print("curr_time",curr_time  )
        print("model_name",model_name  )
        print("model_pk",model_pk  )

        #######  Save to audit log ######
        #audit =  AuditLog(model=model_name,model_pk=model_name,who=curr_user,when=curr_time,changes=model_delta_as_dict)
        #audit.save()

    class Meta:
        abstract = True


class Item(models.Model):
    # title of item (e.g. 'pencils')
    name = models.CharField(max_length=30)

    # display label for unites (e.g. 'packs')
    unit_label_name = models.CharField(max_length=15)

    # maximum number of units that can be taken for this item
    max_units = models.IntegerField(validators=[MinValueValidator(1)])

    # number of the item per unit (e.g. 8 (pencils per pack))
    qty_per_unit = models.IntegerField(validators=[MinValueValidator(1)])

    # also has attribute: 'orders' as defined by ManyToMany in Order

    # whether or not the item is active.
    active = models.BooleanField(default=True)

    # order of item in the orderItem list
    rank = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)


class School(ModelChangeLogger,models.Model):
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('name', )

# class ModelChangeLogger:
#     def save(self, *args, **kwargs):
#         print("IM SAVING!!!")
#         print("THE MODEL NAME IM SAVING IS:",self._meta.model_name)
#         print("THE FIRST MODEL OBJECT IS:",self._meta.model.objects.first())
#         print("...AS A DICT:",model_to_dict(self._meta.model.objects.first()))
#         print("THE INSTANCE OF THE MODEL IM SAVING IS",self)
#         print("current_user",get_current_user())
#         super(ModelChangeLogger, self).save(*args, **kwargs)


class Teacher(ModelChangeLogger,models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=30)
    # TODO: this is overridden in the serializer, so it should be validated in the view
    email = models.EmailField(null=False)
    phone = models.CharField(max_length=20, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False)
    active = models.BooleanField(default=True)
    address = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.first_name) + ' ' + str(self.last_name) + ' ' + str(self.school)

    class Meta:
        ordering = ('last_name', 'first_name',)
        unique_together = ('first_name','last_name','email')


class Waiver(models.Model):
    file = models.FileField(blank=True, default='')
    uploaded_date = models.DateTimeField(auto_now_add=True, blank=True)


# Order model: one per teacher visit, summarizes what a teacher got
class Order(models.Model):
    # date the teacher visited TEP
    checkout_time = models.DateTimeField(auto_now_add=True, blank=True)

    # whether this order has been exported to csv yet
    downloaded = models.BooleanField(default=False)

    # teacher associated with the order
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, null=False, unique_for_month='checkout_time')

    # each order has many items, and many items are in many orders
    # items = models.ManyToManyField(
    #     Item, through='OrderItem', related_name='orders')

    # password_hash = models.CharField(max_length=100)
    def __str__(self):
        return str(self.pk) + '_' + str(self.teacher)

    class Meta:
        ordering = ('checkout_time', )


# Associative entity for order and item


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='order_items', on_delete=models.CASCADE, null=False)
    item = models.ForeignKey(
        Item, related_name='order_items', on_delete=models.CASCADE, null=False)

    # how many units of an item a teacher took (e.g. 8 (packs))
    units_taken = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return str(self.order)+ "_"+ str(self.item)+"_"+str(self.units_taken)



# ValidationPassword: the password that volunteers/TEP employees enter to validate the form
class ValidationPassword(models.Model):
    digest = models.CharField(max_length=65)
    uploaded_date = models.DateTimeField(default=datetime.now, blank=True)
    # hash_digest = models.CharField(max_length=65)
