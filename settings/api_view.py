# views.py
from email.message import EmailMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from .models import ContactUs
from .serializers import ContactUsSerializer
from django.core.mail import send_mail

class ContactUsView(APIView):
    def get(self, request):
        """Retrieve all messages."""
        contacts = ContactUs.objects.all()
        serializer = ContactUsSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()

            # Send confirmation email to the user
            subject = f"Thank you for contacting us, {contact.name}"
            message = (
                f"Dear {contact.name},\n\n"
                f"Thank you for reaching out to us. We have received your message:\n\n"
                f"Subject: {contact.subject}\n"
                f"Message: {contact.message}\n\n"
                f"Our team will get back to you as soon as possible.\n\n"
                f"Best regards,\n"
                f"Your Company Name"
            )
            recipient = contact.email

            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,  # Replace with your sender email
                    [recipient],
                    fail_silently=False,
                )
                return Response(
                    {
                        "message":"Your message has been submitted successfully, and a confirmation email has been sent!",
                        "data":serializer.data
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(
                    {"detail": "Message saved but email could not be sent.", "error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
