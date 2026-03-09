from django.conf import settings
from .models import Product

class Wishlist:
    def __init__(self, request):
        """
        Initialize the wishlist.
        """
        self.session = request.session
        wishlist = self.session.get(settings.WISHLIST_SESSION_ID)
        if not wishlist:
            # save an empty wishlist in the session
            wishlist = self.session[settings.WISHLIST_SESSION_ID] = []
        self.wishlist = wishlist

    def add(self, product):
        """
        Add a product to the wishlist if it doesn't already exist.
        """
        product_id = product.id
        if product_id not in self.wishlist:
            self.wishlist.append(product_id)
            self.save()

    def remove(self, product):
        """
        Remove a product from the wishlist.
        """
        product_id = product.id
        if product_id in self.wishlist:
            self.wishlist.remove(product_id)
            self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over the items in the wishlist and get the products
        from the database.
        """
        products = Product.objects.filter(id__in=self.wishlist)
        for product in products:
            yield product

    def __len__(self):
        """
        Count all items in the wishlist.
        """
        return len(self.wishlist)

    def clear(self):
        # remove wishlist from session
        del self.session[settings.WISHLIST_SESSION_ID]
        self.save()
