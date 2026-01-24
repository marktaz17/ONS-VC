from django import forms
from .models import building_record,holidays,Signatories
from datetime import date
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.functions import ExtractYear

class NumericField(forms.CharField):
    def clean(self, value):
        super().clean(value)
        if value in (None, ''):
            return None  # Allow None or empty string

        try:
            # Try converting the value to float
            float_value = float(value)
            return float_value  # Return the float value
        except ValueError:
            raise ValidationError("Please enter a valid number.")  # Custom

class IntegerField(forms.CharField):
    def clean(self, value):
        super().clean(value)
        if value in (None, ''):
            return None  # Allow None or empty string

        try:
            # Try converting the value to an integer
            int_value = int(value)
            return int_value  # Return the integer value
        except ValueError:
            raise ValidationError("Please enter a valid number.")

class Add_Records(forms.ModelForm):

    numeric_validator_section = RegexValidator(
        r'^\d{1}$',  # Regex pattern to match exactly 1 digit
        'Only numeric values are allowed (exactly 1 digit).'
    )
    numeric_validator_lot = RegexValidator(
        r'^\d{1,2}$',  # Regex pattern to match exactly 1 or 3 digits
        'Only numeric values are allowed.'
    )
    numeric_validator_building = RegexValidator(
        r'^\d{1,2}$',  # Regex pattern to match 1 or 2 digits
        'Only numeric values are allowed (1 or 2 digits).'
    )

    created_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],  # Adjust as needed
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance and instance.created_at:
                # Convert to local timezone for display
                self.fields['created_at'].initial = instance.created_at.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%dT%H:%M')

    cavite_pin = forms.CharField(
        required=True,
        initial=127,
        widget=forms.TextInput(attrs={"placeholder": "Cavite City Pin", "class": "form-control"}),
        label=""
    )

    brgy_pin = forms.ChoiceField(
        required=True,
        choices=[('', '-Select Brgy-')] + list(building_record.BRGY_CHOICES),
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )

    district_pin = forms.ChoiceField(
        required=True,
        choices=[('', '-Select District-')] + list(building_record.DISTRICT),
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )

    section_pin = forms.CharField(
        max_length=1,
        min_length=1,
        validators=[numeric_validator_section],  # Add the numeric validator
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Add your CSS class here
            'maxlength': '3',  # Ensure the max length is enforced in the HTML
            # 'placeholder': '3 digits',  # Optional placeholder
        })
    )

    lot_pin = forms.CharField(
        max_length=2,
        min_length=1,
        validators=[numeric_validator_lot],  # Add the numeric validator
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Add your CSS class here
            'maxlength': '2',  # Ensure the max length is enforced in the HTML
            # 'placeholder': '2 digits',  # Optional placeholder
        })
    )

    building_pin = forms.CharField(
        required=True,
        max_length=2,
        min_length=1,
        validators=[numeric_validator_building],  # Add the numeric validator
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Add your CSS class here
            'maxlength': '4',  # Ensure the max length is enforced in the HTML
            # 'placeholder': '4 digits',  # Optional placeholder
        })
    )

    pin_number = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )

    lot_owner = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={
        "class": "form-control",
        "oninput": "this.value = this.value.toUpperCase();"  # This will convert input to uppercase
    }),
    label=""
    )

    building_owner = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control",
        "oninput": "this.value = this.value.toUpperCase();"
        }),
        label=""
    )

    address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control",
        "oninput": "this.value = this.value.toUpperCase();"
        }),
        label=""
    )

    contact_number = IntegerField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=""
    )

    occupancy_permit = NumericField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=""
    )

    electrical_permit = NumericField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=""
    )

    comment =   forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control",
        "oninput": "this.value = this.value.toUpperCase();"
        }),
        label=""
    )

    second_comment =   forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control",
        "oninput": "this.value = this.value.toUpperCase();"
        }),
        label=""
    )

    third_comment =   forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control",
        "oninput": "this.value = this.value.toUpperCase();"
        }),
        label=""
    )

    for_legal_comment =   forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control",
        "oninput": "this.value = this.value.toUpperCase();"
        }),
        label=""
    )

    status = forms.ChoiceField(
        required=True,
        # initial='NONCOMPLIANT',
        choices=[('', '-Select Status-')] + list(building_record.STATUS),
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )

    second_status = forms.ChoiceField(
        required=False,
        # initial='NONCOMPLIANT',
        choices=[('', '-Select Status-')] + list(building_record.STATUS),
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )

    third_status = forms.ChoiceField(
        required=False,
        # initial='NONCOMPLIANT',
        choices=[('', '-Select Status-')] + list(building_record.STATUS),
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )

    for_legal_status = forms.ChoiceField(
        required=False,
        # initial='NONCOMPLIANT',
        choices=[('', '-Select Status-')] + list(building_record.STATUS),
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )

    first_notice_date = forms.DateField(
        required=True,
        # initial=date.today,  # Set the default value to today's date
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label=""
    )

    second_notice_date = forms.DateField(
        required=False,
        # initial=date.today,  # Set the default value to today's date
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date", "readonly": "readonly"}),
        label=""
    )

    third_notice_date = forms.DateField(
        required=False,
        # initial=date.today,  # Set the default value to today's date
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date", "readonly": "readonly"}),
        label=""
    )

    for_legal_notice_date = forms.DateField(
        required=False,
        # initial=date.today,  # Set the default value to today's date
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date", "readonly": "readonly"}),
        label=""
    )

    final_status = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )
    
    first_notice_print_history = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )
    first_notice_print_date = forms.DateField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )
    second_notice_print_history = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )
    second_notice_print_date = forms.DateField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )
    third_notice_print_history = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )
    third_notice_print_date = forms.DateField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )
    for_legal_notice_print_history = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )
    for_legal_notice_print_date = forms.DateField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )
    date_complied = forms.DateField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )
    date_final_status = forms.DateField(
    required=False,
    widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    label=""
    )


    class Meta: # Designate what model to use
        model = building_record
        exclude = ('user',) # exclude the user and include all the field in form serializer_
        # fields = ('last_name', 'first_name') sample include field

class Add_Holidays(forms.ModelForm):
    holiday = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label=""
    )

    class Meta: # Designate what model to use
        model = holidays
        exclude = ('user',) # exclude the user and include all the field in form serializer_
        # fields = ('last_name', 'first_name') sample include field

class Add_Signatories(forms.ModelForm):
    signatory = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control",
        "oninput": "this.value = this.value.toUpperCase();"
        }),
        label=""
    )
    position = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control",
        "oninput": "this.value = this.value.toUpperCase();"
        }),
        label=""
    )



    class Meta: # Designate what model to use
        model = Signatories
        exclude = ('user',) # exclude the user and include all the field in form serializer_
        # fields = ('last_name', 'first_name') sample include field

class Reprint_Notice(forms.Form):
    SELECT_NOTICE = (
        # ('FIRST NOTICE', 'FIRST NOTICE'), # first element in tuple will be saved in database, 2nd is in form for user to view
        ('SECOND NOTICE', 'SECOND NOTICE'),
        ('THIRD NOTICE', 'THIRD NOTICE'),
        ('FOR LEGAL', 'FOR LEGAL')
    )


    reprint_pin_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": " Enter PIN",
        "oninput": "this.value = this.value.toUpperCase();"
        }),
        label=""
    )

    reprint_notice = forms.ChoiceField(
        required=True,
        # initial='NONCOMPLIANT',
        choices=[('', '-Select Status-')] + list(SELECT_NOTICE),
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )
    notice_status = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": " Enter PIN",
        "oninput": "this.value = this.value.toUpperCase();"
        }),
        label=""
    )

class Report_Notice(forms.Form):
    BRGY_CHOICES = (
        ('ALL BARANGAYS','ALL BARANGAYS'),
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
    SELECT_STATUS = (
        ('COMPLIED', 'COMPLIED'), # first element in tuple will be saved in database, 2nd is in form for user to view
        ('LOT OWNER CONSENT', 'LOT OWNER CONSENT'),
        ('NONCOMPLIANT', 'NONCOMPLIANT'),
        ('PROCESSING', 'PROCESSING'),
        ('REASSESSMENT', 'REASSESSMENT'),
        ('ALL STATUS','RECORDS WITH STATUS'),
        ('NO STATUS','RECORDS WITHOUT STATUS'),

    )

    # report_pin_number = forms.CharField(
    #     required=False,
    #     widget=forms.TextInput(attrs={"class": "form-control", "placeholder": " Enter PIN",
    #     "oninput": "this.value = this.value.toUpperCase();"
    #     }),
    #     label=""
    # )

    report_notice_status = forms.ChoiceField(
        required=True,
        # initial='NONCOMPLIANT',
        choices=[('', '-Select Status-')] + list(SELECT_STATUS),
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )

    starting_date = forms.DateField(
        required=False,
        # initial=date.today,  # Set the default value to today's date
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label=""
    )

    ending_date = forms.DateField(
        required=False,
        # initial=date.today,  # Set the default value to today's date
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label=""
    )

    report_brgy = forms.ChoiceField(
        required=True,
        choices=[('', '-Select Brgy-')] + list(BRGY_CHOICES),
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )

class Daily_Encoded(forms.Form):
    select_user = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Select a User"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate the choices with all registered users and add "All Users" option
        user_choices = [(user.username, user.get_full_name() or user.username) for user in User.objects.all()]
        self.fields['select_user'].choices = [('', '-Select Encoder-'), ("All Encoders", "All Encoders")] + user_choices

    encoded_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label=""
    )

class Occupancy_Eletrical_Payment(forms.Form):
    BRGY_CHOICES = (
        ('ALL BARANGAYS','ALL BARANGAYS'),
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

    report_brgy = forms.ChoiceField(
        required=True,
        choices=[('', '-Select Brgy-')] + list(BRGY_CHOICES),
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )

    select_year = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get distinct years from date_complied in your model
        years = (
            building_record.objects
            .exclude(date_complied__isnull=True)
            .annotate(year=ExtractYear('date_complied'))
            .values_list('year', flat=True)
            .distinct()
            .order_by('year')
        )
        year_choices = [('', '-Select Year-')] + [(str(year), str(year)) for year in years if year]
        self.fields['select_year'].choices = year_choices

class dashboard_selected_year(forms.Form):
    select_year = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get distinct years from date_complied in your model
        years = (
            building_record.objects
            .exclude(date_final_status__isnull=True)
            .annotate(year=ExtractYear('date_final_status'))
            .values_list('year', flat=True)
            .distinct()
            .order_by('year')
        )
        year_choices = [('', '-Select Year-')] + [(str(year), str(year)) for year in years if year]
        self.fields['select_year'].choices = year_choices