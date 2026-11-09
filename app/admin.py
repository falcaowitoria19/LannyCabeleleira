from django.contrib import admin
from .models import Cliente,Servico,Agendamento

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display=("nome","duracao","preco","preco_a_partir")
    #permite pesquisar serviços pelo nome
    search_fields=("nome",)
    #organiza os servicos alfabeticamente
    ordering=("nome",)

admin.site.register(Cliente)
admin.site.register(Agendamento)

# Register your models here.
