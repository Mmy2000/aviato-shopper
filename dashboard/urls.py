from django.urls import path
from .views import DashboardDataView, RecentOrdersView

urlpatterns = [
    path('recent-orders/', RecentOrdersView.as_view(), name='recent-orders'),
    path('', DashboardDataView.as_view(), name='dashboard'),
]
