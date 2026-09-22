from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import Profile
from apps.perfumes.models import Perfume
from apps.reviews.models import Occasion, OccasionVote, Rating, Review, Sentiment

User = get_user_model()

PERFUMES = [
    {
        "name": "Noche de Sándalo",
        "brand": "Esencias",
        "description": "Una estela amaderada y cálida, con sándalo cremoso, ámbar suave y un fondo de vainilla ahumada.",
        "notes": "Sándalo · Ámbar · Vainilla",
        "image_url": "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=800&q=80",
        "price": "89.00",
    },
    {
        "name": "Citrus Aurora",
        "brand": "Esencias",
        "description": "Bergamota brillante, lima y neroli para los días de calor. Fresca, nítida y fácil de llevar.",
        "notes": "Bergamota · Lima · Neroli",
        "image_url": "https://images.unsplash.com/photo-1594035910387-fea47794261f?auto=format&fit=crop&w=800&q=80",
        "price": "72.00",
    },
    {
        "name": "Rosa de Medianoche",
        "brand": "Maison Luna",
        "description": "Rosa de Damasco envuelta en pachulí y almizcle. Elegante, intensa y pensada para la noche.",
        "notes": "Rosa · Pachulí · Almizcle",
        "image_url": "https://images.unsplash.com/photo-1615634260167-c8cdede054de?auto=format&fit=crop&w=800&q=80",
        "price": "115.00",
    },
    {
        "name": "Brisa Marina",
        "brand": "Costa Atelier",
        "description": "Notas acuáticas, sal marina y cedro claro. Recuerda a una tarde de verano frente al océano.",
        "notes": "Sal marina · Cedro · Acuática",
        "image_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=800&q=80",
        "price": "64.00",
    },
    {
        "name": "Vainilla Nómada",
        "brand": "Maison Luna",
        "description": "Vainilla gourmand con tonka, café tostado y un toque de canela. Dulce, pero con carácter.",
        "notes": "Vainilla · Tonka · Café",
        "image_url": "https://images.pexels.com/photos/1961795/pexels-photo-1961795.jpeg?auto=compress&cs=tinysrgb&w=800",
        "price": "98.00",
    },
    {
        "name": "Bosque de Cedro",
        "brand": "Atelier Norte",
        "description": "Cedro, vetiver e incienso. Seco, verde y envolvente; ideal para otoño e invierno.",
        "notes": "Cedro · Vetiver · Incienso",
        "image_url": "https://images.pexels.com/photos/965989/pexels-photo-965989.jpeg?auto=compress&cs=tinysrgb&w=800",
        "price": "81.00",
    },
]


class Command(BaseCommand):
    help = "Create demo admin/customer users and a starter perfume catalog."

    def handle(self, *args, **options):
        admin = self._user(
            username="admin",
            email="admin@esencias.local",
            password="Admin1234!",
            first_name="Admin",
            staff=True,
            role=Profile.Role.ADMIN,
        )
        customer = self._user(
            username="bryan",
            email="bryanalzate007@gmail.com",
            password="User1234!",
            first_name="Bryan",
            staff=False,
            role=Profile.Role.CUSTOMER,
        )

        created_perfumes = []
        for data in PERFUMES:
            perfume, _ = Perfume.objects.update_or_create(
                name=data["name"],
                brand=data["brand"],
                defaults=data,
            )
            created_perfumes.append(perfume)

        first, second, third = created_perfumes[:3]
        Review.objects.get_or_create(
            perfume=first,
            user=customer,
            defaults={"body": "Me encanta para cenas. La estela dura toda la noche."},
        )
        Review.objects.get_or_create(
            perfume=second,
            user=customer,
            defaults={"body": "Perfecta para la oficina en primavera. Muy fresca."},
        )
        Rating.objects.update_or_create(
            perfume=first, user=customer, defaults={"sentiment": Sentiment.LOVE}
        )
        Rating.objects.update_or_create(
            perfume=second, user=customer, defaults={"sentiment": Sentiment.LIKE}
        )
        OccasionVote.objects.get_or_create(perfume=first, user=customer, occasion=Occasion.NIGHT)
        OccasionVote.objects.get_or_create(perfume=first, user=customer, occasion=Occasion.WINTER)
        OccasionVote.objects.get_or_create(perfume=second, user=customer, occasion=Occasion.DAY)
        OccasionVote.objects.get_or_create(perfume=second, user=customer, occasion=Occasion.SPRING)

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write("Admin: admin / Admin1234!")
        self.stdout.write("Usuario: bryan / User1234! (bryanalzate007@gmail.com)")
        self.stdout.write(f"Perfumes: {len(created_perfumes)}")
        self.stdout.write(f"Admin user id: {admin.id}")

    def _user(self, *, username, email, password, first_name, staff, role):
        from allauth.account.models import EmailAddress

        user = User.objects.filter(username=username).first()
        if user is None and username == "bryan":
            user = User.objects.filter(username="sofia").first()
        if user is None:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                is_staff=staff,
                is_superuser=staff,
            )
        else:
            user.username = username
            user.email = email
            user.first_name = first_name
            user.is_staff = staff
            user.is_superuser = staff
            user.set_password(password)
            user.save()
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.country = "Colombia"
        profile.save()
        EmailAddress.objects.filter(user=user).exclude(email=email).delete()
        EmailAddress.objects.update_or_create(
            user=user,
            email=email,
            defaults={"primary": True, "verified": True},
        )
        return user
