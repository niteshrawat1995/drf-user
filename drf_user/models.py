from django.db import models

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group

from django.utils.text import gettext_lazy as _

from drfaddons import datatypes as cmodels


class Role(Group):
    """
    A proxy model for Group for renaming Group to Role.
    """
    class Meta:
        proxy = True
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')


class User(AbstractBaseUser, PermissionsMixin):
    """
    A Custom USER Model. This model has ad-on properties in compare to original DJango User Mobile. This has been
    done considering the need of relevant data in Indian scenario.
    """
    from .managers import UserManager

    username = models.CharField(_('Unique UserName'), max_length=254,  unique=True)
    email = models.EmailField(_('EMail Address'), unique=True)
    mobile = models.CharField(_('Mobile Number'), max_length=150, unique=True)
    name = models.CharField(_('Full Name'), max_length=500, blank=False)
    date_joined = cmodels.UnixTimestampField(_('Date Joined'), auto_now_add=True)
    update_date = cmodels.UnixTimestampField(_('Date Modified'), auto_created=True)
    is_active = models.BooleanField(_('Activated'), default=False)
    is_staff = models.BooleanField(_('Staff Status'), default=False)
    is_whatsapp = models.BooleanField(_('Is mobile WhatsApp enabled?'), default=False)

    groups = models.ManyToManyField(
        Role,
        verbose_name=_('Roles'),
        blank=True,
        help_text=_(
            'The roles this user belongs to. A user will get all permissions '
            'granted to each of their roles.'
        ),
        related_name="user_set",
        related_query_name="user",
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'mobile', 'email']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return str(self.name) + ' | ' + str(self.username)


class AuthTransaction(models.Model):
    """
    This Model keeps the record of all authentication that is taking place. It's not required for authentication
    verification. Just a record keeping model.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField(blank=False, null=False)
    date_created = cmodels.UnixTimestampField(_('Created On'), auto_created=True)
    token = models.TextField(_('JWT Token passed'))
    session = models.TextField(_('Session Passed'))
    is_active = models.BooleanField(_('Is Active?'), default=True)

    def __str__(self):
        return str(self.user.name) + ' | ' + str(self.user.username)

    class Meta:
        verbose_name = _('Authentication Transaction')
        verbose_name_plural = _('Authentication Transactions')


class OTPValidation(models.Model):
    """
    This model keeps a record of OTP Validation and which destinations have been successfully validated.
    """
    DESTINATION_CHOICES = [
        ('E', 'EMail Address'),
        ('M', 'Mobile Number')
    ]

    otp = models.CharField(_('OTP Code'), max_length=10, unique=True)
    destination = models.CharField(_('Destination Address (Mobile/EMail)'), max_length=254, unique=True)
    create_date = models.DateTimeField(_('Create Date'), auto_now_add=True)
    update_date = models.DateTimeField(_('Date Modified'), auto_now=True)
    is_validated = models.BooleanField(_('Is Validated'), default=False)
    validate_attempt = models.IntegerField(_('Attempted Validation'), default=3)
    prop = models.CharField(_('Destination Property'), default='E', max_length=3, choices=DESTINATION_CHOICES)
    send_counter = models.IntegerField(_('OTP Sent Counter'), default=0)
    sms_id = models.CharField(_('SMS ID'), max_length=254, null=True, blank=True)
    reactive_at = cmodels.UnixTimestampField(_('ReActivate Sending OTP'))

    def __str__(self):
        return self.destination

    class Meta:
        verbose_name = _('OTP Validation')
        verbose_name_plural = _('OTP Validations')
