from django.urls import path, include
from customer_application import views
from .return_plan import urls
from .views import NotificationAPIView

urlpatterns = [
    path('login/send-code/', views.send_login_code),
    path('login/', views.customer_login),
    path('businessmans/', views.BusinessmansList.as_view()),
    path('businessmans/<str:page_businessman_id>/', views.BusinessmanRetrieveAPIView.as_view()),
    path('notif/', NotificationAPIView.as_view()),
    path('plan/', include(urls)),
]
