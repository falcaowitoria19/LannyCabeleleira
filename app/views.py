from django.shortcuts import render,redirect
from.models import Cliente,Servico,Agendamento
# Create your views here.

def inicio(request):
    if request.method =="POST":
        nome=request.POST["nome"]
        telefone=request.POST["telefone"]
        Cliente.objects.create(nome=nome,telefone=telefone)
        return redirect("agendamentos")
    return render(request,'inicio.html')
def cliente(request):
    return render(request,'app/cliente.html')
def agendamentos(request):
    return render(request,'agendamentos.html')
def meus_agendamentos(request):
    return render(request,'meus_agendamentos.html')