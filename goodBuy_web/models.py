from django.db import models
from django.contrib.auth.models import AbstractUser

class GroupClassification(models.Model):
    group_classification_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class State(models.Model):
    state_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Permission(models.Model):
    permission_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    owner = models.EmailField()
    introduce = models.TextField()
    group_classification = models.ForeignKey(GroupClassification, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True)
    img = models.ImageField(upload_to='group_images/', null=True, blank=True)
    endtime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    email = models.EmailField(unique=True)
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='user_images/', null=True, blank=True)
    register_date = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Admin(models.Model):
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('email', 'group')

class OrderState(models.Model):
    order_state_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_pay = models.BooleanField(default=False)
    tot = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    link = models.URLField(null=True, blank=True)
    update = models.DateTimeField(auto_now=True)
    order_state = models.ForeignKey(OrderState, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.email}"

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    amount = models.IntegerField()
    introduce = models.TextField()
    img = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class ProductOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'product')

class Comment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    rank = models.IntegerField()
    comment = models.TextField()
    postdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order', 'email')

class Follow(models.Model):
    user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    follow = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'follow')
