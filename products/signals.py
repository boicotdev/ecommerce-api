from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, Order, OrderProduct, Product

@receiver(post_save, sender=Payment)
def update_order_and_stock(sender, instance, created, **kwargs):
    """
    Signal que actualiza el estado de la orden, calcula el total del pago y ajusta el stock
    cuando se confirma un pago.
    """
    if created:  # Solo ejecutar cuando se crea un nuevo pago
        try:
            order = instance.order  # Obtener la orden relacionada con el pago

            # Calcular el monto total del pago basado en los productos de la orden
            order_products = OrderProduct.objects.filter(order=order)
            total_payment_amount = sum(
                item.product.price * item.quantity for item in order_products
            )

            # Asignar el monto calculado al Payment y guardarlo
            instance.payment_amount = total_payment_amount
            print(instance)
            instance.save()

            # Verificar que la orden aún está en estado "PENDING"
            if order.status == "PENDING":
                order.status = "PROCESSING"
                order.save()

                # Reducir el stock de los productos de la orden
                for order_product in order_products:
                    product = order_product.product  # Obtener el producto
                    if product.stock >= order_product.quantity:
                        product.stock -= order_product.quantity  # Reducir el stock
                        product.save()
                    else:
                        print(f"Stock insuficiente para {product.name}")

                print(f"Orden {order.id} actualizada a 'PROCESSING', stock ajustado y pago calculado.")

        except Order.DoesNotExist:
            print("No se encontró la orden asociada al pago")
