from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from.models import Cliente,Servico,Agendamento
from django.utils import timezone
from datetime import date, time
import calendar as calendario_python
# Create your views here.
#necessario para o login cabeleleira
from django.contrib.auth import authenticate,login as auth_login,get_user_model
from django.contrib.auth.decorators import login_required
from functools import wraps

def inicio(request):
    if request.method =="POST":
        nome=request.POST["nome"]
        telefone=request.POST["telefone"]
        cliente=Cliente.objects.create(nome=nome,telefone=telefone)
        request.session['cliente_id']=cliente.id
        return redirect("agendamentos")
    return render(request,'inicio.html')
def cliente(request):
    return render(request,'app/cliente.html')
def agendamentos(request):
    servicos=Servico.objects.all()
    if request.method == "POST":
        servico_id=request.POST["servico"]
        data= request.POST["data"]
        hora=request.POST["hora"]

        cliente_id=request.session["cliente_id"]
        Agendamento.objects.create(
            servico_id=servico_id,
            cliente_id=cliente_id,
            data=data,
            hora=hora
        )

    return render(request,'agendamentos.html',{"servicos":servicos})

def meus_agendamentos(request):
    cliente_id=request.session["cliente_id"]
    agendamentos=Agendamento.objects.filter(
        cliente_id=cliente_id
    )
    return render(request,'meus_agendamentos.html',{
        "agendamentos":agendamentos
    })

def login_cabeleireira(request):
    #Se a cabeleireira já estiver logada, vai direto ao painel.
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("painel_cabeleireira")
    
    erro=None

    if request.method=="POST":
        email=request.POST.get("email","").strip()
        senha=request.POST.get("senha","")
        Usuario=get_user_model()
        usuarios=Usuario.objects.filter(email__iexact=email)
        # O e-mail precisa corresponder a uma única conta.
        if usuarios.count()==1:
            usuario_encontrado=usuarios.first()
            usuario=authenticate(request,username=usuario_encontrado.get_username(),password=senha)
            if usuario is not None and usuario.is_staff:
                auth_login(request,usuario)
                return redirect("painel_cabeleireira")
        erro="E-mail ou senha invalidos, ou conta sem permissão"
    return render(request,"login_cabeleireira.html",{"erro":erro})

def somente_cabeleireira(view):
    @wraps(view)
    @login_required(login_url="login_cabeleireira")
    def verificar_acesso(request,*args,**kwargs):
        if not request.user.is_staff:
            return redirect("login_cabeleireira")
        return view(request, *args, **kwargs)
    return verificar_acesso

@somente_cabeleireira
def painel_cabeleireira(request):
    hoje = timezone.localdate()
    # Descobre qual dia foi selecionado no calendário.
    dia_selecionado = None
    dia_parametro = request.GET.get("dia")
    if dia_parametro:
        try:
            dia_selecionado = date.fromisoformat(dia_parametro)
        except ValueError:
            dia_selecionado = None
    # Define o mês que será exibido.
    try:
        mes = int(request.GET.get("mes", hoje.month))
        ano = int(request.GET.get("ano", hoje.year))

        if not 1 <= mes <= 12 or not 1 <= ano <= 9999:
            raise ValueError

    except (ValueError, TypeError):
        mes = hoje.month
        ano = hoje.year

    # Se um dia foi selecionado sem mês explícito,
    # abre o mês desse dia.
    if dia_selecionado and "mes" not in request.GET:
        mes = dia_selecionado.month
        ano = dia_selecionado.year

    # Monta o calendário mensal.
    primeiro_dia = date(ano, mes, 1)

    if mes == 12:
        proximo_mes = date(ano + 1, 1, 1) if ano < 9999 else None
    else:
        proximo_mes = date(ano, mes + 1, 1)

    calendario = calendario_python.Calendar(firstweekday=6).monthdatescalendar(ano, mes)
    # Busca os agendamentos do mês para marcar os dias.
    agendamentos_mes = Agendamento.objects.filter(data__gte=primeiro_dia)
    if proximo_mes:
        agendamentos_mes = agendamentos_mes.filter(data__lt=proximo_mes)

    marcadores = {}

    for data_agendamento, status in agendamentos_mes.values_list(
        "data", "status"
    ):
        if data_agendamento not in marcadores:
            marcadores[data_agendamento] = set()

        marcadores[data_agendamento].add(status)

    semanas = []

    for semana in calendario:
        dias = []

        for dia in semana:
            dias.append({
                "data": dia,
                "numero": dia.day,
                "mes_atual": dia.month == mes,
                "tem_agendamento": dia in marcadores,
                "status_agendamentos": sorted(
                    marcadores.get(dia, set())
                ),
                "selecionado": dia == dia_selecionado,
                "hoje": dia == hoje,
            })

        semanas.append(dias)

    # Filtros da lista de clientes.
    filtro = request.GET.get("filtro", "hoje")

    agendamentos = Agendamento.objects.select_related(
        "cliente", "servico"
    )

    if dia_selecionado:
        agendamentos = agendamentos.filter(
            data=dia_selecionado
        )
        filtro = "dia"

    elif filtro == "hoje":
        agendamentos = agendamentos.filter(data=hoje)

    elif filtro == "proximos":
        agendamentos = agendamentos.filter(data__gte=hoje)

    elif filtro != "todos":
        filtro = "hoje"
        agendamentos = agendamentos.filter(data=hoje)

    agendamentos = agendamentos.order_by("data", "hora")

    # Dados para os cards de resumo.
    total_hoje = Agendamento.objects.filter(
        data=hoje
    ).exclude(status="cancelado").count()

    total_agendados = Agendamento.objects.filter(
        status="agendado",
        data__gte=hoje,
    ).count()

    total_concluidos = Agendamento.objects.filter(
        status="concluido"
    ).count()

    nomes_meses = [
        "Janeiro", "Fevereiro", "Março", "Abril",
        "Maio", "Junho", "Julho", "Agosto",
        "Setembro", "Outubro", "Novembro", "Dezembro",
    ]

    mes_anterior = (
        date(ano - 1, 12, 1)
        if mes == 1 and ano > 1
        else date(ano, mes - 1, 1) if mes > 1 else None
    )

    mes_seguinte = (
        date(ano + 1, 1, 1)
        if mes == 12 and ano < 9999
        else date(ano, mes + 1, 1) if mes < 12 else None
    )
    nomes_dias=["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    return render(
        request,
        "painel_cabeleireira.html",
        {
            "agendamentos": agendamentos,
            "filtro": filtro,
            "hoje": hoje,
            "semanas": semanas,
            "mes": mes,
            "ano": ano,
            "nomes_dias": nomes_dias,
            "nome_mes": nomes_meses[mes - 1],
            "mes_anterior": mes_anterior,
            "mes_seguinte": mes_seguinte,
            "dia_selecionado": dia_selecionado,
            "total_hoje": total_hoje,
            "total_agendados": total_agendados,
            "total_concluidos": total_concluidos,
        },
    )
@somente_cabeleireira
@require_POST
def cancelar_agendamento(request,agendamento_id):
        agendamento=get_object_or_404(
            Agendamento,id=agendamento_id
        )
        agendamento.status="cancelado"
        agendamento.save()
        return redirect("painel_cabeleireira")

@somente_cabeleireira
@require_POST
def concluir_agendamento(request,agendamento_id):
    agendamento=get_object_or_404(Agendamento,id=agendamento_id)
    if agendamento.status !="cancelado":
        agendamento.status="concluido"
        agendamento.save()
    return redirect("painel_cabeleireira")

@somente_cabeleireira
def editar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento,id=agendamento_id)
    servicos = Servico.objects.all()
    if request.method == "POST":
        servico_id = request.POST.get("servico")
        data = request.POST.get("data")
        hora = request.POST.get("hora")
        try:
            servico = get_object_or_404(Servico, id=servico_id)
            nova_data = date.fromisoformat(data)
            novo_horario = time.fromisoformat(hora)
        except (ValueError, TypeError):
            return render(
                request,"editar_agendamento.html",
                {
                    "agendamento": agendamento,
                    "servicos": servicos,
                    "erro": "Data, horário ou serviço inválido.",
                }
            )
        conflito = Agendamento.objects.filter( data=nova_data, hora=novo_horario,status="agendado").exclude(id=agendamento.id).exists()
        if conflito:
            return render(request,"editar_agendamento.html",
                {
                    "agendamento": agendamento,
                    "servicos": servicos,
                    "erro": "Esse horário já está ocupado.",
                }
            )
        agendamento.servico = servico
        agendamento.data = nova_data
        agendamento.hora = novo_horario
        agendamento.save()
        return redirect("painel_cabeleireira")
    return render(request,"editar_agendamento.html",
        {
            "agendamento": agendamento,
            "servicos": servicos,
        }
    )