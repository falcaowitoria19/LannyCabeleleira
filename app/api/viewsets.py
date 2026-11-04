from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from .. import horarios
from ..models import Cliente,Servico,Agendamento
from .serializers import ClienteSerializer,ServicoSerializer,AgendamentoSerializer,MeusAgendamentosSerializer
class ClienteViewSet(viewsets.ModelViewSet):
    queryset=Cliente.objects.all()
    serializer_class=ClienteSerializer

class ServicoViewSet(viewsets.ModelViewSet):
    queryset=Servico.objects.all()
    serializer_class=ServicoSerializer

class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer

    def create(self, request):

        data = request.data.get('data')
        hora = request.data.get('hora')
        cliente_id = request.data.get('cliente')
        servico_id = request.data.get('servico')

        cliente = Cliente.objects.filter(id=cliente_id).first()

        if not cliente:
            return Response(
                {'erro': 'Cliente não encontrado.'},
                status=404
            )

        servico = Servico.objects.filter(id=servico_id).first()

        if not servico:
            return Response(
                {'erro': 'Serviço não encontrado.'},
                status=404
            )

        erro = horarios.validar(
            horarios.interpretar_data(data),
            horarios.interpretar_hora(hora),
            servico
        )

        if erro:
            return Response({'erro': erro}, status=400)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(status='agendado')

            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )

    @action(detail=False, methods=['GET'])
    def horarios_disponiveis(self, request):

        data = horarios.interpretar_data(request.query_params.get('data'))
        servico_id = request.query_params.get('servico', '')
        servico = (
            Servico.objects.filter(id=servico_id).first()
            if servico_id.isdigit() else None
        )

        if data is None or servico is None:
            return Response(
                {'erro': 'Informe a data (AAAA-MM-DD) e o serviço.'},
                status=400
            )

        return Response({
            'data': data.isoformat(),
            'horarios_disponiveis': [
                h['hora'] for h in horarios.listar_horarios(data, servico)
                if h['disponivel']
            ]
        })

    @action(detail=False, methods=['GET'])
    def por_data(self, request):

        data = request.query_params.get('data')

        if not data:
            return Response(
                {'erro': 'Informe a data.'},
                status=400
            )

        agendamentos = Agendamento.objects.filter(
            data=data
        )

        serializer = self.get_serializer(
            agendamentos,
            many=True
        )

        return Response(serializer.data)
    @action(detail=True, methods=['PATCH'])
    def cancelar(self, request, pk=None):

        agendamento = self.get_object()

        agendamento.status = 'cancelado'
        agendamento.save()

        serializer = self.get_serializer(agendamento)

        return Response(serializer.data)
    @action(detail=False, methods=['GET'])
    def meus_agendamentos(self, request):

        cliente_id = request.query_params.get('cliente')

        if not cliente_id:
            return Response(
                {'erro': 'Informe o cliente.'},
                status=400
            )

        agendamentos = Agendamento.objects.filter(
            cliente_id=cliente_id
        )

        serializer = MeusAgendamentosSerializer(
            agendamentos,
            many=True
        )

        return Response(serializer.data)