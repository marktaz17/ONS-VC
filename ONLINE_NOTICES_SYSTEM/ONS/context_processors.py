# from django.utils.timezone import localtime, now, timezone
from ONS.models import building_record
from django.db.models import Q
from django.utils import timezone
from datetime import datetime

def global_no_of_notice(request):
    if request.user.is_authenticated:
        # today = localtime(now()).date()
        today = timezone.localtime(timezone.now()).date()
        # Calculate the number of notices
        no_of_notice = building_record.objects.filter(
            (Q(second_status="NONCOMPLIANT") & Q(second_notice_date=today) & Q(second_notice_print_history="")) |
            (Q(third_status="NONCOMPLIANT") & Q(third_notice_date=today) & Q(third_notice_print_history="")) |
            (Q(for_legal_status="NONCOMPLIANT") & Q(for_legal_notice_date=today) & Q(for_legal_notice_print_history=""))
        ).count()
        # print(today)
    else:
        no_of_notice = 0

    return {'no_of_notice': no_of_notice}

def global_no_of_pending_notice(request):
    if request.user.is_authenticated:
        # today = localtime(now()).date()
        today = timezone.localtime(timezone.now()).date()
        compare_date = datetime.strptime("3/25/2025", "%m/%d/%Y").date()
        # UNCOMMMENT BY NEXT YEAR
        # pending_notice = building_record.objects.filter(
    #     (Q(second_notice_date__lt=today) & Q(second_status="NONCOMPLIANT") & Q(first_notice_print_history="")) | 
    #     (Q(third_notice_date__lt=today) & Q(third_status="NONCOMPLIANT") & Q(second_notice_print_history="")) |
    #     (Q(for_legal_notice_date__lt=today) & Q(for_legal_status="NONCOMPLIANT") & Q(for_legal_notice_print_history=""))
    # )
    # COMMENT BY NEXT YEAR
        no_of_pending_notice = building_record.objects.filter(
        (Q(second_notice_date__gte=compare_date) & Q(second_notice_date__lt=today) & Q(second_status="NONCOMPLIANT") & Q(second_notice_print_history="")) | 
        (Q(third_notice_date__gte=compare_date) & Q(third_notice_date__lt=today) & Q(third_status="NONCOMPLIANT") & Q(third_notice_print_history="")) |
        (Q(for_legal_notice_date__gte=compare_date) & Q(for_legal_notice_date__lt=today) & Q(for_legal_status="NONCOMPLIANT") & Q(for_legal_notice_print_history=""))
        ).count()
        # print(today)
    else:
        no_of_pending_notice = 0

    return {'no_of_pending_notice': no_of_pending_notice}