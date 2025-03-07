from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, Order, OrderProduct, Product

@receiver(post_save, sender=Payment)
def update_order_and_stock(sender, instance, created, **kwargs):
    delivery = 5000
    """
    Signal que actualiza el estado de la orden, ajusta el stock cuando se confirma un pago.
    """
    if created:
        try:
            order = instance.order
            order_products = OrderProduct.objects.filter(order=order)
            if order.status == "PENDING":
                order.status = "PROCESSING"
                order.save()

                # Reduce the Product.stock
                for order_product in order_products:
                    product = order_product.product
                    if product.stock >= order_product.quantity:
                        product.stock -= order_product.quantity
                        product.save()
                    else:
                        print(f"Stock insuficiente para {product.name}")


        except Order.DoesNotExist:
            print("No se encontró la orden asociada al pago")