import shutil
import tempfile
from decimal import Decimal
from io import BytesIO, StringIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from accounts.management.commands.seed_store import CATALOG
from accounts.models import Cart, Category, CustomUser, Order, OrderItem, Product

TEMP_MEDIA = tempfile.mkdtemp()


def image_upload(name='photo.png'):
    buffer = BytesIO()
    Image.new('RGB', (30, 40), 'navy').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class StoreTestCase(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser('boss', 'boss@example.com', 'pass12345')
        self.shopper = CustomUser.objects.create_user('shopper', 'shop@example.com', 'pass12345')
        self.men = Category.objects.create(name='Men')
        self.shirt = Product.objects.create(
            seller=self.admin, category=self.men, name='Linen Shirt',
            description='Soft linen.', price=Decimal('1500.00'), stock=3,
        )

    def login_admin(self):
        self.client.login(username='boss', password='pass12345')

    def login_shopper(self):
        self.client.login(username='shopper', password='pass12345')


class AdminAccessTests(StoreTestCase):

    admin_urls = [
        ('admin_dashboard', []),
        ('admin_products', []),
        ('admin_product_add', []),
        ('admin_product_edit', ['product']),
        ('admin_categories', []),
    ]

    def resolve(self, name, args):
        return reverse(name, args=[self.shirt.id] if args else [])

    def test_anonymous_and_regular_users_are_redirected(self):
        for name, args in self.admin_urls:
            url = self.resolve(name, args)
            self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}", msg_prefix=name)

        self.login_shopper()
        for name, args in self.admin_urls:
            self.assertEqual(self.client.get(self.resolve(name, args)).status_code, 302, name)

        response = self.client.post(reverse('admin_product_delete', args=[self.shirt.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(id=self.shirt.id).exists())

    def test_superuser_can_open_every_admin_page(self):
        self.login_admin()
        for name, args in self.admin_urls:
            self.assertEqual(self.client.get(self.resolve(name, args)).status_code, 200, name)

    def test_superuser_login_lands_on_admin_panel(self):
        response = self.client.post(reverse('login'), {'username': 'boss', 'password': 'pass12345'})
        self.assertRedirects(response, reverse('admin_dashboard'))


class AdminProductTests(StoreTestCase):

    def product_data(self, **overrides):
        data = {
            'name': 'Denim Jacket', 'category': self.men.id, 'description': 'Classic.',
            'price': '2499', 'stock': '7', 'is_available': 'on',
        }
        data.update(overrides)
        return data

    def test_add_product_with_image(self):
        self.login_admin()
        response = self.client.post(reverse('admin_product_add'), self.product_data(image=image_upload()))
        self.assertRedirects(response, reverse('admin_products'))

        product = Product.objects.get(name='Denim Jacket')
        self.assertEqual(product.seller, self.admin)
        self.assertEqual(product.price, Decimal('2499'))
        self.assertEqual(product.stock, 7)
        self.assertTrue(product.is_available)
        self.assertTrue(product.image.name.startswith('products/'))

        # And it is served from the database on the storefront.
        response = self.client.get(reverse('shop'), {'category': 'Men'})
        self.assertContains(response, 'Denim Jacket')
        self.assertContains(response, product.image.url)

    def test_invalid_input_shows_errors_instead_of_crashing(self):
        self.login_admin()
        cases = [
            self.product_data(price='abc'),
            self.product_data(price='0'),
            self.product_data(stock='-4'),
            self.product_data(name=''),
            self.product_data(category='9999'),
            self.product_data(image=SimpleUploadedFile('fake.png', b'not an image', content_type='image/png')),
        ]
        for data in cases:
            response = self.client.post(reverse('admin_product_add'), data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(list(response.context['messages']), data)
        self.assertFalse(Product.objects.filter(name='Denim Jacket').exists())

    def test_edit_product_keeps_image_unless_replaced_or_removed(self):
        self.login_admin()
        self.shirt.image = image_upload('first.png')
        self.shirt.save()
        original_image = self.shirt.image.name
        url = reverse('admin_product_edit', args=[self.shirt.id])

        self.client.post(url, self.product_data(name='Linen Shirt v2', stock='12'))
        self.shirt.refresh_from_db()
        self.assertEqual(self.shirt.name, 'Linen Shirt v2')
        self.assertEqual(self.shirt.stock, 12)
        self.assertTrue(self.shirt.is_available)
        self.assertEqual(self.shirt.image.name, original_image)
        self.assertEqual(self.shirt.seller, self.admin)

        self.client.post(url, self.product_data(image=image_upload('second.png')))
        self.shirt.refresh_from_db()
        self.assertNotEqual(self.shirt.image.name, original_image)

        self.client.post(url, self.product_data(**{'image-clear': 'on'}))
        self.shirt.refresh_from_db()
        self.assertFalse(self.shirt.image)

    def test_unchecking_available_hides_product(self):
        self.login_admin()
        data = self.product_data(name='Linen Shirt')
        del data['is_available']
        self.client.post(reverse('admin_product_edit', args=[self.shirt.id]), data)
        self.shirt.refresh_from_db()
        self.assertFalse(self.shirt.is_available)
        self.assertNotIn(self.shirt, self.client.get(reverse('shop')).context['products'])

    def test_failed_edit_does_not_rename_in_page_header(self):
        self.login_admin()
        response = self.client.post(
            reverse('admin_product_edit', args=[self.shirt.id]), self.product_data(price='oops'))
        self.assertEqual(response.context['product'].name, 'Linen Shirt')

    def test_toggle_availability_and_update_stock(self):
        self.login_admin()
        list_url = reverse('admin_products') + '?status=low-stock'

        response = self.client.post(reverse('admin_product_toggle', args=[self.shirt.id]), {'next': list_url})
        self.assertRedirects(response, list_url)
        self.shirt.refresh_from_db()
        self.assertFalse(self.shirt.is_available)

        self.client.post(reverse('admin_product_stock', args=[self.shirt.id]), {'stock': '42'})
        self.shirt.refresh_from_db()
        self.assertEqual(self.shirt.stock, 42)

        self.client.post(reverse('admin_product_stock', args=[self.shirt.id]), {'stock': '-1'})
        self.shirt.refresh_from_db()
        self.assertEqual(self.shirt.stock, 42)

    def test_next_parameter_cannot_redirect_off_site(self):
        self.login_admin()
        response = self.client.post(
            reverse('admin_product_stock', args=[self.shirt.id]),
            {'stock': '5', 'next': 'https://evil.example.com/'})
        self.assertRedirects(response, reverse('admin_products'))

    def test_list_filters(self):
        self.login_admin()
        Product.objects.create(seller=self.admin, category=self.men, name='Sold Out Tee',
                               description='', price=500, stock=0)
        response = self.client.get(reverse('admin_products'), {'status': 'out-of-stock'})
        self.assertEqual([p.name for p in response.context['products']], ['Sold Out Tee'])
        response = self.client.get(reverse('admin_products'), {'status': 'low-stock', 'category': self.men.id})
        self.assertEqual([p.name for p in response.context['products']], ['Linen Shirt'])

    def test_delete_product(self):
        self.login_admin()
        self.client.post(reverse('admin_product_delete', args=[self.shirt.id]))
        self.assertFalse(Product.objects.filter(id=self.shirt.id).exists())

    def test_cannot_delete_product_with_order_history(self):
        self.login_admin()
        order = Order.objects.create(user=self.shopper, full_name='S', phone='1', address='A', state='S',
                                     city='C', pincode='1', total_price=1650)
        OrderItem.objects.create(order=order, product=self.shirt, quantity=1, price=1500)
        self.client.post(reverse('admin_product_delete', args=[self.shirt.id]))
        self.assertTrue(Product.objects.filter(id=self.shirt.id).exists())
        self.assertEqual(order.items.count(), 1)


class AdminCategoryTests(StoreTestCase):

    def test_add_rename_delete_category(self):
        self.login_admin()
        self.client.post(reverse('admin_category_add'), {'name': 'Watches'})
        watches = Category.objects.get(name='Watches')

        self.client.post(reverse('admin_category_add'), {'name': 'watches'})
        self.assertEqual(Category.objects.filter(name__iexact='watches').count(), 1)

        self.client.post(reverse('admin_category_edit', args=[watches.id]), {'name': 'Luxury Watches'})
        watches.refresh_from_db()
        self.assertEqual(watches.name, 'Luxury Watches')

        self.client.post(reverse('admin_category_delete', args=[watches.id]))
        self.assertFalse(Category.objects.filter(id=watches.id).exists())

    def test_cannot_delete_category_with_products(self):
        self.login_admin()
        self.client.post(reverse('admin_category_delete', args=[self.men.id]))
        self.assertTrue(Category.objects.filter(id=self.men.id).exists())


class SeedStoreTests(StoreTestCase):

    def test_seed_creates_catalog_with_images_and_is_idempotent(self):
        call_command('seed_store', stdout=StringIO())

        for category_name, products in CATALOG.items():
            category = Category.objects.get(name=category_name)
            seeded = Product.objects.filter(category=category, name__in=[p[0] for p in products])
            self.assertEqual(seeded.count(), len(products), category_name)
            self.assertTrue(4 <= len(products) <= 5)
            for product in seeded:
                self.assertTrue(product.image, product.name)
                self.assertTrue(product.image.storage.exists(product.image.name), product.name)
                self.assertTrue(product.is_available)

        # The pre-existing "Men" category is reused, not duplicated.
        self.assertEqual(Category.objects.filter(name__iexact='men').count(), 1)

        counts = (Category.objects.count(), Product.objects.count())
        call_command('seed_store', stdout=StringIO())
        self.assertEqual((Category.objects.count(), Product.objects.count()), counts)


class ShoppingFlowTests(StoreTestCase):

    def setUp(self):
        super().setUp()
        call_command('seed_store', stdout=StringIO())

    def test_full_purchase_flow(self):
        self.login_shopper()

        # Open a category from the collections page.
        response = self.client.get(reverse('collections'))
        self.assertEqual(response.status_code, 200)
        women = Category.objects.get(name='Women')
        response = self.client.get(reverse('collections'), {'category': women.id})
        self.assertEqual(response.status_code, 200)
        dress = Product.objects.get(name='Tangerine Tiered Sundress')
        self.assertContains(response, dress.name)
        for other in Product.objects.exclude(category=women):
            self.assertNotContains(response, f'>{other.name}<')

        response = self.client.get(reverse('shop'), {'category': 'Women'})
        self.assertContains(response, reverse('product_detail', args=[dress.id]))

        # View button -> product page.
        response = self.client.get(reverse('product_detail', args=[dress.id]))
        self.assertContains(response, dress.name)
        self.assertContains(response, dress.image.url)
        self.assertContains(response, reverse('add_to_cart', args=[dress.id]))

        # Add to cart and view it.
        self.assertRedirects(self.client.get(reverse('add_to_cart', args=[dress.id])), reverse('cart'))
        response = self.client.get(reverse('cart'))
        self.assertContains(response, dress.name)
        item = Cart.objects.get(user=self.shopper, product=dress)

        # Update quantity.
        self.client.get(reverse('increase_cart', args=[item.id]))
        self.client.get(reverse('increase_cart', args=[item.id]))
        self.client.get(reverse('decrease_cart', args=[item.id]))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.context['subtotal'], dress.price * 2)

        # Checkout.
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total'], dress.price * 2 + 150)

        stock_before = dress.stock
        response = self.client.post(reverse('checkout'), {
            'full_name': 'Asha Shopper', 'email': 'shop@example.com', 'phone': '9876543210',
            'address': '12 MG Road', 'city': 'Kochi', 'state': 'Kerala', 'pincode': '682001',
            'payment': 'UPI',
        })
        self.assertRedirects(response, reverse('order_success'))

        order = Order.objects.get(user=self.shopper)
        self.assertEqual(order.total_price, dress.price * 2 + 150)
        self.assertEqual(order.payment_method, 'UPI')
        self.assertEqual(order.items.get().quantity, 2)
        self.assertFalse(Cart.objects.filter(user=self.shopper).exists())
        dress.refresh_from_db()
        self.assertEqual(dress.stock, stock_before - 2)

        # The order shows up for the customer and the admin.
        self.assertContains(self.client.get(reverse('orders')), f'#{order.id}')
        self.assertEqual(self.client.get(reverse('order_detail', args=[order.id])).status_code, 200)
        self.client.logout()
        self.login_admin()
        self.assertContains(self.client.get(reverse('admin_dashboard')), f'#{order.id}')

    def test_cart_quantity_is_capped_at_stock(self):
        self.login_shopper()
        loafers = Product.objects.get(name='Tan Perforated Loafers')  # stock 3
        for _ in range(5):
            self.client.get(reverse('add_to_cart', args=[loafers.id]))
        item = Cart.objects.get(user=self.shopper, product=loafers)
        self.assertEqual(item.quantity, 3)
        self.client.get(reverse('increase_cart', args=[item.id]))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

    def test_checkout_rejects_items_that_sold_out(self):
        self.login_shopper()
        loafers = Product.objects.get(name='Tan Perforated Loafers')
        self.client.get(reverse('add_to_cart', args=[loafers.id]))
        Product.objects.filter(id=loafers.id).update(stock=0)

        response = self.client.post(reverse('checkout'), {
            'full_name': 'A', 'phone': '1', 'address': 'B', 'city': 'C', 'state': 'D',
            'pincode': '1', 'payment': 'COD',
        })
        self.assertRedirects(response, reverse('cart'))
        self.assertFalse(Order.objects.exists())
        self.assertTrue(Cart.objects.filter(user=self.shopper).exists())

    def test_checkout_with_missing_fields_shows_error(self):
        self.login_shopper()
        self.client.get(reverse('add_to_cart', args=[self.shirt.id]))
        response = self.client.post(reverse('checkout'), {'full_name': 'A', 'payment': 'COD'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())

    def test_public_pages_render_with_catalog(self):
        for url in [reverse('home'), reverse('shop'), reverse('collections'), reverse('category'),
                    reverse('search') + '?q=shirt', reverse('about'), reverse('contact')]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        for category_name in CATALOG:
            response = self.client.get(reverse('shop'), {'category': category_name})
            self.assertEqual(len(response.context['products']), 5 + (category_name == 'Men'), category_name)
