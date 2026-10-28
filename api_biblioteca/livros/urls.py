"""Rotas da app `livros`, geradas pelo router do DRF."""

from rest_framework.routers import DefaultRouter

from .views import LivroViewSet

router = DefaultRouter()
router.register("livros", LivroViewSet, basename="livro")

urlpatterns = router.urls
