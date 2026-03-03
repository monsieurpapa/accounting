from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """Product category (e.g., Office Supplies, Hardware)."""
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="product_categories")
    name = models.CharField(_("Category Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        unique_together = [("organization", "name")]

    def __str__(self):
        return self.name

class Product(models.Model):
    """Represents a product in stock."""
    UNIT_CHOICES = [
        ("UNIT", _("Unit")),
        ("KG", _("Kilogram")),
        ("L", _("Liter")),
        ("M", _("Meter")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="products")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    code = models.CharField(_("Product Code"), max_length=50)
    name = models.CharField(_("Product Name"), max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    unit = models.CharField(_("Unit"), max_length=10, choices=UNIT_CHOICES, default="UNIT")
    description = models.TextField(_("Description"), blank=True, null=True)
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        unique_together = [("organization", "code")]



    def __str__(self):
        return f"{self.code} - {self.name}"

class StockLevel(models.Model):
    """Tracks current quantity per product."""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="stock_level")
    quantity = models.DecimalField(_("Current Quantity"), max_digits=15, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name}: {self.quantity} {self.product.get_unit_display()}"

class StockMovement(models.Model):
    """Records stock inflows and outflows."""
    MOVEMENT_TYPE_CHOICES = [
        ("IN", _("Stock In")),
        ("OUT", _("Stock Out")),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    movement_type = models.CharField(_("Movement Type"), max_length=3, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.DecimalField(_("Quantity"), max_digits=15, decimal_places=2)
    date = models.DateTimeField(_("Date"), auto_now_add=True)
    reference = models.CharField(_("Reference"), max_length=255, blank=True, null=True) # e.g., Purchase reference or Sale invoice
    description = models.TextField(_("Description"), blank=True, null=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Stock Movement")
        verbose_name_plural = _("Stock Movements")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Update StockLevel
            stock_level, created = StockLevel.objects.get_or_create(product=self.product)
            if self.movement_type == 'IN':
                stock_level.quantity += self.quantity
            else:
                stock_level.quantity -= self.quantity
            stock_level.save()
