from django.shortcuts import render,redirect
from.models import Cliente,Servico,Agendamento
from django.utils import timezone
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
    hoje=timezone.localdate()
    filtro=request.GET.get("filtro","hoje")
    agendamentos=Agendamento.objects.select_related("cliente","servico")
    if filtro=="hoje":
        agendamentos=agendamentos.filter(data=hoje)
    elif filtro=="proximos":
        agendamentos=agendamentos.filter(data__gte=hoje)
    elif filtro == "todos":
        pass
    else:
        filtro ="hoje"
        agendamentos=agendamentos.filter(data=hoje)
    agendamentos=agendamentos.order_by("data","hora")
    return render(request,"painel_cabeleireira.html",{"agendamentos":agendamentos,"filtro":filtro,"hoje":hoje})
    