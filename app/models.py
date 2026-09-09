from django.db import models

# Create your models here.
class Cliente(models.Model):
    nome=models.CharField(max_length=70)
    telefone=models.CharField(max_length=15)
class Servico(models.Model):
    nome=models.CharField(max_length=50)
    duracao=models.PositiveIntegerField()
class Agendamento(models.Model):
    servico=models.ForeignKey(Servico,on_delete=models.CASCADE,related_name="agendamentos")
    cliente=models.ForeignKey(Cliente,on_delete=models.CASCADE,related_name="agendamentos")
    data=models.DateField()
    hora=models.TimeField()
    status = models.CharField(max_length=20,default="agendado")
    
