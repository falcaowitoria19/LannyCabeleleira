from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
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

        agendamento_existente = Agendamento.objects.filter(
            data=data,
            hora=hora
        ).exists()

        if agendamento_existente:
            return Response(
                {'erro': 'Esse horário já está ocupado.'},
                status=400
            )

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

        data = request.query_params.get('data')

        if not data:
            return Response(
                {'erro': 'Informe a data.'},
                status=400
            )

        agendamentos = Agendamento.objects.filter(
            data=data,
            status='agendado'
        )

        horarios_ocupados = [
            agendamento.hora.strftime('%H:%M')
            for agendamento in agendamentos
        ]

        horarios = [
            '09:00',
            '10:00',
            '11:00',
            '12:00',
            '13:00',
            '14:00',
            '15:00',
            '16:00',
            '17:00',
            '18:00'
        ]

        horarios_disponiveis = [
            horario
            for horario in horarios
            if horario not in horarios_ocupados
        ]

        return Response({
            'data': data,
            'horarios_disponiveis': horarios_disponiveis
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