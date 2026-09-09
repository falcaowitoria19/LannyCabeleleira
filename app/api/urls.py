from rest_framework.routers import DefaultRouter
from .viewsets import ClienteViewSet,ServicoViewSet,AgendamentoViewSet

router=DefaultRouter()

router.register("cliente",ClienteViewSet)
router.register("servico",ServicoViewSet)
router.register("agendamento",AgendamentoViewSet)
urlpatterns=router.urls