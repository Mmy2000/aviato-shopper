from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from accounts.models import Profile, User
from order.models import Order
from .serializers import OrderSerializer
from django.utils.timezone import now, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.db import models


# Create your views here.

class RecentOrdersView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]  # Optional: restrict to authenticated users

    def get(self, request):
        recent_orders = Order.objects.filter(is_orderd=True).order_by('-created_at')[:4]
        serializer = OrderSerializer(recent_orders, many=True)
        return Response(serializer.data)

class DashboardDataView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    """
    API endpoint for retrieving dashboard data, including key metrics and recent activity.
    """

    def calculate_percentage_change(self, current, previous):
        """
        Calculate percentage change between two values.
        Returns a string with a percentage change or "N/A" if previous is zero.
        """
        if previous == 0:
            return "N/A"
        change = ((current - previous) / previous) * 100
        return f"{change:+.1f}%"

    def format_time_difference(self, timestamp):
        """
        Format the time difference in minutes, hours, days, months, or years.
        """
        time_difference = now() - timestamp
        total_seconds = time_difference.total_seconds()

        if total_seconds < 3600:  # Less than an hour
            minutes = int(total_seconds // 60)
            return f"{minutes} minutes ago"
        elif total_seconds < 86400:  # Less than a day
            hours = int(total_seconds // 3600)
            return f"{hours} hours ago"
        elif total_seconds < 2592000:  # Less than a month (30 days)
            days = int(total_seconds // 86400)
            return f"{days} days ago"
        elif total_seconds < 31536000:  # Less than a year (12 months)
            months = int(total_seconds // 2592000)
            return f"{months} months ago"
        else:  # More than a year
            years = int(total_seconds // 31536000)
            return f"{years} years ago"

    def get(self, request):
        # Define time ranges
        today = now()
        last_7_days = today - timedelta(days=7)
        previous_7_days = last_7_days - timedelta(days=7)

        # Metrics: Total Users
        total_users = User.objects.count()
        previous_total_users = User.objects.filter(date_joined__lt=last_7_days).count()
        total_users_change = self.calculate_percentage_change(total_users, previous_total_users)

        # Metrics: Revenue
        current_revenue = (
            Order.objects.filter(
                is_orderd=True,
                payment__status="Completed",  # Ensure payments are completed
                created_at__gte=last_7_days
            )
            .aggregate(total=Sum('order_total'))['total'] or 0
        )
        previous_revenue = (
            Order.objects.filter(
                is_orderd=True,
                payment__status="Completed",  # Ensure payments are completed
                created_at__gte=previous_7_days,
                created_at__lt=last_7_days
            )
            .aggregate(total=Sum('order_total'))['total'] or 0
        )
        revenue_change = self.calculate_percentage_change(current_revenue, previous_revenue)

        # Metrics: New Orders
        current_new_orders = Order.objects.filter(is_orderd=True, created_at__gte=last_7_days).count()
        previous_new_orders = Order.objects.filter(
            is_orderd=True, created_at__gte=previous_7_days, created_at__lt=last_7_days
        ).count()
        new_orders_change = self.calculate_percentage_change(current_new_orders, previous_new_orders)

        # Compile recent activity data
        recent_orders = [
            {
                "message": f"{order.user.full_name} placed an order",
                "details": f"Order Total: ${order.order_total:.2f}",
                "timestamp": self.format_time_difference(order.created_at),
                "datetime": order.created_at,  # For sorting
            }
            for order in Order.objects.filter(is_orderd=True).order_by('-created_at')[:5]
        ]

        recent_signups = [
            {
                "message": f"{user.first_name} {user.last_name} signed up",
                "details": "New account created",
                "timestamp": self.format_time_difference(user.date_joined),
                "datetime": user.date_joined,  # For sorting
            }
            for user in User.objects.filter(date_joined__gte=today - timedelta(days=1)).order_by('-date_joined')[:5]
        ]

        profile_updates = [
            {
                "message": f"{profile.user.first_name} {profile.user.last_name} updated their profile",
                "details": "Profile information updated",
                "timestamp": self.format_time_difference(profile.updated_at),
                "datetime": profile.updated_at,  # For sorting
            }
            for profile in Profile.objects.filter(updated_at__gte=today - timedelta(days=1)).order_by('-updated_at')[:5]
        ]

        # Combine all recent activity into a single list and sort by datetime
        recent_activity = recent_orders + recent_signups + profile_updates
        sorted_recent_activity = sorted(recent_activity, key=lambda x: x["datetime"], reverse=True)

        # Remove the 'datetime' key before returning the response
        for activity in sorted_recent_activity:
            activity.pop("datetime")

        # Prepare response data
        data = {
            "metrics": {
                "total_users": total_users,
                "total_users_change": total_users_change,
                "total_revenue": current_revenue,
                "revenue_change": revenue_change,
                "new_orders": current_new_orders,
                "new_orders_change": new_orders_change,
            },
            "recent_activity": sorted_recent_activity,
        }

        return Response(data)
