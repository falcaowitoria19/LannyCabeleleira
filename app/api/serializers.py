from rest_framework import serializers
from ..models import Cliente,Servico,Agendamento
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cliente
        fields=['id','nome','telefone']

class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Servico
        fields=['id','nome','duracao']

class AgendamentoSerializer(serializers.ModelSerializer):

    servico_nome = serializers.CharField(source='servico.nome',read_only=True)
    class Meta:
        model = Agendamento
        fields = [
            'id',
            'servico',
            'servico_nome',
            'cliente',
            'data',
            'hora',
            'status'
        ]
        read_only_fields = ['status']
class MeusAgendamentosSerializer(serializers.ModelSerializer):

    servico = serializers.CharField(
        source='servico.nome',
        read_only=True
    )

    class Meta:
        model = Agendamento
        fields = [
            'id',
            'servico',
            'data',
            'hora',
            'status'
        ]