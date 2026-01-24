from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

# def validate_phone_length(value):
#     if len(value) != 4:
#         raise ValidationError('Phone number must be exactly 4 characters long.')

# ...existing code...


# Create your models here.
class building_record(models.Model):

    BRGY_CHOICES = (
        ('1','1 (HEN. M. ALVAREZ)'),
        ('2','2 (C. TIRONA)'),
        ('3','3 (HEN. E. AGUINALDO)'),
        ('4','4 (HEN. M. TRIAS)'),
        ('5','5 (HEN. E. EVANGELISTA)'),
        ('6','6 (DIEGO SILANG)'),
        ('7','7 (KAPITAN KONG)'),
        ('8','8 (MANUEL S. ROJAS)'),
        ('9','9 (KANAWAY)'),
        ('10','10 (KINGFISHER)'),
        ('10A','10-A (KINGFISHER-A)'),
        ('10B','10-B (KINGFISHER-B)'),
        ('11','11 (LAWIN)'),
        ('12','12 (LOVE BIRD)'),
        ('13','13 (AGUILA)'),
        ('14','14 (LORO)'),
        ('15','15 (KILYAWAN)'),
        ('16','16 (MARTINES)'),
        ('17','17 (KALAPATI)'),
        ('18','18 (MAYA)'),
        ('19','19 (GEMINI)'),
        ('20','20 (VIRGO)'),
        ('21','21 (SCORPIO)'),
        ('22','22 (LEO)'),
        ('22A','22-A (LEO A)'),
        ('23','23 (AQUARIUS)'),
        ('24','24 (LIBRA)'),
        ('25','25 (CAPRICORN)'),
        ('26','26 (CANCER)'),
        ('27','27 (SAGITARIUS)'),
        ('28','28 (TAURUS)'),
        ('29','29 (LAO-LAO)'),
        ('29A','29-A (LAO-LAO A)'),
        ('30','30 (BID-BID)'),
        ('31','31 (MAYA-MAYA)'),
        ('32','32 (SALAY-SALAY)'),
        ('33','33 (BUWAN-BUWAN)'),
        ('34','34 (LAPU-LAPU)'),
        ('35','35 (HASA-HASA)'),
        ('36','36 (SAP-SAP)'),
        ('36A','36-A (SAP-SAP A)'),
        ('37','37 (CADENA DE AMOR)'),
        ('37A','37-A (CADENA DE AMOR A)'),
        ('38','38 (SAMPAGUITA)'),
        ('38A','38-A (SAMPAGUITA A)'),
        ('39','39 (JASMIN)'),
        ('40','40 (GUMAMELA)'),
        ('41','41 (ROSAL)'),
        ('42','42 (PINAGBUKLOD)'),
        ('42A','42-A (PINAGBUKLOD A)'),
        ('42B','42-B (PINAGBUKLOD B)'),
        ('42C','42-C (PINAGBUKLOD C)'),
        ('43','43 (PINAGPALA)'),
        ('44','44 (MALIGAYA)'),
        ('45','45 (KAUNLARAN)'),
        ('45A','45-A (KAUNLARAN A)'),
        ('46','46 (SINAGTALA)'),
        ('47','47 (PAGKAKAISA)'),
        ('47A','47-A (PAGKAKAISA A)'),
        ('47B','47-B (PAGKAKAISA B)'),
        ('48','48 (NARRA)'),
        ('48A','48-A (NARRA A)'),
        ('49','49 (AKASYA)'),
        ('49A','49-A (AKASYA A)'),
        ('50','50 (KABALYERO)'),
        ('51','51 (KAMAGONG)'),
        ('52','52 (IPIL)'),
        ('53','53 (YAKAL)'),
        ('53A','53-A (YAKAL A)'),
        ('53B','53-B (YAKAL B)'),
        ('54','54 (PECHAY)'),
        ('54A','54-A (PECHAY A)'),
        ('55','55 (AMPALAYA)'),
        ('56','56 (LABANOS)'),
        ('57','57 (REPOLYO)'),
        ('58','58 (PATOLA)'),
        ('58A','58-A (PATOLA A)'),
        ('59','59 (SITAW)'),
        ('60','60 (LETSUGAS)'),
        ('61','61 (TALONG)'),
        ('61A','61-A (TALONG A)'),
        ('062','62 (KANGKONG)'),
        ('62A','62-A (KANGKONG A)'),
        ('62B','62-B (KANGKONG B)')
    )

    DISTRICT = (
        ('1', '(1) DALAHICAN/STA. CRUZ'), # first element in tuple will be saved in database, 2nd is in form for user to view
        ('2', '(2) CARIDAD'),
        ('3', '(3) SAN ANTONIO'),
        ('4', '(4) SAN ROQUE')
    )

    STATUS = (
        ('COMPLIED', 'COMPLIED'), # first element in tuple will be saved in database, 2nd is in form for user to view
        ('LOT OWNER CONSENT', 'LOT OWNER CONSENT'),
        ('NONCOMPLIANT', 'NONCOMPLIANT'),
        ('PROCESSING', 'PROCESSING'),
        ('REASSESSMENT', 'REASSESSMENT')

    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='building_records', null=True, blank=True)
    cavite_pin = models.CharField(max_length=3, blank=False, null=False, default=127)
    district_pin = models.CharField(max_length=2, choices=DISTRICT)
    brgy_pin = models.CharField(max_length=4, choices=BRGY_CHOICES)
    section_pin = models.CharField(max_length=3, blank=False, null=False)
    lot_pin = models.CharField(max_length=2, blank=False, null=False)
    building_pin = models.CharField(max_length=4, blank=True, null=True)
    pin_number = models.CharField(max_length=23, blank=True, null=True)

    lot_owner = models.CharField(max_length=350, blank=True, null=True)
    building_owner = models.CharField(max_length=350, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    contact_number = models.CharField(max_length=11, blank=True, null=True)
    occupancy_permit = models.CharField(max_length=25, blank=True, null=True)
    electrical_permit = models.CharField(max_length=25, blank=True, null=True)

    first_notice_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True, choices=STATUS)
    comment =   models.CharField(max_length=50, blank=True, null=True)

    second_notice_date = models.DateField(null=True, blank=True)
    second_status = models.CharField(null=True,max_length=50, blank=True, choices=STATUS)
    second_comment =   models.CharField(max_length=50, blank=True, null=True)

    third_notice_date = models.DateField(null=True, blank=True)
    third_status = models.CharField(null=True,max_length=50, blank=True, choices=STATUS)
    third_comment =   models.CharField(max_length=50, blank=True, null=True)

    for_legal_notice_date = models.DateField(null=True, blank=True)
    for_legal_status = models.CharField(null=True,max_length=50, blank=True, choices=STATUS)
    for_legal_comment =   models.CharField(max_length=50, blank=True, null=True)

    final_status = models.CharField(max_length=23, blank=True, null=True)
    # PRINT HISTORY
    first_notice_print_history = models.CharField(max_length=50, blank=True, null=True)
    second_notice_print_history = models.CharField(max_length=50, blank=True, null=True)
    second_notice_print_date = models.DateField(null=True, blank=True)
    third_notice_print_history = models.CharField(max_length=50, blank=True, null=True)
    third_notice_print_date = models.DateField(null=True, blank=True)
    for_legal_notice_print_history = models.CharField(max_length=50, blank=True, null=True)
    for_legal_notice_print_date = models.DateField(null=True, blank=True)

    date_complied =  models.DateField(null=True, blank=True)
    date_final_status = models.DateField(null=True, blank=True)
    history = HistoricalRecords() 

    def __str__(self):
        return(f'{self.lot_owner} {self.building_owner} {self.pin_number}')

class holidays(models.Model):
    holiday = models.DateField(null=True, blank=True)

    def __str__(self):
        return(f'{self.holiday}')

class Signatories(models.Model):
    signatory = models.CharField(max_length=50, blank=True)
    position = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return(f'{self.signatory}')

class ActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)