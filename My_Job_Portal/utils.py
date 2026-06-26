from Accounts.models import ActivityLog
from django.template.loader import get_template, render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def log_activity(user, action, description=None, icon_class='fa-solid fa-circle-dot', link=None):
    """
    Creates an activity log entry for the user.
    """
    if user.is_authenticated:
        ActivityLog.objects.create(
            user=user,
            action=action,
            description=description,
            icon_class=icon_class,
            link=link
        )

def render_to_pdf(template_src, context_dict={}):
    """
    Renders a Django template to a PDF and returns an HttpResponse.
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def send_email_notification(subject, template_name, context, recipient_list):
    """
    Sends an email notification using a template.
    """
    try:
        html_message = render_to_string(template_name, context)
        send_mail(
            subject,
            "", # Plain text message (optional, but good practice)
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
