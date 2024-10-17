from django.contrib import admin
from .models import Profile, User
from django.contrib.auth.admin import UserAdmin

# Inline for Profile to show up in the User admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class AccountAdmin(UserAdmin):
    # Display fields in the admin list view
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active', 'is_admin')
    
    # Fields that can be clicked to open the user’s detail view
    list_display_links = ('email', 'first_name', 'last_name')
    
    # Make certain fields read-only
    readonly_fields = ('last_login', 'date_joined')
    
    # Add filters for user status and dates
    list_filter = ('is_active', 'is_admin', 'date_joined')
    
    # Add a search bar for key fields
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    # Customize the form fieldsets to organize fields better
    fieldsets = (
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'username')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active', 'is_superadmin')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Password', {'fields': ('password',)}),
    )
    
    # Inline Profile management within the User admin
    inlines = (ProfileInline,)

    ordering = ('-date_joined',)

    # To avoid errors with permissions
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# Customize Profile admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'city', 'headline', 'full_address')
    search_fields = ('user__email', 'country', 'city')
    list_filter = ('country', 'city')

admin.site.register(User, AccountAdmin)
admin.site.register(Profile, ProfileAdmin)
