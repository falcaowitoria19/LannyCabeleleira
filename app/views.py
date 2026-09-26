from django.shortcuts import render,redirect
from.models import Cliente,Servico,Agendamento
# Create your views here.

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
    return render(request,'meus_agendamentos.html')