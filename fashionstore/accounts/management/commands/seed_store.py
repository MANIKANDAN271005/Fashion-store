"""
Load the starter fashion catalog into the database.

    python manage.py seed_store                 # uses the first superuser as seller
    python manage.py seed_store --seller admin

Safe to run repeatedly: existing categories and products (matched by name) are
left untouched, except that a seeded product missing its image gets one again.
Images are copied from static/images, resized, and saved to MEDIA_ROOT/products/
just like an image uploaded through the admin panel.
"""

from decimal import Decimal
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from PIL import Image

from accounts.models import Category, Product

IMAGE_DIR = Path(settings.BASE_DIR) / 'static' / 'images'
MAX_IMAGE_SIZE = (1000, 1300)

# category -> [(name, price, stock, source image, description)]
CATALOG = {
    'Men': [
        ('Earth Brown Casual Shirt', '1499', 25, 'men6.png',
         'A relaxed-fit cotton shirt in a rich earth-brown tone. Soft, breathable and easy to dress up '
         'with chinos or down with denim.'),
        ('Purple Floral Relaxed Shirt', '1799', 18, 'men7.png',
         'Statement short-sleeve shirt with an all-over purple floral print and a camp collar. '
         'Lightweight viscose drapes beautifully for summer evenings.'),
        ('Sky Blue Linen Shirt', '1999', 22, 'men9.png',
         'Pure linen shirt in a crisp sky-blue shade with a classic collar and full sleeves. '
         'Gets softer with every wash.'),
        ('Black Contrast-Stitch Oversized Tee', '899', 40, 'men4.jpg',
         'Heavyweight cotton tee with a dropped shoulder, oversized silhouette and contrast '
         'stitching at the seams.'),
        ('Mustard Knit Polo', '1299', 4, 'men10.png',
         'Textured knit polo in a warm mustard hue with a clean button placket and ribbed cuffs.'),
        ('Black Leather Biker Jacket', '4999', 8, 'jacket-biker.jpg',
         'Classic biker jacket in soft black faux leather with an asymmetric zip, snap-down '
         'collar and zipped cuffs. Layer it over a tee for an effortless edge.'),
    ],
    'Women': [
        ('Tangerine Tiered Sundress', '2199', 15, 'women8.png',
         'Breezy V-neck sundress with flutter sleeves and a tiered skirt in a vibrant tangerine '
         'shade. Perfect for brunches and beach days.'),
        ('Ivory Embroidered Kurta Set', '3499', 10, 'women9.png',
         'Elegant ivory kurta with colourful yoke embroidery, paired with straight pants and a '
         'sheer dupatta. Made for festive occasions.'),
        ('Denim Co-ord Set', '2799', 12, 'women10.png',
         'Relaxed denim top with raw-edge hem and matching wide-leg trousers. Wear together or '
         'style each piece separately.'),
        ('Floral Print Button-Down Shirt', '1599', 20, 'women6.png',
         'Soft, flowy shirt with a hand-painted floral print. Tuck it into high-waist trousers '
         'for a polished look.'),
        ('Block Print Cotton Kurti', '999', 30, 'Kurti.png',
         'Everyday cotton kurti with a traditional block print, round neck and three-quarter '
         'sleeves.'),
    ],
    'Kids': [
        ("Daddy's Little Princess Hoodie", '899', 25, 'kids1.jpg',
         'Cosy fleece-lined hoodie with contrast red raglan sleeves and a playful slogan print.'),
        ('Lime Pinafore Dress', '1099', 18, 'kids2.jpg',
         'Sweet corduroy pinafore dress in a fresh lime shade, layered over a white tee. Easy '
         'button fastening at the shoulders.'),
        ('Linen Shirt & Shorts Set', '1299', 14, 'kids3.png',
         'Two-piece set in breathable linen blend — a short-sleeve shirt with matching '
         'drawstring shorts.'),
        ('Graphic Tee & Cargo Jeans Set', '1499', 16, 'kids4.png',
         'Soft cotton graphic tee paired with durable cargo jeans with utility pockets. Built '
         'for playtime.'),
        ('Printed Top & Palazzo Set', '1199', 12, 'Kids - Age 7to8.png',
         'Flowy printed top with matching palazzo pants in a comfortable cotton blend. '
         'Ideal for ages 7–8.'),
    ],
    'Shoes': [
        ('Classic Brown Leather Oxfords', '3499', 12, 'shoes3.jpg',
         'Handcrafted cap-toe oxfords in polished brown leather with a cushioned insole. A '
         'wardrobe essential for formal wear.'),
        ('Retro Suede Sneakers', '2999', 20, 'shoes6.png',
         'Chunky low-top sneakers in soft suede with contrast stripes and a grippy rubber sole.'),
        ("Men's Black Chelsea Boots", '3999', 8, 'shoes7.png',
         'Sleek black leather Chelsea boots with elastic side panels and a stacked heel.'),
        ('Tan Perforated Loafers', '2499', 3, 'shoes8.png',
         'Slip-on loafers in tan leather with breathable perforated detailing. Smart-casual '
         'comfort all day.'),
        ('Pastel Low-Top Sneakers', '3299', 18, 'Shoes - Nike.png',
         'Clean white leather sneakers with a pastel pink accent — light, comfortable and '
         'easy to pair.'),
    ],
    'Accessories': [
        ('Tan Leather Satchel Bag', '2799', 10, 'Accessories6.png',
         'Structured satchel in smooth tan leather with a top handle and detachable '
         'shoulder strap.'),
        ('Wool Felt Fedora Hat', '1199', 15, 'Accessories1.jpg',
         'Classic fedora in soft wool felt with a grosgrain band. Available in neutral shades.'),
        ('Statement Earrings Collection', '599', 35, 'Accessories - Earrings.png',
         'A curated set of lightweight fashion earrings — hoops, drops and studs for every '
         'outfit.'),
        ('Boho Bracelet & Sunglasses Set', '999', 20, 'Accessories3.png',
         'Layered beaded bracelets paired with retro tinted sunglasses for an effortless '
         'boho look.'),
        ('Autumn Scarf & Accessories Edit', '1499', 12, 'Accessories5.jpg',
         'Printed silk-feel scarf curated with coordinating accessories for the season.'),
    ],
    'Watches': [
        ('Gold Tone Classic Watch', '4999', 8, 'watches4.png',
         'Timeless gold-tone stainless steel watch with a sunray dial and date window.'),
        ('Minimal Black Leather Watch', '2499', 15, 'watches5.png',
         'Ultra-slim case with a clean black dial and a soft black leather strap.'),
        ('Gold Chronograph Sports Watch', '6499', 6, 'watches7.png',
         'Bold chronograph with a gold bezel, black dial, sub-dials and a leather strap.'),
        ('Black Steel Chronograph', '5499', 10, 'watches8.png',
         'Sporty chronograph with a black dial and a matching black link bracelet.'),
        ('Blue Dial Square Watch', '3999', 5, 'watches3.jpg',
         'Modern square case with a gradient blue dial and a brushed steel bracelet.'),
    ],
}


def product_image(filename):
    """Open a catalog photo, shrink it for the web and return it as a JPEG ContentFile."""

    with Image.open(IMAGE_DIR / filename) as img:
        img = img.convert('RGBA') if img.mode in ('P', 'LA') else img
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, 'white')
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert('RGB')
        img.thumbnail(MAX_IMAGE_SIZE)

        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)

    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = 'Create the starter fashion categories and products (with images).'

    def add_arguments(self, parser):
        parser.add_argument('--seller', help='Username that will own the products (default: first superuser).')

    def handle(self, *args, **options):

        seller = self.get_seller(options['seller'])

        missing = sorted({
            image for products in CATALOG.values()
            for _, _, _, image, _ in products
            if not (IMAGE_DIR / image).exists()
        })
        if missing:
            raise CommandError(f'Missing images in {IMAGE_DIR}: {", ".join(missing)}')

        created_categories = created_products = images_added = 0

        with transaction.atomic():

            for category_name, products in CATALOG.items():

                category = Category.objects.filter(name__iexact=category_name).first()
                if category is None:
                    category = Category.objects.create(name=category_name)
                    created_categories += 1

                for name, price, stock, image, description in products:

                    product = Product.objects.filter(name__iexact=name, category=category).first()

                    if product is None:
                        product = Product.objects.create(
                            seller=seller,
                            category=category,
                            name=name,
                            description=description,
                            price=Decimal(price),
                            stock=stock,
                            is_available=True,
                        )
                        created_products += 1

                    if not product.image:
                        product.image.save(f'{slugify(name)}.jpg', product_image(image))
                        images_added += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created_categories} new categories, {created_products} new products '
            f'and {images_added} product images (seller: {seller.username}).'
        ))

    def get_seller(self, username):

        User = get_user_model()

        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'No user named "{username}".')

        seller = User.objects.filter(is_superuser=True).order_by('id').first()
        if seller is None:
            raise CommandError('Create an admin first: python manage.py createsuperuser')
        return seller
