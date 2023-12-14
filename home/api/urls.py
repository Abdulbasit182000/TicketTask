from app.views import (CommentViewSet, DocumentViewSet, ProjectViewset,
                       RegisterAPI, TaskViewSet)
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

router = DefaultRouter()
router.register(r"projects", ProjectViewset, basename="project")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"comments", CommentViewSet, basename="comment")


urlpatterns = [
    path("", include(router.urls)),
    # Register API
    path("register/", RegisterAPI.as_view()),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # DRF Spectacular URLs
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"),
        name="redoc"
    ),
]
