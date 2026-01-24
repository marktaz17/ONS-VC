# from django.contrib.auth import logout
# from django.utils.timezone import now
# from datetime import datetime, timedelta, date
# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# import logging

# logger = logging.getLogger(__name__)

# class AutoLogoutMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.user.is_authenticated:
#             last_activity = request.session.get('last_activity')
#             if last_activity:
#                 from django.utils.dateparse import parse_datetime
#                 last_activity = parse_datetime(last_activity)

#                 elapsed_time = now() - last_activity
#                 if elapsed_time.total_seconds() > 7200:  # 30 seconds timeout
#                     logout(request)
#                     request.session.flush()
#                     logger.info(f"User {request.user.username} logged out due to inactivity.")
#                     return redirect('login_page')

#             # Update the session with the current time
#             request.session['last_activity'] = now().isoformat()
#         return self.get_response(request)