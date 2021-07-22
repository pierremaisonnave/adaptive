import debug_toolbar 
from django.contrib import admin
from django.urls import path, include


from django.conf import settings # so as to save pdf to Media forder
from django.conf.urls.static import static# so as to save pdf to Media forder

from django_email_verification import urls as email_urls

from django.contrib.auth import views as auth_views#for pass reset
from royalty.settings.base import GOOGLE_RECAPTCHA_SITE_KEY,GOOGLE_RECAPTCHA_SECRET_KEY


urlpatterns = [
    path('', include('royalty_app.urls')),
    path('admin/', admin.site.urls),
    path('email/', include(email_urls)),

    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_reset/password_change_done.html'), 
        name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_reset/password_change.html'), 
        name='password_change'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_done.html'),
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset/password_reset_confirm.html',
    ), name='password_reset_confirm'),

    #path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset/password_reset_form.html',
            subject_template_name='password_reset/password_reset_subject.txt',
            email_template_name='password_reset/password_reset_email.html',
            extra_context ={'recaptcha_site_key': GOOGLE_RECAPTCHA_SITE_KEY},
        ),
        name='password_reset'
        ),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_complete.html'),
        name='password_reset_complete'),
    
    path('__debug__/', include(debug_toolbar.urls)),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



