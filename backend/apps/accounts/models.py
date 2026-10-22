import secrets
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.utils import timezone


class Profile(models.Model):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        ADMIN = "admin", "Admin"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    country = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    profile_person = models.ForeignKey('Profile_person', on_delete=models.CASCADE, related_name='profiles', null=True, blank=True)
    preferred_language = models.CharField(max_length=8, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"



class DataDeletionRequest(models.Model):
    class Status(models.TextChoices):
        DELETED = "deleted", "Eliminada"
        ABSENT = "absent", "Sin datos"
        KEPT = "kept", "Conservada"

    confirmation_code = models.CharField(max_length=64, unique=True)
    facebook_user_id = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.confirmation_code


class Profile_person(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ["name"]

  def __str__(self):
    return self.name


_REFERRAL_CODE_ALPHABET = string.ascii_uppercase + string.digits
_REFERRAL_CODE_LENGTH = 8


def generate_referral_code():
    return "".join(secrets.choice(_REFERRAL_CODE_ALPHABET) for _ in range(_REFERRAL_CODE_LENGTH))


class PointsAccount(models.Model):
    """Saldo de puntos. Se habilita con la primera compra y vuelve a cero al redimir."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="points_account",
    )
    enabled = models.BooleanField(
        default=False,
        help_text="Se activa con la primera compra. Habilita puntos y referidos.",
    )
    enabled_at = models.DateTimeField(null=True, blank=True)
    balance = models.PositiveIntegerField(default=0)
    referral_code = models.CharField(max_length=8, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cuenta de puntos"
        verbose_name_plural = "Cuentas de puntos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} · {self.balance} pts"

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self._unused_referral_code()
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"referral_code"}
        super().save(*args, **kwargs)

    def enable(self):
        if self.enabled:
            return
        now = timezone.now()
        with transaction.atomic():
            account = PointsAccount.objects.select_for_update().get(pk=self.pk)
            if account.enabled:
                self.enabled = True
                self.enabled_at = account.enabled_at
                return
            account.enabled = True
            account.enabled_at = now
            account.save(update_fields=["enabled", "enabled_at", "updated_at"])
        self.enabled = True
        self.enabled_at = now

    def add_points(self, points, source, *, order=None, referral=None):
        if points <= 0:
            raise ValidationError("Los puntos deben ser mayores a cero.")
        if source == PointEntry.Source.PURCHASE and order is None:
            raise ValidationError("Una compra debe indicar el pedido.")
        if source == PointEntry.Source.REFERRAL and referral is None:
            raise ValidationError("Un referido debe indicar la referencia.")

        with transaction.atomic():
            account = PointsAccount.objects.select_for_update().get(pk=self.pk)
            if not account.enabled:
                raise ValidationError("Los puntos se habilitan después de la primera compra.")
            if order is not None and order.user_id != account.user_id:
                raise ValidationError("El pedido no pertenece a esta cuenta.")
            if referral is not None and referral.referrer_id != account.user_id:
                raise ValidationError("El referido no pertenece a esta cuenta.")
            entry = PointEntry.objects.create(
                account=account,
                source=source,
                points=points,
                status=PointEntry.Status.AVAILABLE,
                order=order,
                referral=referral,
            )
            account.balance += points
            account.save(update_fields=["balance", "updated_at"])
        self.balance = account.balance
        return entry

    def redeem(self):
        """Redime el saldo completo. El historial de origen y estados se conserva."""
        now = timezone.now()
        with transaction.atomic():
            account = PointsAccount.objects.select_for_update().get(pk=self.pk)
            available = list(
                account.entries.select_for_update().filter(status=PointEntry.Status.AVAILABLE)
            )
            total = sum(entry.points for entry in available)
            if total == 0:
                if account.balance != 0:
                    account.balance = 0
                    account.save(update_fields=["balance", "updated_at"])
                    self.balance = 0
                return None
            redemption = PointRedemption.objects.create(account=account, points=total)
            for entry in available:
                entry.status = PointEntry.Status.REDEEMED
                entry.redeemed_at = now
                entry.redemption = redemption
                entry.save(update_fields=["status", "redeemed_at", "redemption"])
                PointEntryEvent.objects.create(entry=entry, status=PointEntry.Status.REDEEMED)
            account.balance = 0
            account.save(update_fields=["balance", "updated_at"])
        self.balance = 0
        return redemption

    @staticmethod
    def _unused_referral_code():
        for _ in range(10):
            code = generate_referral_code()
            if not PointsAccount.objects.filter(referral_code=code).exists():
                return code
        raise ValidationError("No se pudo generar un código de referido.")


class PointEntry(models.Model):
    """Lote de puntos recibido. Conserva el origen aunque el saldo ya esté en cero."""

    class Source(models.TextChoices):
        PURCHASE = "purchase", "Compra"
        REFERRAL = "referral", "Referido"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Disponibles"
        REDEEMED = "redeemed", "Redimidos"

    account = models.ForeignKey(PointsAccount, related_name="entries", on_delete=models.CASCADE)
    source = models.CharField(max_length=20, choices=Source.choices)
    points = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    order = models.ForeignKey(
        "purchases.Order",
        related_name="point_entries",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    referral = models.ForeignKey(
        "Referral",
        related_name="point_entries",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    redemption = models.ForeignKey(
        "PointRedemption",
        related_name="entries",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    redeemed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Puntos recibidos"
        verbose_name_plural = "Puntos recibidos"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["account", "status"])]
        constraints = [
            models.CheckConstraint(check=models.Q(points__gt=0), name="point_entry_points_positive"),
        ]

    def __str__(self):
        return f"{self.get_source_display()} · {self.points} pts"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            PointEntryEvent.objects.create(entry=self, status=self.status)


class PointEntryEvent(models.Model):
    """Fecha en la que un lote de puntos cambió de estado."""

    entry = models.ForeignKey(PointEntry, related_name="events", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=PointEntry.Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Estado de puntos"
        verbose_name_plural = "Estados de puntos"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_status_display()} · {self.created_at}"


class PointRedemption(models.Model):
    """Momento en que el saldo volvió a cero."""

    account = models.ForeignKey(PointsAccount, related_name="redemptions", on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Redención de puntos"
        verbose_name_plural = "Redenciones de puntos"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(check=models.Q(points__gt=0), name="point_redemption_points_positive"),
        ]

    def __str__(self):
        return f"{self.points} pts · {self.created_at}"


class Referral(models.Model):
    """Referido de un cliente que ya hizo su primera compra. Al referir se suman puntos."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        CREDITED = "credited", "Acreditado"

    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="referrals_made",
        on_delete=models.PROTECT,
    )
    referred = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="referral_received",
        on_delete=models.PROTECT,
    )
    code = models.CharField(max_length=8)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    points_awarded = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Referido"
        verbose_name_plural = "Referidos"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["referrer", "status"])]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(referrer=models.F("referred")),
                name="referral_no_self_reference",
            ),
        ]

    def __str__(self):
        return f"{self.referrer} → {self.referred}"

    def save(self, *args, **kwargs):
        if not self.code and self.referrer_id:
            account = PointsAccount.objects.filter(user_id=self.referrer_id).only("referral_code").first()
            if account:
                self.code = account.referral_code
                update_fields = kwargs.get("update_fields")
                if update_fields is not None:
                    kwargs["update_fields"] = set(update_fields) | {"code"}
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            ReferralEvent.objects.create(referral=self, status=self.status)

    def credit(self, points):
        if points <= 0:
            raise ValidationError("Los puntos deben ser mayores a cero.")
        with transaction.atomic():
            referral = Referral.objects.select_for_update().get(pk=self.pk)
            if referral.status != Referral.Status.PENDING:
                raise ValidationError("Este referido ya no está pendiente.")
            account = referral.referrer.points_account
            account.add_points(points, PointEntry.Source.REFERRAL, referral=referral)
            referral.status = Referral.Status.CREDITED
            referral.points_awarded = points
            referral.save(update_fields=["status", "points_awarded", "updated_at"])
            ReferralEvent.objects.create(referral=referral, status=Referral.Status.CREDITED)
        self.status = Referral.Status.CREDITED
        self.points_awarded = points

    @classmethod
    def refer(cls, referrer, referred, points):
        if referrer.pk == referred.pk:
            raise ValidationError("No puedes referirte a ti mismo.")
        try:
            account = referrer.points_account
        except PointsAccount.DoesNotExist:
            raise ValidationError("Los referidos se habilitan después de la primera compra.") from None
        if not account.enabled:
            raise ValidationError("Los referidos se habilitan después de la primera compra.")
        try:
            with transaction.atomic():
                referral = cls.objects.create(
                    referrer=referrer,
                    referred=referred,
                    code=account.referral_code,
                    status=cls.Status.PENDING,
                )
                referral.credit(points)
        except IntegrityError as exc:
            raise ValidationError("Este usuario ya fue referido.") from exc
        return referral


class ReferralEvent(models.Model):
    """Fecha en la que un referido cambió de estado."""

    referral = models.ForeignKey(Referral, related_name="events", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Referral.Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Estado del referido"
        verbose_name_plural = "Estados del referido"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_status_display()} · {self.created_at}"