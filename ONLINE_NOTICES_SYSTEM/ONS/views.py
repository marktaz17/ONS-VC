from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import building_record, holidays, Signatories, ActionLog
from .forms import Add_Records, Add_Holidays, Add_Signatories, Reprint_Notice, Report_Notice, Daily_Encoded, Occupancy_Eletrical_Payment, dashboard_selected_year
from django.utils.safestring import mark_safe
from django.urls import reverse
from datetime import datetime, timedelta, date, time
from django.utils import timezone
from django.db.models import Count, Q
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
import json
from django.http import HttpResponse
from django.urls import reverse
import re
from django.db.models.functions import TruncDate
import pytz
manila_tz = pytz.timezone('Asia/Manila')
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# import pdfkit
# config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

# Configure logging
logger = logging.getLogger(__name__)
# Create your views here.
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
def login_page(request):
    if request.method == 'POST':
        username = request.POST['userName']
        password = request.POST['passWord']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have Been Logged In!")
            return redirect('dashboard')
        else:
            messages.warning(request, "Invalid Username or Password!")
            return redirect('login_page')
    else:
        return render(request, 'login_page.html')

def home(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            draw = int(request.GET.get('draw', 0))
            start = int(request.GET.get('start', 0))
            length = int(request.GET.get('length', 10))
            search_value = request.GET.get('search[value]', '')

            records = building_record.objects.all()

           # Global search
            if search_value:
                records = records.filter(
                    Q(pin_number__icontains=search_value) |
                    Q(building_owner__icontains=search_value) |
                    Q(brgy_pin__icontains=search_value) |
                    Q(final_status__icontains=search_value)
                )

            # Column-specific search
            pin_number_search = request.GET.get('columns[1][search][value]', '')
            building_owner_search = request.GET.get('columns[2][search][value]', '')
            brgy_pin_search = request.GET.get('columns[3][search][value]', '')
            final_status_search = request.GET.get('columns[4][search][value]', '')

            # Apply column-specific search filters
            if pin_number_search:
                records = records.filter(pin_number__icontains=pin_number_search)
            if building_owner_search:
                records = records.filter(building_owner__icontains=building_owner_search)
            if brgy_pin_search:
                records = records.filter(brgy_pin__iexact=brgy_pin_search)
            if final_status_search:
                records = records.filter(final_status__icontains=final_status_search)

            # Sorting logic
            sorting_col_index0 = request.GET.get('order[0][column]', '1')
            sorting_direction = request.GET.get('order[0][dir]', 'asc')
            sorting_col_map = {
                '1': 'pin_number',
                '2': 'building_owner',
                '3': 'brgy_pin',
                '4': 'final_status',
                '5': 'created_at'  # Add created_at to the sorting options if necessary
            }
            sorting_col = sorting_col_map.get(sorting_col_index0, 'created_at')
            if sorting_direction == 'asc':
                sorting_col = '-' + sorting_col

            records = records.order_by(sorting_col)

            # Pagination
            total_records = building_record.objects.count()
            filtered_records = records.count()
            records = records[start:start + length]

            # Prepare data for the response
            data = []
            for item in records:
                # Format the created_at date to "Aug. 1, 2025, 10:02 a.m."
                if item.created_at:
                    formatted_date = item.created_at.strftime('%b. %d, %Y')
                else:
                    formatted_date = ""
                data.append({
                    'pin_number': item.pin_number,
                    'building_owner': item.building_owner,
                    'brgy_pin': item.brgy_pin,
                    'final_status': item.final_status,
                    'created_at': formatted_date,
                    'action': '<div style="display: flex; justify-content: center; gap: 10px;">'
                            f'<a href="{reverse("update", args=[item.id])}" class="btn btn-secondary" title="Edit">Edit'
                            '</a>'
                            f'<a href="{reverse("delete", args=[item.id])}" class="btn btn-danger" title="Delete">Delete'
                            '</a>'
                            '</div>'
                })

            response = {
                'draw': draw,
                'recordsTotal': total_records,
                'recordsFiltered': filtered_records,
                'data': data
            }
            return JsonResponse(response)

        return render(request, 'home.html')
    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')

def holiday_table(request):
    records = holidays.objects.all() # --add this--
    if request.user.is_authenticated:

        return render(request, 'holiday.html',{'records':records})
    else:
        messages.success(request, "You must be Logged In to view the page!")
        return redirect('login_page')

def signatory_table(request):
    records = Signatories.objects.all() # --add this--
    if request.user.is_authenticated:

        return render(request, 'signatory.html',{'records':records})
    else:
        messages.success(request, "You must be Logged In to view the page!")
        return redirect('login_page')

def user_logout(request):
    logout(request)
    # messages.success(request, "You have been Logged Out!")
    return redirect('login_page')

def delete_record(request, pk): # delete building record
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view the page.")
        return redirect('login_page')

    del_record = building_record.objects.get(id=pk)

    if not request.user.has_perm('ONLINE_NOTICES_SYSTEM.delete_building_record'):
        messages.warning(request, "You do not have permission to delete this record.")
        return redirect('home')
    try:
        del_record.delete()
        messages.success(request, "Record Deleted Successfully!")
    except Exception as e:
        messages.error(request, "An error occurred while deleting the record.")
        print(f"Error: {e}")  # Log the exception for debugging

    return redirect('home')

def delete_holiday(request, pk):
    if request.user.is_authenticated:
        try:
            # Get the holiday record to delete
            del_record = holidays.objects.get(id=pk)
            del_record.delete()
            messages.success(request, "Holiday Deleted Successfully!")

            # Fetch all building records that may need date recomputation
            building_records = building_record.objects.all()

            for record in building_records:
                # Check if "COMPLIED" is NOT in any relevant fields
                if 'COMPLIED' not in (record.status, record.second_status, record.third_status, record.for_legal_status):
                    # Ensure the first_notice_date exists before recalculating
                    if record.first_notice_date:
                        # Calculate the new second, third, and legal notice dates
                        second_notice_date = calculate_final_date(record.first_notice_date)
                        third_notice_date = calculate_final_date(second_notice_date)
                        for_legal_notice_date = calculate_final_date(third_notice_date)

                        # Update the record with new dates
                        record.second_notice_date = second_notice_date
                        record.third_notice_date = third_notice_date
                        record.for_legal_notice_date = for_legal_notice_date
                        record.save()

            return redirect('holiday_table')

        except holidays.DoesNotExist:
            messages.error(request, "Holiday not found.")
            return redirect('holiday_table')

    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')

def delete_signatory(request, pk): # delete building record
    if request.user.is_authenticated:
        del_record = Signatories.objects.get(id=pk)
        del_record.delete()
        messages.success(request, "Signatory Deleted Successfully!")
        return redirect('signatory_table')
    else:
        messages.success(request, "You must be Logged In to view the page!")
        return redirect('home')

def add_holiday(request):
    form = Add_Holidays(request.POST or None)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if form.is_valid():
                holiday = form.cleaned_data['holiday']
                records = holidays.objects.filter(holiday=holiday)
                if records.exists():
                    message = mark_safe(f'DUPLICATE HOLIDAY FOUND! {holiday}')
                    messages.warning(request, message)
                    return redirect('add_holiday')
                else:
                    # Save the new holiday
                    form.save()

                    # Fetch all building records that need date recomputation
                    building_records = building_record.objects.all()

                    for record in building_records:
                        # Check if "COMPLIED" is in any of the relevant fields
                        if 'COMPLIED' not in (record.status, record.second_status, record.third_status, record.for_legal_status):
                            # Ensure the first_notice_date exists
                            if record.first_notice_date:
                                # Calculate the new second, third, and legal notice dates
                                second_notice_date = calculate_final_date(record.first_notice_date)
                                third_notice_date = calculate_final_date(second_notice_date)
                                for_legal_notice_date = calculate_final_date(third_notice_date)

                                # Update the record with new dates
                                record.second_notice_date = second_notice_date
                                record.third_notice_date = third_notice_date
                                record.for_legal_notice_date = for_legal_notice_date
                                record.save()
                        else:
                            # Optionally log or handle records with "COMPLIED"
                            print(f'Skipping record {record.id} due to COMPLIED status.')

                    messages.success(request, 'Holiday Added Successfully!')
                    return redirect('holiday_table')
        else:
            return render(request, 'add_holiday.html', {'form': form, 'add_holiday_button': True})
    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('home')

def add_signatory(request):
    form = Add_Signatories(request.POST or None)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request, 'Signatory Added Successfully!')
                return redirect('signatory_table')
        else:
            return render(request, 'add_signatory.html',{'form': form, 'add_signatory_button': True})
    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')

def add_record(request):
    if request.user.is_authenticated:
        form = Add_Records(request.POST or None)  # Replace with your actual form class
        today = timezone.localtime(timezone.now()).date()
        if form.is_valid():
            # Extract cleaned data from the form
            cavite_pin = form.cleaned_data['cavite_pin']
            district = form.cleaned_data['district_pin']
            brgy = form.cleaned_data['brgy_pin']
            section = form.cleaned_data['section_pin']
            lot = form.cleaned_data['lot_pin']
            building = form.cleaned_data['building_pin']
            first_notice_date = form.cleaned_data['first_notice_date']  # Ensure this field exists in your form
            status = form.cleaned_data['status']
            date_complied = form.cleaned_data['date_complied']
            date_final_status = form.cleaned_data['date_final_status']

            add_district = f'0{district}'

            len_brgy = len(brgy)

            if len_brgy == 3:
                add_brgy = f'0{brgy}'
            elif len_brgy == 2:
                add_brgy = f'00{brgy}'
            else:
                add_brgy = f'000{brgy}'


            add_section = f'{int(section):03}'
            add_lot = f'{int(lot):02}'

            if building:
                add_building = f'10{int(building):02}'
            else:
                add_building = ''

            if add_building:
                pin_number = f'{cavite_pin}-{add_district}-{add_brgy}-{add_section}-{add_lot}-{add_building}'
            else:
                pin_number = f'{cavite_pin}-{add_district}-{add_brgy}-{add_section}-{add_lot}'

            # Create the pin number
            # pin_number = f'{cavite_pin}-{add_district}-{add_brgy}-{add_section}-{add_lot}-{add_building}'
            logger.info(f'Pin Number: {pin_number}')  # Use logging instead of print

            # Check for duplicate records
            records = building_record.objects.filter(pin_number=pin_number)
            if records.exists():
                duplicate_pin_url = reverse('update', args=[records.first().id])
                message = mark_safe(f'DUPLICATE PIN RECORD FOUND! <a href="{duplicate_pin_url}">{pin_number}</a>')
                messages.warning(request, message)
                return redirect('add')  # Redirect to the same page if duplicate found


            if form.cleaned_data['status'] in ["COMPLIED", "PROCESSING", "REASSESSMENT", "LOT OWNER CONSENT"]:
                initial_status = status
            else:
                initial_status = "NONCOMPLIANT"

            if form.cleaned_data['status'] == "COMPLIED":
                date_complied = today
            else:
                date_final_status = today
            # Create a new instance of the model
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.date_complied = date_complied
            instance.date_final_status = date_final_status
            instance.final_status = initial_status
            instance.pin_number = pin_number

            if status == 'NONCOMPLIANT':
                # Calculate the final dates
                if first_notice_date:
                    second_notice_date = calculate_final_date(first_notice_date)
                    third_notice_date = calculate_final_date(second_notice_date)
                    for_legal_notice_date = calculate_final_date(third_notice_date)

                    logger.info(f'Second Notice Date: {second_notice_date.strftime("%m/%d/%Y")}')
                    logger.info(f'Third Notice Date: {third_notice_date.strftime("%m/%d/%Y")}')
                    logger.info(f'For Legal Notice Date: {for_legal_notice_date.strftime("%m/%d/%Y")}')

                    # Set calculated dates
                    instance.second_notice_date = second_notice_date
                    instance.third_notice_date = third_notice_date
                    instance.for_legal_notice_date = for_legal_notice_date
                    instance.second_status = "NONCOMPLIANT"
                    instance.third_status = "NONCOMPLIANT"
                    instance.for_legal_status = "NONCOMPLIANT"

            # Save the instance
            try:
                instance.history_user = request.user
                instance.save()
                messages.success(request, 'Record Added Successfully!')
                return redirect('home')  # Redirect to home after success
            except Exception as e:
                logger.error(f'Error saving record: {e}')
                messages.error(request, 'An error occurred while saving the record.')

        else:
            # Handle form errors if the form is not valid
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f"{field}: {error}")

        # Render the form if the request method is GET or the form is not valid
        return render(request, 'add.html', {'form': form, 'add_button': True})

    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')

def add_working_days(start_date, num_days):
    """
    Add working days to a start date, excluding weekends and holidays.
    """
    holidays_list = []  # Initialize holidays as an empty list
    try:
        # Attempt to get the list of holidays from the database
        holidays_list = holidays.objects.values_list('holiday', flat=True)  # Get list of holidays
        holidays_list = [holiday for holiday in holidays_list]  # No need to convert to date objects
    except Exception as e:
        print(f"Error fetching holidays: {e}")  # Log any exceptions that occur

    current_date = start_date
    added_days = 0

    while added_days < num_days:
        current_date += timedelta(days=1)

        # Check if the current date is a weekend or a holiday
        if current_date.weekday() < 5 and current_date not in holidays_list:  # Monday to Friday are 0-4
            added_days += 1

    return current_date

def calculate_final_date(first_notice_date):
    """
    Calculate the final date by adding 4 working days and considering holidays.
    """
    # Ensure first_notice_date is a datetime object
    if isinstance(first_notice_date, str):
        try:
            first_notice_date = datetime.strptime(first_notice_date, "%m/%d/%Y")
        except ValueError:
            raise ValueError("Invalid date format. Please use MM/DD/YYYY.")

    # Add 4 working days
    final_date = add_working_days(first_notice_date, 4)

    return final_date

def update_record(request, pk):
    if request.user.is_authenticated:
        current_record = building_record.objects.get(id=pk)
        form = Add_Records(request.POST or None, instance=current_record)
        today = timezone.localtime(timezone.now()).date()
        if form.is_valid():
            if form.has_changed():
                
                cavite_pin = form.cleaned_data['cavite_pin']
                district = form.cleaned_data['district_pin']
                brgy = form.cleaned_data['brgy_pin']
                section = form.cleaned_data['section_pin']
                lot = form.cleaned_data['lot_pin']
                building = form.cleaned_data['building_pin']

                add_district = f'0{district}'

                len_brgy = len(brgy)

                if len_brgy == 3:
                    add_brgy = f'0{brgy}'
                elif len_brgy == 2:
                    add_brgy = f'00{brgy}'
                else:
                    add_brgy = f'000{brgy}'


                add_section = f'{int(section):03}'
                add_lot = f'{int(lot):02}'

                if building:
                    add_building = f'10{int(building):02}'
                else:
                    add_building = ''

                if add_building:
                    pin_number = f'{cavite_pin}-{add_district}-{add_brgy}-{add_section}-{add_lot}-{add_building}'
                else:
                    pin_number = f'{cavite_pin}-{add_district}-{add_brgy}-{add_section}-{add_lot}'

                form.cleaned_data['pin_number'] = pin_number
                status = form.cleaned_data['status']
                first_notice_date = form.cleaned_data['first_notice_date']
                second_status = form.cleaned_data['second_status']
                third_status = form.cleaned_data['third_status']
                for_legal_status = form.cleaned_data['for_legal_status']
                date_complied = form.cleaned_data['date_complied']
                date_final_status = form.cleaned_data['date_final_status']
                relevant_fields_changed = any(field in form.changed_data for field in ['status', 'second_status', 'third_status', 'for_legal_status'])
                if relevant_fields_changed:
                    date_final_status = today
                # print(f'Pin Number: {pin_number}')
                if 'district_pin' in form.changed_data or 'brgy_pin' in form.changed_data or 'section_pin' in form.changed_data or 'lot_pin' in form.changed_data or 'building_pin' in form.changed_data:
                    # Check for duplicate records
                    records = building_record.objects.filter(
                        cavite_pin=cavite_pin,
                        district_pin=district,
                        brgy_pin=brgy,
                        section_pin=section,
                        lot_pin=lot,
                        building_pin=building
                    )
                    if records.exists():
                        duplicate_pin_url = reverse('update', args=[records.first().id])
                        message = mark_safe(f'DUPLICATE PIN RECORD FOUND! <a href="{duplicate_pin_url}">{pin_number}</a>')
                        messages.warning(request, message)
                        return redirect('update', pk=pk)

                # Initialize notice dates
                second_notice_date = calculate_final_date(first_notice_date)
                third_notice_date = calculate_final_date(second_notice_date)
                for_legal_notice_date = calculate_final_date(third_notice_date)

                # Check statuses and set dates to None if conditions are met
                if form.cleaned_data['status'] in ["COMPLIED", "PROCESSING", "REASSESSMENT", "LOT OWNER CONSENT"]:
                    second_notice_date = None
                    third_notice_date = None
                    for_legal_notice_date = None
                    second_status = None
                    third_status = None
                    for_legal_status = None
                    final_status = status
                    # print(f'Status: {form.cleaned_data["status"]}')

                elif form.cleaned_data['second_status'] in ["COMPLIED", "PROCESSING", "REASSESSMENT", "LOT OWNER CONSENT"]:
                    third_notice_date = None
                    for_legal_notice_date = None
                    third_status = None
                    for_legal_status = None
                    final_status = second_status
                    # print(f'Second Status: {form.cleaned_data["second_status"]}')

                elif form.cleaned_data['third_status'] in ["COMPLIED", "PROCESSING", "REASSESSMENT", "LOT OWNER CONSENT"]:
                    for_legal_notice_date = None
                    for_legal_status = None
                    final_status = third_status
                    # print(f'Third Status: {form.cleaned_data["third_status"]}')

                elif form.cleaned_data['for_legal_status'] in ["COMPLIED", "PROCESSING", "REASSESSMENT", "LOT OWNER CONSENT"]:
                    for_legal_status = for_legal_status
                    final_status = for_legal_status
                    # print(f'Third Status: {form.cleaned_data["third_status"]}')

                else:
                    # Calculate notice dates if none of the statuses are as specified
                    second_notice_date = calculate_final_date(first_notice_date)
                    third_notice_date = calculate_final_date(second_notice_date)
                    for_legal_notice_date = calculate_final_date(third_notice_date)
                    second_status = "NONCOMPLIANT"
                    third_status = "NONCOMPLIANT"
                    for_legal_status = "NONCOMPLIANT"
                    final_status = status
                    # print(f'Second Notice Date: {second_notice_date.strftime("%m/%d/%Y")}')
                    # print(f'Third Notice Date: {third_notice_date.strftime("%m/%d/%Y")}')
                    # print(f'For Legal Notice Date: {for_legal_notice_date.strftime("%m/%d/%Y")}')
                # Get today's date with timezone

                match[status, second_status, third_status, for_legal_status]:
                    case ("COMPLIED", _, _, _):
                        date_complied = today
                        
                        print("First Notice Complied")
                    case ("NONCOMPLIANT", "COMPLIED", _, _):
                        date_complied = today
                        
                        print("Second Notice Complied")
                    case ("NONCOMPLIANT", "NONCOMPLIANT", "COMPLIED", _):
                        date_complied = today
                        
                        print("Third Notice Complied")
                    case ("NONCOMPLIANT", "NONCOMPLIANT", "NONCOMPLIANT", "COMPLIED"):
                        date_complied = today
                        
                        print("For Legal Notice Complied")
                    case _:
                        date_complied = None
                        
                        print("Unknown Status")

                # Save the instance
                instance = form.save(commit=False)
                instance.date_final_status = date_final_status
                instance.date_complied = date_complied
                instance.pin_number = pin_number
                instance.second_notice_date = second_notice_date
                instance.third_notice_date = third_notice_date
                instance.for_legal_notice_date = for_legal_notice_date
                instance.second_status = second_status
                instance.third_status = third_status
                instance.for_legal_status = for_legal_status
                instance.final_status = final_status
                instance.history_user = request.user
                instance.save()
                messages.success(request, 'Record updated successfully!')
                return redirect('update', pk=pk)

            else:  # If no changes were made
                messages.info(request, "The record remains unchanged.")
                return redirect('update', pk=pk)
        else:
            # Handle form errors if the form is not valid
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f"{field}: {error}")
        return render(request, 'update.html', {'form': form, 'edit_button': True, 'today': today})

    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')

def notice(request):
    print_button = True  # Initialize print_button to True
    if request.user.is_authenticated:  # Get today's date in the correct timezone
        today = timezone.localtime(timezone.now()).date()
        print('Today:', today)
        if request.method == 'POST':
            if 'successful_print' in request.POST:
                # Filter notices based on the conditions
                notices = building_record.objects.filter(
                    (Q(second_status="NONCOMPLIANT") & Q(second_notice_date=today) & Q(second_notice_print_history="")) |
                    (Q(third_status="NONCOMPLIANT") & Q(third_notice_date=today) & Q(third_notice_print_history="")) |
                    (Q(for_legal_status="NONCOMPLIANT") & Q(for_legal_notice_date=today) & Q(for_legal_notice_print_history=""))
                )

                if notices.exists():  # Check if the queryset is not empty
                    for notice in notices:
                        # Update the print history based on the type of notice
                        if notice.second_notice_date == today and notice.second_notice_print_history == "":
                            notice.second_notice_print_history = "PRINTED"
                            notice.second_notice_print_date = today
                            notice.save(update_fields=['second_notice_print_history', 'second_notice_print_date'])  # Save only these fields
                        elif notice.third_notice_date == today and notice.third_notice_print_history == "":
                            notice.third_notice_print_history = "PRINTED"
                            notice.third_notice_print_date = today
                            notice.save(update_fields=['third_notice_print_history', 'third_notice_print_date'])  # Save only these fields
                        elif notice.for_legal_notice_date == today and notice.for_legal_notice_print_history == "":
                            notice.for_legal_notice_print_history = "PRINTED"
                            notice.for_legal_notice_print_date = today
                            notice.save(update_fields=['for_legal_notice_print_history', 'for_legal_notice_print_date'])  # Save only these fields
                        else:
                            print('Unknown Notice')

                    print('Successful Print')
                    messages.success(request, 'Notices have been successfully printed.')

                else:
                    print('No notices found to print.')
                    messages.warning(request, 'No notices found to print.')

            if 'unsuccessful_print' in request.POST:
                print('Unsuccessful Print')
                messages.warning(request, 'Print was unsuccessful.')

        notices = building_record.objects.filter(
            (Q(second_status="NONCOMPLIANT") & Q(second_notice_date=today) & Q(second_notice_print_history="")) |
            (Q(third_status="NONCOMPLIANT") & Q(third_notice_date=today) & Q(third_notice_print_history="")) |
            (Q(for_legal_status="NONCOMPLIANT") & Q(for_legal_notice_date=today) & Q(for_legal_notice_print_history=""))
        )
        no_of_notice = 0
        # Print the building_pin, dates, and notice type for each notice found
        if notices.exists():  # Check if the queryset is not empty
            for notice in notices:
                # Determine the type of notice and get the corresponding date
                if notice.second_notice_date == today:
                    notice_type = "Second Notice"
                    notice_date = notice.second_notice_date
                    no_of_notice += 1
                elif notice.third_notice_date == today:
                    notice_type = "Third Notice"
                    notice_date = notice.third_notice_date
                    no_of_notice += 1
                elif notice.for_legal_notice_date == today:
                    notice_type = "For Legal Notice"
                    notice_date = notice.for_legal_notice_date
                    no_of_notice += 1
                else:
                    notice_type = "Unknown Notice"
                    notice_date = None
        else:
            print_button = False  # Set to False if no notices are found
                # Print the details
                # print(f"Building PIN: {notice.pin_number}|{notice_date}|{notice_type}")
        # print(f'no_of_notice: {no_of_notice}')
        # Pass today's date to the template context
        context = {
            'notices': notices,
            'today': today,
            'no_of_notice': no_of_notice,
            'print_button': print_button,  # Pass the print_button variable to the context
        }
        return render(request, 'notice.html', context)

    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')

def print_notice(request, pk):

    today = timezone.localtime(timezone.now()).date()
    if request.user.is_authenticated:
        record = building_record.objects.get(id=pk)
        signatory = Signatories.objects.all()

        return render(request, 'print_notice.html', {'record': record, 'today': today, 'signatory': signatory})
    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')

def print_all_notice(request):

    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view the page.")
        return redirect('login_page')

    # Get today's date
    today = timezone.localtime(timezone.now()).date()
    signatory = Signatories.objects.all()
    # Retrieve all relevant notices
    records = building_record.objects.filter(
            (Q(second_status="NONCOMPLIANT") & Q(second_notice_date=today) & Q(second_notice_print_history="")) |
            (Q(third_status="NONCOMPLIANT") & Q(third_notice_date=today) & Q(third_notice_print_history="")) |
            (Q(for_legal_status="NONCOMPLIANT") & Q(for_legal_notice_date=today) & Q(for_legal_notice_print_history=""))
        )

    # Prepare a list for notices and a counter for 2nd and 3rd notices
    notice_records = []
    notice_counter = 0

    for record in records:
        if (record.second_status == "NONCOMPLIANT" and record.second_notice_date == today) or \
           (record.third_status == "NONCOMPLIANT" and record.third_notice_date == today):
            notice_records.append(record)
            notice_counter += 1  # Increment the counter
    # Prepare a list for notices and a counter for legal
    notice_legal_records = []
    notice_legal_counter = 0

    for record_legal in records:
        if (record_legal.for_legal_status == "NONCOMPLIANT" and record_legal.for_legal_notice_date == today):
            notice_legal_records.append(record_legal)
            notice_legal_counter += 1  # Increment the counter

    context = {
        'signatory': signatory,
        'notice_records': notice_records,  # Pass only the relevant records
        'notice_counter': notice_counter,
        'notice_legal_records': notice_legal_records,  # Pass only the relevant records
        'notice_legal_counter': notice_legal_counter,  # Pass the counter if needed
        'today': today,
    }

    return render(request, 'print_all_notice.html', context)

def update_signatory(request, pk):
    if request.user.is_authenticated:
        updated_signatory = Signatories.objects.get(id=pk)
        form = Add_Signatories(request.POST or None, instance=updated_signatory)
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, 'Record Updated!')
                return redirect('update_signatory', pk=pk)
            else: # If no changes were made
                    messages.info(request, "The record remain unchanged.")
                    return redirect('update_signatory', pk=pk)
        return render(request, 'update_signatory.html',{'form':form, 'edit_signatory_button': True})
    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')

# def download_all_pdf(request):

#     # Get today's date
#     today = timezone.now().date()
#     signatory = Signatories.objects.all()

#     # Retrieve all relevant notices
#     records = building_record.objects.filter(
#         second_status="NONCOMPLIANT",
#         second_notice_date=today
#     ) | building_record.objects.filter(
#         third_status="NONCOMPLIANT",
#         third_notice_date=today
#     ) | building_record.objects.filter(
#         for_legal_status="NONCOMPLIANT",
#         for_legal_notice_date=today
#     )

#     # Prepare a list for notices and a counter for 2nd and 3rd notices
#     notice_records = []
#     notice_counter = 0

#     for record in records:
#         if (record.second_status == "NONCOMPLIANT" and record.second_notice_date == today) or \
#         (record.third_status == "NONCOMPLIANT" and record.third_notice_date == today):
#             notice_records.append(record)
#             notice_counter += 1  # Increment the counter

#     # Prepare a list for notices and a counter for legal
#     notice_legal_records = []
#     notice_legal_counter = 0

#     for record_legal in records:
#         if (record_legal.for_legal_status == "NONCOMPLIANT" and record_legal.for_legal_notice_date == today):
#             notice_legal_records.append(record_legal)
#             notice_legal_counter += 1  # Increment the counter
# ## Prepare the context for rendering
#     context = {
#         'signatory': signatory,
#         'notice_records': notice_records,  # Pass only the relevant records
#         'notice_counter': notice_counter,
#         'notice_legal_records': notice_legal_records,  # Pass only the relevant records
#         'notice_legal_counter': notice_legal_counter,  # Pass the counter if needed
#         'today': today,
#     }

#     return render(request, 'download_all_pdf.html', context)

def modal_open(request):
    if request.method == 'POST' and 'modal_open' in request.POST:
        print('modal on')
        context = {
            'modal_on': True,  # Trigger the modal
        }
        return render(request, 'notice.html', context)
    else:
        return redirect('notice')  # Redirect if not a POST request

# def generatepdf(request):
#     today = timezone.now().date()
#     formatted_date = today.strftime('%m-%d-%Y')

#     # Options for PDF generation
#     options = {
#         'page-size': 'Legal',  # Use a predefined page size
#         'margin-bottom': '0in',
#         'margin-top': '0in',
#         'margin-right': '0in',
#         'margin-bottom': '0in',
#         'margin-left': '0in',
#         'encoding': "UTF-8",

#         'no-outline': None

#     }

    # Generate PDF from the specified URL
    # pdf = pdfkit.from_url(request.build_absolute_uri(reverse('download_all_pdf')), False, options=options, configuration=config)

    # Create a response with the generated PDF
    # response = HttpResponse(pdf, content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="{formatted_date}.pdf"'
    # return response
@login_required
def dashboard(request):
    # Use Q objects to filter and annotate counts in one query
    today = timezone.localtime(timezone.now()).date()
    date_to_filter = 7
    audit_trail_record = building_record.history.filter(history_date__gte=timezone.now()-timedelta(days=date_to_filter)).order_by('-history_date')
    form = dashboard_selected_year(request.POST or None)
    auth_user = User.objects.all()
    for auth_user in auth_user:
        print(auth_user.id , auth_user.username)
    reset_button = False
    filter_button = True
    if request.method == 'GET':
        # Reset the session variable to None when accessing the dashboard
        request.session['select_year'] = None
    if request.method == 'POST':
        if 'filter_button' in request.POST:
            if form.is_valid():
                select_year = form.cleaned_data['select_year']
                request.session['select_year'] = select_year
                audit_trail_record = building_record.history.filter(history_date__year=select_year)
                status_counts = building_record.objects.filter(
                    Q(date_final_status__year=select_year) & Q(
                        final_status__in=[
                            "COMPLIED",
                            "LOT OWNER CONSENT",
                            "NONCOMPLIANT",
                            "PROCESSING",
                            "REASSESSMENT",
                            ""
                        ]
                    )
                ).values('final_status').annotate(count=Count('final_status'))

                # Initialize counts for each final_status
                complied_count = 0
                lot_owner_consent_count = 0
                noncompliant_count = 0
                processing_count = 0
                reassessment_count = 0
                no_entry_count = 0

                # Populate the counts based on the results
                for item in status_counts:
                    if item['final_status'] == "COMPLIED":
                        complied_count = item['count']
                    elif item['final_status'] == "LOT OWNER CONSENT":
                        lot_owner_consent_count = item['count']
                    elif item['final_status'] == "NONCOMPLIANT":
                        noncompliant_count = item['count']
                    elif item['final_status'] == "PROCESSING":
                        processing_count = item['count']
                    elif item['final_status'] == "REASSESSMENT":
                        reassessment_count = item['count']
                    elif item['final_status'] == "":
                        no_entry_count = item['count']
                
                total_count = (complied_count +
                            lot_owner_consent_count +
                            noncompliant_count +
                            processing_count +
                            reassessment_count +
                            no_entry_count)
                # Prepare the context with separate counts
                formatted_complied_count = "{:,}".format(complied_count)
                formatted_lot_owner_consent_count = "{:,}".format(lot_owner_consent_count)
                formatted_noncompliant_count = "{:,}".format(noncompliant_count)
                formatted_processing_count = "{:,}".format(processing_count)
                formatted_reassessment_count = "{:,}".format(reassessment_count)
                formatted_no_entry_count = "{:,}".format(no_entry_count)
                formatted_total_count = "{:,}".format(total_count)

                # FOR TABLE
                statuses = ['COMPLIED', 'NONCOMPLIANT', 'REASSESSMENT', 'PROCESSING', 'LOT OWNER CONSENT', '']

                results = []

                # Loop through each barangay choice
                for brgy_code, brgy_name in BRGY_CHOICES:
                    permits = building_record.objects.filter(brgy_pin=brgy_code, final_status__in=statuses, date_final_status__year=select_year)
                    total_permits = permits.count()
                
                     # Check if there are any permits with a valid date_final_status
                    if permits.exists():  # Only proceed if there are permits
                        total_permits = permits.count()

                        # Initialize sums for occupancy and electrical permits
                        total_occupancy_permits = 0
                        total_electrical_permits = 0

                        # Sum the values of occupancy_permit and electrical_permit for 'Complied' status
                        for permit in permits.filter(final_status='COMPLIED'):
                            if permit.occupancy_permit:
                                total_occupancy_permits += float(permit.occupancy_permit)  # Convert to float if stored as a string
                            if permit.electrical_permit:
                                total_electrical_permits += float(permit.electrical_permit)  # Convert to float if stored as a string

                        total_occupancy_permits = "{:,.2f}".format(total_occupancy_permits)
                        total_electrical_permits = "{:,.2f}".format(total_electrical_permits)

                        brgy_counts = {
                            'barangay': brgy_name,
                            'Complied': "{:.2f}".format((permits.filter(final_status='COMPLIED').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
                            'Noncompliant': "{:.2f}".format((permits.filter(final_status='NONCOMPLIANT').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
                            'Reassessment': "{:.2f}".format((permits.filter(final_status='REASSESSMENT').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
                            'Processing': "{:.2f}".format((permits.filter(final_status='PROCESSING').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
                            'LotOwnerConsent': "{:.2f}".format((permits.filter(final_status='LOT OWNER CONSENT').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
                            'NoTagging': "{:.2f}".format((permits.filter(final_status='').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
                            'total_occupancy_permits': total_occupancy_permits,  # Add occupancy permits count
                            'total_electrical_permits': total_electrical_permits,
                        }

                        results.append(brgy_counts)

                # TOTAL of building and eletrical permit
                total_of_building_permit = 0
                total_of_electrical_permit = 0

                # Fetch all permits with the specified final status
                total_of_all_permits = building_record.objects.filter(final_status__in=statuses, date_final_status__year=select_year)

                # Iterate through permits with final status 'COMPLIED'
                for permit in total_of_all_permits.filter(final_status='COMPLIED'):
                    # Check and accumulate occupancy permit values
                    if permit.occupancy_permit:
                        total_of_building_permit += float(permit.occupancy_permit)  # Convert to float if stored as a string

                    # Check and accumulate electrical permit values
                    if permit.electrical_permit:
                        total_of_electrical_permit += float(permit.electrical_permit)  # Convert to float if stored as a string

                # Format the totals with commas and two decimal places
                total_of_building_permit = "{:,.2f}".format(total_of_building_permit)
                total_of_electrical_permit = "{:,.2f}".format(total_of_electrical_permit)

                

                context = {'form': form, 
                           'select_year': select_year, 
                           'filter_button': False,
                           'reset_button': True,
                           'formatted_complied_count': formatted_complied_count,
                           'formatted_lot_owner_consent_count': formatted_lot_owner_consent_count,
                           'formatted_noncompliant_count': formatted_noncompliant_count,
                           'formatted_processing_count': formatted_processing_count,
                           'formatted_reassessment_count': formatted_reassessment_count,
                           'formatted_no_entry_count': formatted_no_entry_count,
                           'formatted_total_count': formatted_total_count,
                            'results': results,
                            'total_of_building_permit': total_of_building_permit,
                            'total_of_electrical_permit': total_of_electrical_permit,
                            'audit_trail_record': audit_trail_record,
                           }
                return render(request, 'dashboard.html', context)
            else:
                messages.warning(request, "Invalid form submission.")
        elif 'reset_button' in request.POST:
            request.session['select_year'] = None
            return redirect('dashboard')
    else:
        form = dashboard_selected_year()
        status_counts = building_record.objects.filter(
            final_status__in=[
                "COMPLIED",
                "LOT OWNER CONSENT",
                "NONCOMPLIANT",
                "PROCESSING",
                "REASSESSMENT",
                ""
            ]
        ).values('final_status').annotate(count=Count('final_status'))

        # Initialize counts for each final_status
        complied_count = 0
        lot_owner_consent_count = 0
        noncompliant_count = 0
        processing_count = 0
        reassessment_count = 0
        no_entry_count = 0

        # Populate the counts based on the results
        for item in status_counts:
            if item['final_status'] == "COMPLIED":
                complied_count = item['count']
            elif item['final_status'] == "LOT OWNER CONSENT":
                lot_owner_consent_count = item['count']
            elif item['final_status'] == "NONCOMPLIANT":
                noncompliant_count = item['count']
            elif item['final_status'] == "PROCESSING":
                processing_count = item['count']
            elif item['final_status'] == "REASSESSMENT":
                reassessment_count = item['count']
            elif item['final_status'] == "":
                no_entry_count = item['count']

        total_count = (complied_count +
                    lot_owner_consent_count +
                    noncompliant_count +
                    processing_count +
                    reassessment_count +
                    no_entry_count)
        # Prepare the context with separate counts
        formatted_complied_count = "{:,}".format(complied_count)
        formatted_lot_owner_consent_count = "{:,}".format(lot_owner_consent_count)
        formatted_noncompliant_count = "{:,}".format(noncompliant_count)
        formatted_processing_count = "{:,}".format(processing_count)
        formatted_reassessment_count = "{:,}".format(reassessment_count)
        formatted_no_entry_count = "{:,}".format(no_entry_count)
        formatted_total_count = "{:,}".format(total_count)

        # FOR TABLE
        statuses = ['COMPLIED', 'NONCOMPLIANT', 'REASSESSMENT', 'PROCESSING', 'LOT OWNER CONSENT', '']

        results = []

        # Loop through each barangay choice
        for brgy_code, brgy_name in BRGY_CHOICES:
            permits = building_record.objects.filter(brgy_pin=brgy_code, final_status__in=statuses)
            total_permits = permits.count()

            # Initialize sums for occupancy and electrical permits
            total_occupancy_permits = 0
            total_electrical_permits = 0

            # Sum the values of occupancy_permit and electrical_permit for 'Complied' status
            for permit in permits.filter(final_status='COMPLIED'):
                if permit.occupancy_permit:
                    total_occupancy_permits += float(permit.occupancy_permit)  # Convert to int if stored as a string
                if permit.electrical_permit:
                    total_electrical_permits += float(permit.electrical_permit)  # Convert to int if

            total_occupancy_permits = "{:,.2f}".format(total_occupancy_permits)
            total_electrical_permits = "{:,.2f}".format(total_electrical_permits)

            brgy_counts = {
            'barangay': brgy_name,
            'Complied': "{:.2f}".format((permits.filter(final_status='COMPLIED').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
            'Noncompliant': "{:.2f}".format((permits.filter(final_status='NONCOMPLIANT').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
            'Reassessment': "{:.2f}".format((permits.filter(final_status='REASSESSMENT').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
            'Processing': "{:.2f}".format((permits.filter(final_status='PROCESSING').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
            'LotOwnerConsent': "{:.2f}".format((permits.filter(final_status='LOT OWNER CONSENT').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
            'NoTagging': "{:.2f}".format((permits.filter(final_status='').count() / total_permits * 100.0)) if total_permits > 0 else "0.00",
            'total_occupancy_permits': total_occupancy_permits,  # Add occupancy permits count
            'total_electrical_permits': total_electrical_permits,
        }


            results.append(brgy_counts)

        # TOTAL of building and eletrical permit
        total_of_building_permit = 0
        total_of_electrical_permit = 0

        # Fetch all permits with the specified final status
        total_of_all_permits = building_record.objects.filter(final_status__in=statuses)

        # Iterate through permits with final status 'COMPLIED'
        for permit in total_of_all_permits.filter(final_status='COMPLIED'):
            # Check and accumulate occupancy permit values
            if permit.occupancy_permit:
                total_of_building_permit += float(permit.occupancy_permit)  # Convert to float if stored as a string

            # Check and accumulate electrical permit values
            if permit.electrical_permit:
                total_of_electrical_permit += float(permit.electrical_permit)  # Convert to float if stored as a string

        # Format the totals with commas and two decimal places
        total_of_building_permit = "{:,.2f}".format(total_of_building_permit)
        total_of_electrical_permit = "{:,.2f}".format(total_of_electrical_permit)

        # Print the results
        print(f'Total of Building Permit: {total_of_building_permit}')
        print(f'Total of Electrical Permit: {total_of_electrical_permit}')
        
    # print(results)  # Debugging output to check results
    context = {
    'formatted_complied_count': formatted_complied_count,
    'formatted_lot_owner_consent_count': formatted_lot_owner_consent_count,
    'formatted_noncompliant_count': formatted_noncompliant_count,
    'formatted_processing_count': formatted_processing_count,
    'formatted_reassessment_count': formatted_reassessment_count,
    'formatted_no_entry_count': formatted_no_entry_count,
    'formatted_total_count': formatted_total_count,
    'total_of_building_permit': total_of_building_permit,
    'total_of_electrical_permit': total_of_electrical_permit,
    'results': results,
    'form': form,
    'filter_button': filter_button,
    'reset_button': reset_button,
    'audit_trail_record': audit_trail_record,
    'today': today,
    }

    # Render the template with the context
    return render(request, 'dashboard.html', context) # Initialize the form if not a POST request
    
def dashboard_data(request):
    # Query to get the count of each final_status
    select_year = request.session.get('select_year', None)
    if select_year is not None:
        status_counts = building_record.objects.filter(
            Q(date_final_status__year=select_year) & Q(
                final_status__in=[
                    "COMPLIED",
                    "LOT OWNER CONSENT",
                    "NONCOMPLIANT",
                    "PROCESSING",
                    "REASSESSMENT",
                    ""
                ]
            )
        ).values('final_status').annotate(count=Count('final_status'))
    else:
        status_counts = building_record.objects.filter(
            final_status__in=[
                "COMPLIED",
                "LOT OWNER CONSENT",
                "NONCOMPLIANT",
                "PROCESSING",
                "REASSESSMENT",
                ""
            ]
        ).values('final_status').annotate(count=Count('final_status'))

    # Initialize counts dictionary
    counts = {
        "complied": 0,
        "lot_owner_consent": 0,
        "noncompliant": 0,
        "processing": 0,
        "reassessment": 0,
        "no_entry": 0,
    }

    # Populate counts from the query results
    for item in status_counts:
        status = item['final_status']
        if status == "COMPLIED":
            counts["complied"] += item['count']
        elif status == "LOT OWNER CONSENT":
            counts["lot_owner_consent"] += item['count']
        elif status == "NONCOMPLIANT":
            counts["noncompliant"] += item['count']
        elif status == "PROCESSING":
            counts["processing"] += item['count']
        elif status == "REASSESSMENT":
            counts["reassessment"] += item['count']
        elif status == "":
            counts["no_entry"] += item['count']

    # Calculate total counts
    total_counts = sum(counts.values())

    # Calculate percentages with two decimal places
    percentages = {key: round((value / total_counts * 100), 2) if total_counts > 0 else 0 for key, value in counts.items()}
    
    # Return only the percentages as a JSON response
    return JsonResponse(percentages)

@login_required
def reprint_notice(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = Reprint_Notice(request.POST)

            if 'generate_notice' in request.POST:
                if form.is_valid():
                    reprint_pin_number = form.cleaned_data['reprint_pin_number']
                    reprint_notice = form.cleaned_data['reprint_notice']

                    # Check if the record exists
                    record_checker = building_record.objects.filter(pin_number=reprint_pin_number)

                    if record_checker.exists():

                        records = record_checker.all()  # Fetch all matching records
                        output_data = []

                        # Determine the status based on reprint_notice
                        for record in records:
                            if reprint_notice == 'FIRST NOTICE' and record.first_notice_print_history == '':
                                status = record.status
                                notice_status = 'FIRST NOTICE'
                                notice_date = record.first_notice_date
                            elif reprint_notice == 'SECOND NOTICE' and record.second_notice_print_history == 'PRINTED':
                                status = record.second_status
                                notice_status = 'SECOND NOTICE'
                                notice_date = record.second_notice_date
                            elif reprint_notice == 'THIRD NOTICE' and record.third_notice_print_history == 'PRINTED':
                                status = record.third_status
                                notice_status = 'THIRD NOTICE'
                                notice_date = record.third_notice_date
                            elif reprint_notice == 'FOR LEGAL' and record.for_legal_notice_print_history == 'PRINTED':
                                status = record.for_legal_status
                                notice_status = 'FOR LEGAL'
                                notice_date = record.for_legal_notice_date
                            else:
                                status = None  # Handle unexpected values
                                notice_status = None
                                notice_date = None
                                messages.warning(request, "The record is not yet available!")
                                return render(request, 'reprint_notice.html', {'form': form, 'generate': True})
                            # Check if the status is NONCOMPLIANT
                            if status == 'NONCOMPLIANT':
                                if isinstance(notice_date, date):
                                    notice_date = notice_date.strftime('%Y-%m-%d')  # Format as needed
                                output_data.append({
                                    'id': record.id,
                                    'pin_number': record.pin_number,
                                    'building_owner': record.building_owner,
                                    'address': record.address,
                                    'notice_status': notice_status,
                                    'notice_date': notice_date,
                                })

                        request.session['notice_status'] = notice_status
                        if output_data:
                            return render(request, 'reprint_notice.html', {
                                'output_data': output_data,
                                'table': True,
                                'generate': False,
                                'reset': True
                            })
                        # Store output_data in session
                        else:
                            messages.info(request, "No NONCOMPLIANT statuses found for the selected records.")
                            return render(request, 'reprint_notice.html', {'form': form, 'generate': True})

                    else:
                        messages.warning(request, "No records found for the given PIN!")
                        return render(request, 'reprint_notice.html', {'form': form, 'generate': True})
                else:
                    messages.warning(request, "There was an error in the form submission.")
                    return render(request, 'reprint_notice.html', {'form': form, 'generate': True})

            if 'reset_notice' in request.POST:
                return render(request, 'reprint_notice.html', {'form': form, 'generate': True})

        else:
            # Render the form if the request method is GET
            form = Reprint_Notice()  # Ensure the form is instantiated
            return render(request, 'reprint_notice.html', {'form': form, 'generate': True})
    else:
        messages.warning(request, "You must be logged in to view the page!")
        return redirect('login_page')

    return render(request, 'reprint_notice.html', {'form': form, 'generate': True})

def reprint_notice_id(request, pk):
    if request.user.is_authenticated:
        record = building_record.objects.get(id=pk)
        signatory = Signatories.objects.all()
        output_data = request.session.get('notice_status', [])
        print(f"Output Data: {output_data}")
        return render(request, 'reprint_notice_id.html', {'record': record, 'signatory': signatory, 'output_data': output_data})
    else:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')

def reports(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view the page.")
        return redirect('login_page')
    form = Report_Notice(request.POST or None)
    today = timezone.localtime(timezone.now()).date()

    if request.method == 'POST':
        if 'generate_report' in request.POST:
            if form.is_valid():
                report_notice_status = form.cleaned_data['report_notice_status']
                report_brgy = form.cleaned_data['report_brgy']
                starting_date = form.cleaned_data['starting_date']
                ending_date = form.cleaned_data['ending_date']
                all_status = ['COMPLIED', 'NONCOMPLIANT', 'LOT OWNER CONSENT','PROCESSING','REASSESSMENT']
                # all_brgy = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '10A', '10B', '11', '12',
                #             '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '22A', '23', '24',
                #             '25', '26', '27', '28', '29', '29A', '30', '31', '32', '33', '34', '35', '36',
                #             '36A', '37', '37A', '38', '38A', '39', '40', '41', '42', '42A', '42B', '42C',
                #             '43', '44', '45', '45A', '46', '47', '47A', '47B', '48', '48A', '49', '49A',
                #             '50', '51', '52', '53', '53A', '53B', '54', '54A', '55', '56', '57', '58',
                #             '58A', '59', '60', '61', '61A', '062', '62A', '62B']


                 # Check if 'ALL STATUS' is selected
                if report_notice_status == 'ALL STATUS':
                    # Use Q objects to filter for all statuses
                    report_query = Q(final_status__in=all_status)
                elif report_notice_status == 'NO STATUS':
                    report_query = Q(final_status='')
                    print('no status selected')
                else:
                    # Use Q object for the selected status
                    report_query = Q(final_status=report_notice_status)

                if report_brgy == 'ALL BARANGAYS':
                    report_brgy_query = Q(brgy_pin__isnull=False)
                else:
                    report_brgy_query = Q(brgy_pin=report_brgy)

                # print(f'report_query: {report_query}')
                if (starting_date == None and ending_date) or (starting_date and ending_date == None):
                    messages.warning(request, "Invalid Date Range")
                    return render(request, 'reports.html', {'form': form, 'generate_report': True})
                elif starting_date == None and ending_date == None:
                    report_checker = building_record.objects.filter(
                        Q(report_query) & Q(report_brgy_query) & (
                            Q(first_notice_date__isnull=True) &
                            Q(second_notice_date__isnull=True) &
                            Q(third_notice_date__isnull=True) &
                            Q(for_legal_notice_date__isnull=True)
                        )
                    )
                elif ending_date > today:
                    messages.warning(request, "Invalid Date Range (Future dates are not allowed)")
                    return render(request, 'reports.html', {'form': form, 'generate_report': True})
                elif starting_date > ending_date:
                    messages.warning(request, "Invalid Date Range (Starting date cannot be after ending date)")
                    return render(request, 'reports.html', {'form': form, 'generate_report': True})
                elif starting_date < ending_date or starting_date == ending_date:
                    report_checker = building_record.objects.filter(
                        Q(report_query) & Q(report_brgy_query) & (
                            Q(first_notice_date__range=(starting_date, ending_date)) |
                            Q(second_notice_date__range=(starting_date, ending_date)) |
                            Q(third_notice_date__range=(starting_date, ending_date)) |
                            Q(for_legal_notice_date__range=(starting_date, ending_date))
                        )
                    )
                # report_checker_json = serialize('json', report_checker)# Convert to a list of dictionaries
                if report_checker.exists():
                    records = report_checker.all()  # Fetch all matching records
                    output_data = []
                    report_counter = 0
                    # Populate output_data with records
                    for record in records:
                        report_counter += 1
                        output_data.append({
                            'pin_number': record.pin_number,
                            'building_owner': record.building_owner,
                            'address': record.address,
                            'brgy_pin': record.brgy_pin,
                            'first_notice_date': record.first_notice_date.strftime('%m-%d-%Y') if record.first_notice_date else None,
                            'second_notice_date': record.second_notice_date.strftime('%m-%d-%Y') if record.second_notice_date else None,
                            'third_notice_date': record.third_notice_date.strftime('%m-%d-%Y') if record.third_notice_date else None,
                            'for_legal_notice_date': record.for_legal_notice_date.strftime('%m-%d-%Y') if record.for_legal_notice_date else None,
                            'second_notice_print_date': record.second_notice_print_date.strftime('%m-%d-%Y') if record.second_notice_print_date else None,
                            'third_notice_print_date': record.third_notice_print_date.strftime('%m-%d-%Y') if record.third_notice_print_date else None,
                            'for_legal_notice_print_date': record.for_legal_notice_print_date.strftime('%m-%d-%Y') if record.for_legal_notice_print_date else None,
                            'occupancy_permit': record.occupancy_permit,
                            'electrical_permit': record.electrical_permit,
                            'final_status': record.final_status,
                        })

                    request.session['report_checker'] = output_data

                    request.session['report_notice_status'] = report_notice_status
                    request.session['report_brgy'] = report_brgy

                    if starting_date and ending_date:
                        request.session['starting_date'] = starting_date.strftime('%m-%d-%Y')
                        request.session['ending_date'] = ending_date.strftime('%m-%d-%Y')
                    else:
                        request.session['starting_date'] = starting_date
                        request.session['ending_date'] = ending_date


                    report_matches = True
                    generate_report = False
                    reset = True
                else:
                    generate_report = True
                    report_matches = False
                    reset = False
                    messages.warning(request, "No records found for the given criteria.")
                    return render(request, 'reports.html', {'form': form, 'generate_report': generate_report})

                context = {
                    'report_checker': report_checker,
                    'today': today,
                    'report_matches': report_matches,
                    'generate_report': generate_report,
                    'reset': reset,
                    # 'no_of_notice': no_of_notice,
                    # 'print_button': print_button,  # Pass the print_button variable to the context
                }

                return render (request, 'reports.html', context)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.warning(request, f"{field}: {error}")

        if 'reset_report' in request.POST:
                    return render(request, 'reports.html', {'form': form, 'generate_report': True})
    else:
        form = Report_Notice()
        return render(request, 'reports.html', {'form': form, 'generate_report': True})

    return render (request, 'reports.html')

def sort_key(value):
    # Split the numeric and alphabetic parts of brgy_pin
    match = re.match(r"(\d+)([A-Za-z]*)", value['brgy_pin'])
    number_part = int(match.group(1)) if match else 0
    letter_part = match.group(2) if match else ""

    # Extract final_status and building_owner for sorting
    final_status = value.get('final_status', '')
    building_owner = value.get('building_owner', '')

    return (number_part, letter_part, final_status, building_owner)

def print_report(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view the page.")
        return redirect('login_page')

    today = date.today()
    # Retrieve output_data directly from session
    output_data = request.session.get('report_checker', [])

    # Sort output_data using the custom sort_key function
    output_data.sort(key=sort_key)

    report_notice_status = request.session.get('report_notice_status', [])
    report_brgy = request.session.get('report_brgy')
    starting_date = request.session.get('starting_date', [])
    ending_date = request.session.get('ending_date', [])

    print(report_brgy)
    report_counter_data = len(output_data)  # Count of reports

    # Render the template with the output data
    context = {
        'output_data': output_data,
        'today': today,
        'report_counter_data': report_counter_data,
        'report_notice_status': report_notice_status,
        'report_brgy': report_brgy,
        'starting_date': starting_date,
        'ending_date': ending_date,
    }

    response = render(request, 'print_report.html', context)
    return response

def daily_encoded_report(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'You must be logged in to view the page.')
        return redirect('login_page')

    form = Daily_Encoded(request.POST or None)
    today = timezone.localtime(timezone.now()).date()

    if request.method == 'POST':
        if 'generate_report' in request.POST:
            if form.is_valid():
                select_user = form.cleaned_data['select_user']
                encoded_date = form.cleaned_data['encoded_date']
            # Filter records where the created_at date matches the encoded_date
                if select_user == 'All Encoders':  # Use the value you set in your form for "All Users"
                    # Query for all users
                    report_query = Q(created_by_id__in=User.objects.all())
                else:
                    # Query for a specific user
                    report_query = Q(created_by__username=select_user)

                if encoded_date > today:
                    messages.warning(request, 'Invalid Date')
                    return render(request, 'daily_encoded_report.html', {'form': form, 'generate_report': True})

                report_checker = building_record.objects.annotate(
                created_date=TruncDate('created_at')  # Truncate created_at to just the date
                ).filter(
                    report_query & Q(created_date=encoded_date)  # Compare with encoded_date
                )


                if report_checker.exists():
                    records = report_checker.all()  # Fetch all matching records
                    output_data = []
                    for record in records:
                        output_data.append({
                            'pin_number': record.pin_number,
                            'building_owner': record.building_owner,
                            'address': record.address,
                            'brgy_pin': record.brgy_pin,
                            'final_status': record.final_status,
                            'created_by': record.created_by.username,  # Assuming created_by is a User instance
                            'created_at': record.created_at.astimezone(manila_tz).strftime('%B %d, %Y, %I:%M %p').lower().replace('am', 'a.m.').replace('pm', 'p.m.'),
                            'select_user': select_user,
                        })
                    request.session['report_encoded'] = output_data
                    request.session['select_user'] = select_user


                    report_matches = True
                    generate_report = False
                    reset = True
                else:
                    generate_report = True
                    report_matches = False
                    reset = False
                    messages.warning(request, "No records found for the given criteria.")
                    return render(request, 'daily_encoded_report.html', {'form': form, 'generate_report': generate_report})

                context = {
                    'report_checker': report_checker,
                    'today': today,
                    'report_matches': report_matches,
                    'generate_report': generate_report,
                    'reset': reset,
                    # 'no_of_notice': no_of_notice,
                    # 'print_button': print_button,  # Pass the print_button variable to the context
                }

                return render (request, 'daily_encoded_report.html', context)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.warning(request, f"{field}: {error}")

        if 'reset_report' in request.POST:
                    return render(request, 'daily_encoded_report.html', {'form': form, 'generate_report': True})

    else:
        form = Daily_Encoded()

    return render(request, 'daily_encoded_report.html', {'form': form, 'generate_report': True})

def print_encoded_report(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view the page.")
        return redirect('login_page')

    today = timezone.localtime(timezone.now()).date()
    # Retrieve output_data directly from session
    output_data = request.session.get('report_encoded', [])
    select_user = request.session.get('select_user')


    # Sort output_data using the custom sort_key function
    output_data.sort(key=sort_key)

    report_counter_data = len(output_data)  # Count of reports

    # Render the template with the output data
    context = {
        'output_data': output_data,
        'today': today,
        'report_counter_data': report_counter_data,
        'select_user': select_user,

    }

    response = render(request, 'print_encoded_report.html', context)
    return response

def occupancy_and_electrical_payments(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'You must be logged in to view the page.')
        return redirect('login_page')

    form = Occupancy_Eletrical_Payment(request.POST or None)
    today = timezone.localtime(timezone.now()).date()

    if request.method == 'POST':
        if 'generate_report' in request.POST:
            if form.is_valid():
                report_brgy = form.cleaned_data['report_brgy']
                select_year = form.cleaned_data['select_year']
                if_complied = 'COMPLIED'
                request.session['selected_brgy_in_occu_elec'] = report_brgy
                request.session['select_year'] = select_year
                if report_brgy == 'ALL BARANGAYS':
                    report_brgy_query = Q(brgy_pin__isnull=False)
                else:
                    report_brgy_query = Q(brgy_pin=report_brgy)

                report_checker = building_record.objects.filter(
                    Q(report_brgy_query) & Q(final_status=if_complied) & Q(date_complied__year=select_year)  # Compare with encoded_date
                )
                # Initialize sums for occupancy and electrical permits
                total_occupancy_payment = 0
                total_electrical_payment = 0
                grand_total_occu_elec = 0
                # Sum the values of occupancy_permit and electrical_permit for 'Complied' status
                for amount in report_checker:
                    if amount.occupancy_permit:
                        total_occupancy_payment += float(amount.occupancy_permit)
                        grand_total_occu_elec += float(amount.occupancy_permit) # Convert to int if stored as a string
                    if amount.electrical_permit:
                        total_electrical_payment += float(amount.electrical_permit)  # Convert to int if
                        grand_total_occu_elec += float(amount.electrical_permit) # Convert to int if stored as a string

                total_occupancy_payment = "{:,.2f}".format(total_occupancy_payment)
                total_electrical_payment = "{:,.2f}".format(total_electrical_payment)
                grand_total_occu_elec = "{:,.2f}".format(grand_total_occu_elec)
                request.session['grand_total_occu_elec'] = grand_total_occu_elec
                request.session['total_occupancy_payment'] = total_occupancy_payment
                request.session['total_electricl_payment'] = total_electrical_payment


                if report_checker.exists():
                    records = report_checker.all()  # Fetch all matching records
                    output_data = []
                    for record in records:
                        occupancy_permit_value = float(record.occupancy_permit) if record.occupancy_permit else 0.0
                        electrical_permit_value = float(record.electrical_permit) if record.electrical_permit else 0.0
                        output_data.append({
                            'pin_number': record.pin_number,
                            'building_owner': record.building_owner,
                            'brgy_pin': record.brgy_pin,
                            'final_status': record.final_status,
                            'occupancy_permit': f"{occupancy_permit_value:,.2f}",
                            'electrical_permit': f"{electrical_permit_value:,.2f}",
                            'date_complied': record.date_complied.strftime('%m-%d-%Y') if record.date_complied else None,

                        })

                    request.session['occupancy_electrical'] = output_data

                    report_matches = True
                    generate_report = False
                    reset = True
                else:
                    generate_report = True
                    report_matches = False
                    reset = False
                    messages.warning(request, "No records found for the given criteria.")
                    return render(request, 'occupancy_and_electrical_payments.html', {'form': form, 'generate_report': generate_report})

                context = {
                    'report_checker': report_checker,
                    'today': today,
                    'report_matches': report_matches,
                    'generate_report': generate_report,
                    'reset': reset,
                    # 'no_of_notice': no_of_notice,
                    # 'print_button': print_button,  # Pass the print_button variable to the context
                }

                return render (request, 'occupancy_and_electrical_payments.html', context)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.warning(request, f"{field}: {error}")

        if 'reset_report' in request.POST:
                    return render(request, 'occupancy_and_electrical_payments.html', {'form': form, 'generate_report': True})

    else:
        form = Occupancy_Eletrical_Payment()

    return render(request, 'occupancy_and_electrical_payments.html', {'form': form, 'generate_report': True})

def print_occupancy_and_electrical_payments(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view the page.")
        return redirect('login_page')

    today = timezone.localtime(timezone.now()).date()
    # Retrieve output_data directly from session
    output_data = request.session.get('occupancy_electrical', [])
    selected_brgy_in_occu_elec = request.session.get('selected_brgy_in_occu_elec')
    total_occupancy_payment = request.session.get('total_occupancy_payment')
    total_electricl_payment = request.session.get('total_electricl_payment')
    grand_total_occu_elec = request.session.get('grand_total_occu_elec')
    select_year = request.session.get('select_year')

    # Sort output_data using the custom sort_key function
    output_data.sort(key=sort_key)

    report_counter_data = len(output_data)  # Count of reports

    # Render the template with the output data
    context = {
        'output_data': output_data,
        'today': today,
        'report_counter_data': report_counter_data,
        'selected_brgy_in_occu_elec': selected_brgy_in_occu_elec,
        'total_occupancy_payment': total_occupancy_payment,
        'total_electricl_payment': total_electricl_payment,
        'grand_total_occu_elec': grand_total_occu_elec,
        'select_year': select_year

    }

    response = render(request, 'print_occupancy_and_electrical_payments.html', context)
    return response


def print_history(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view the page.")
        return redirect('login_page')

    notices = building_record.objects.filter(
            (Q(second_notice_print_history="PRINTED")) |
            (Q(third_notice_print_history="PRINTED")) |
            (Q(for_legal_notice_print_history="PRINTED"))
        )

    return render(request, 'print_history.html', {'notices': notices})

# def check_session_data(request):
#     # Print all session data
#     print(request.session.items())  # Outputs all session key-value pairs
#     return HttpResponse("Check the console for session data.")
# def generatepdf(request):
#     today = timezone.now().date()
#     formatted_date = today.strftime('%m-%d-%Y')

#     pdf = pdfkit.from_url(request.build_absolute_uri(reverse('download_all_pdf')), False, configuration=config)

#     response = HttpResponse(pdf, content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="{formatted_date}.pdf"'
#     return response


# for viewing only
def print_backside(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')

    return render(request, 'print_backside.html')

def pending_notice(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be Logged In to view the page!")
        return redirect('login_page')
    today = timezone.localtime(timezone.now()).date()
    compare_date = datetime.strptime("3/25/2025", "%m/%d/%Y").date()
    pending_pin_number = request.session.get('pin_number', [])
    pending_notice_id = building_record.objects.filter(pin_number=pending_pin_number)
    if request.method == 'POST':
            if 'successful_print' in request.POST:
                if pending_notice_id.exists():
                     for notice in pending_notice_id:
                        # Update the print history based on the type of notice
                        if notice.second_notice_date >= compare_date and notice.second_notice_print_history == "" and notice.second_status == "NONCOMPLIANT" and notice.second_notice_date < today:
                            notice.second_notice_print_history = "PRINTED"
                            notice.second_notice_print_date = today
                            notice.save(update_fields=['second_notice_print_history', 'second_notice_print_date'])
                        if notice.third_notice_date >= compare_date and notice.third_notice_print_history == "" and notice.third_status == "NONCOMPLIANT" and notice.third_notice_date < today:
                            notice.third_notice_print_history = "PRINTED"
                            notice.third_notice_print_date = today
                            notice.save(update_fields=['third_notice_print_history', 'third_notice_print_date'])
                        if notice.for_legal_notice_date >= compare_date and notice.for_legal_notice_print_history == "" and notice.for_legal_status == "NONCOMPLIANT" and notice.for_legal_notice_date < today:
                            notice.for_legal_notice_print_history = "PRINTED"
                            notice.for_legal_notice_print_date = today
                            notice.save(update_fields=['for_legal_notice_print_history', 'for_legal_notice_print_date'])
                        else:
                            print('Unknown Notice')
                messages.success(request, f'Print was successful.{pending_pin_number}')

            if 'unsuccessful_print' in request.POST:
                messages.warning(request, 'Print was unsuccessful.')

    #UNCOMMENT BY NEXT YEAR
    # pending_notice = building_record.objects.filter(
    #     (Q(second_notice_date__lt=today) & Q(second_status="NONCOMPLIANT") & Q(first_notice_print_history="")) |
    #     (Q(third_notice_date__lt=today) & Q(third_status="NONCOMPLIANT") & Q(second_notice_print_history="")) |
    #     (Q(for_legal_notice_date__lt=today) & Q(for_legal_status="NONCOMPLIANT") & Q(for_legal_notice_print_history=""))
    # )

    #COMMENT BY NEXT YEAR
    pending_notice = building_record.objects.filter(
        (Q(second_notice_date__gte=compare_date) & Q(second_notice_date__lt=today) & Q(second_status="NONCOMPLIANT") & Q(second_notice_print_history="")) |
        (Q(third_notice_date__gte=compare_date) & Q(third_notice_date__lt=today) & Q(third_status="NONCOMPLIANT") & Q(third_notice_print_history="")) |
        (Q(for_legal_notice_date__gte=compare_date) & Q(for_legal_notice_date__lt=today) & Q(for_legal_status="NONCOMPLIANT") & Q(for_legal_notice_print_history=""))
    )

    no_of_pending_notice = 0
    if pending_notice.exists():
        for pending_notices in pending_notice:
            no_of_pending_notice += 1

    else:
        print('No Pending Notices')
         # If no pending notices are found, render the template with a message
         # You can customize the message as needed
         # messages.info(request, "No pending notices found.")
         #
    context = {
        'pending_notice': pending_notice,
        'today': today,
        'no_of_pending_notice': no_of_pending_notice,
        'compare_date': compare_date,
    }
    return render(request, 'pending_notice.html', context)

def print_pending_notice(request, pk):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view the page.")
        return redirect('login_page')

    compare_date = datetime.strptime("3/25/2025", "%m/%d/%Y").date()
    today = timezone.localtime(timezone.now()).date()
    record = building_record.objects.get(id=pk)
    signatory = Signatories.objects.all()

    request.session['pin_number'] = record.pin_number
    print(record.pin_number)
    context = {
        'record': record,
        'today': today,
        'signatory': signatory,
        'compare_date': compare_date,
    }

    return render(request, 'print_pending_notice.html', context)

@login_required
def database_table(request):
    # Check if the user is an admin
    if not request.user.is_staff:
        messages.warning(request, "You do not have permission to view this page.")
        return redirect('dashboard')  # Redirect to a different page, e.g., home


    record = building_record.objects.all()
    context = {
        'record': record,
    }
    return render(request, 'database_table.html', context)

@login_required
def update_database_table(request, pk):
    if not request.user.is_staff:
        messages.warning(request, "You do not have permission to view this page.")
        return redirect('dashboard')  # Redirect to a different page, e.g., home

    current_record = building_record.objects.get(id=pk)
    form = Add_Records(request.POST or None, instance=current_record)

    # Make all fields editable and not required
    for field in form.fields.values():
        field.widget.attrs.pop('readonly', None)  # Remove readonly attribute if it exists
        field.required = False  # Set the field as not required

    if form.is_valid():
        if form.has_changed():
            # Print the changed fields
            changed_fields = form.changed_data
            print(f"Changed fields: {changed_fields}")  # Print the changed fields

            # Save the instance
            form.save()
            messages.success(request, 'Record updated successfully!')
            return redirect('update_database_table', pk=pk)

        else:  # If no changes were made
            messages.info(request, "The record remains unchanged.")
            return redirect('update_database_table', pk=pk)

    else:
        # Handle form errors if the form is not valid
        for field, errors in form.errors.items():
            for error in errors:
                messages.warning(request, f"{field}: {error}")

    return render(request, 'update_database_table.html', {'form': form})


@receiver(post_save, sender=building_record)
def log_action(sender, instance, created, **kwargs):
    if created:
        ActionLog.objects.create(user=instance.created_by, action='Created a record')

def get_user(request):
    user = request.user
    # Do something with the user object
    return render(request, 'navbar.html', {'user': user})

def audit_trail(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view the page.")
        return redirect('login_page')
    audit_trail_record = building_record.history.all()
   
    context = {
        'audit_trail_record': audit_trail_record
       
    }
    return render(request, 'audit_trail.html', context)







