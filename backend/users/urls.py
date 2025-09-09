from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import payment_views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('verify/', views.VerifyTokenView.as_view(), name='verify_token'),
    path('google/', views.GoogleOAuthView.as_view(), name='google_oauth'),
    path('apple/', views.AppleOAuthView.as_view(), name='apple_oauth'),
    path('profile/', views.CurrentUserProfileView.as_view(), name='current_profile'),
    path('subscription/', payment_views.subscription_page, name='subscription'),
    path('reset-free-visits/', payment_views.reset_free_visits, name='reset_free_visits'),
]
