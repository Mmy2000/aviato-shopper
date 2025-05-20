from django.db import models
from accounts.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(User,verbose_name=_("user payment"), on_delete=models.CASCADE)
    payment_id = models.CharField(_("payment_id"), max_length=100)
    payment_method = models.CharField(_("payment_method"), max_length=100)
    payment_paid = models.CharField( _("payment_paid"),max_length=100)
    status = models.CharField(_("status"), max_length=100)
    created_at = models.DateTimeField( _("created_at"),default=timezone.now)

    class Meta:
        verbose_name = _("Payments")
        verbose_name_plural = _("Payment")

    def __str__(self):
        return self.payment_id
    

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('On Delivery', 'On Delivery'),  # Add On Delivery status here
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, verbose_name=_("user order"),on_delete=models.SET_NULL , null=True)
    payment = models.ForeignKey(Payment,  verbose_name=_("payment order"),on_delete=models.SET_NULL ,blank=True , null=True)
    order_number = models.CharField(_("order_number"),max_length=50)
    first_name = models.CharField(_("first_name"),max_length=50)
    last_name = models.CharField(_("last_name"),max_length=50)
    phone = models.CharField(_("phone"),max_length=50)
    zip_code = models.CharField(_("zip_code"),max_length=50,blank=True)
    email = models.EmailField(_("email"), max_length=254)
    address_line_1 = models.CharField(_("address_line_1"), max_length=50)
    address_line_2 = models.CharField(_("address_line_2"), max_length=50 , blank=True)
    country = models.CharField(_("country"), max_length=50 )
    state = models.CharField(_("state"), max_length=50 )
    payment_method = models.CharField(_("payment_method"), max_length=50 )
    city = models.CharField(_("city"), max_length=50 )
    order_note = models.CharField(_("order_note"), max_length=1000 , blank=True)
    order_total = models.FloatField(_("order_total"),)
    tax = models.FloatField(_("tax"),)
    status = models.CharField(_("status"),choices=STATUS,default='New' , max_length=15)
    ip = models.CharField(_("ip"),max_length=50  ,blank=True)
    is_orderd = models.BooleanField(_("is_orderd"),default=False)
    delivered_date = models.DateTimeField(blank=True,null=True)
    created_at = models.DateTimeField(_("created_at"), default=timezone.now)
    updated_at = models.DateTimeField(_("updated_at"),default=timezone.now)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
    @property
    def is_cancellable(self):
        if self.delivered_date and self.status != 'Cancelled':
            now = timezone.now()
            one_day_before_delivery = self.delivered_date - timedelta(days=1)
            # Not cancellable if current time is after one day before the delivery date
            return now < one_day_before_delivery
        return False  # If there's no delivered_date, assume it's still cancellable
    
    class Meta:
        verbose_name = _("Orders")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return self.first_name
    
class OrderProduct(models.Model):
    payment = models.ForeignKey(Payment, verbose_name=_("payment order"),on_delete=models.SET_NULL ,blank=True , null=True)
    user = models.ForeignKey(User, verbose_name=_("user order"),on_delete=models.CASCADE)
    order = models.ForeignKey(Order, verbose_name=_("order"),on_delete=models.CASCADE)
    product = models.ForeignKey("store.Product", verbose_name=_("order product"),on_delete=models.CASCADE)
    variations = models.ManyToManyField("store.Variation",blank=True)
    quantity = models.IntegerField(_("quantity"),)
    product_price = models.FloatField(_("product_price"),)
    ordered = models.BooleanField(_("ordered"),default=False)
    created_at = models.DateTimeField(_("created_at"), default=timezone.now)
    updated_at = models.DateTimeField(_("updated_at"),default=timezone.now)

    class Meta:
        verbose_name = _("Order Products")
        verbose_name_plural = _("Order Products")

    def __str__(self):
        return self.product.name
    
class RefundPayment(models.Model):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("completed", "completed"),
        ("failed", "failed"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds")
    payment_id = models.CharField(max_length=100)
    sale_id = models.CharField(max_length=100)
    refund_id = models.CharField(max_length=100)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_from_transaction_fee = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    status = models.CharField(choices=STATUS_CHOICES, default="pending", max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    response_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Refund for {self.order} - {self.status}"