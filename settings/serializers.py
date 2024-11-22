# serializers.py
from rest_framework import serializers
from .models import ContactUs

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'  # Include all fields in the model
        read_only_fields = ['submitted_at', 'is_solved', 'solved_at']
    
    def validate(self, data):
        """
        Ensure the user hasn't already submitted a form with is_solved=False.
        """
        email = data.get('email')
        if ContactUs.objects.filter(email=email, is_solved=False).exists():
            raise serializers.ValidationError(
                "You have already submitted a message that is pending resolution."
            )
        return data