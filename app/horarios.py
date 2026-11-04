"""Regras de horários do salão (fonte única para views, API e edição)."""
from datetime import date, time

from django.utils import timezone

from .models import Agendamento

ABERTURA = 8 * 60       # 08:00, em minutos desde a meia-noite
FECHAMENTO = 18 * 60    # 18:00
PASSO = 30              # intervalo entre inícios possíveis, em minutos


def _minutos(hora):
    return hora.hour * 60 + hora.minute


def _formatar(minutos):
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def interpretar_data(texto):
    try:
        return date.fromisoformat(texto)
    except (TypeError, ValueError):
        return None


def interpretar_hora(texto):
    try:
        return time.fromisoformat(texto)
    except (TypeError, ValueError):
        return None


def _periodos_ocupados(data, ignorar_id=None):
    """Períodos (início, fim) em minutos. Só cancelados liberam o horário."""
    agendamentos = (
        Agendamento.objects.filter(data=data)
        .exclude(status="cancelado")
        .select_related("servico")
    )
    if ignorar_id:
        agendamentos = agendamentos.exclude(id=ignorar_id)
    return [
        (_minutos(a.hora), _minutos(a.hora) + a.servico.duracao)
        for a in agendamentos
    ]


def _minimo_hoje(data):
    """Se a data é hoje, retorna o minuto atual; senão 0."""
    agora = timezone.localtime()
    if data == agora.date():
        return agora.hour * 60 + agora.minute
    return 0


def _livre(inicio, duracao, ocupados):
    fim = inicio + duracao
    return all(fim <= o_ini or inicio >= o_fim for o_ini, o_fim in ocupados)


def listar_horarios(data, servico, ignorar_id=None, bloquear_passado=True):
    """Todos os inícios possíveis do dia, cada um com 'disponivel' True/False."""
    ocupados = _periodos_ocupados(data, ignorar_id)
    minimo = _minimo_hoje(data) if bloquear_passado else 0
    resultado = []
    inicio = ABERTURA
    while inicio + servico.duracao <= FECHAMENTO:
        disponivel = inicio > minimo and _livre(inicio, servico.duracao, ocupados)
        resultado.append({"hora": _formatar(inicio), "disponivel": disponivel})
        inicio += PASSO
    return resultado


def validar(data, hora, servico, ignorar_id=None, bloquear_passado=True):
    """Retorna None se o horário é válido; senão, a mensagem de erro."""
    if data is None or hora is None:
        return "Data ou horário inválido."
    if bloquear_passado and data < timezone.localdate():
        return "Não é possível agendar em uma data passada."
    inicio = _minutos(hora)
    if hora.second or hora.microsecond or inicio % PASSO != 0:
        return "Horário inválido."
    if inicio < ABERTURA or inicio + servico.duracao > FECHAMENTO:
        return "Esse serviço não cabe no horário de funcionamento (08:00 às 18:00)."
    if bloquear_passado and inicio <= _minimo_hoje(data):
        return "Esse horário já passou."
    if not _livre(inicio, servico.duracao, _periodos_ocupados(data, ignorar_id)):
        return "Esse horário já está ocupado."
    return None
