from django.test import TestCase

# Create your tests here.
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Agendamento, Cliente, Servico


class HorariosTestCase(TestCase):
    def setUp(self):
        self.progressiva = Servico.objects.create(nome="Progressiva", duracao=120)
        self.corte = Servico.objects.create(nome="Corte", duracao=30)
        self.cliente = Cliente.objects.create(nome="Ana", telefone="83999999999")
        # Sempre uma data futura, para a regra de "dia passado" não interferir.
        self.data = (timezone.localdate() + timedelta(days=7)).isoformat()

        sessao = self.client.session
        sessao["cliente_id"] = self.cliente.id
        sessao.save()

    def horarios(self, servico, data=None):
        resposta = self.client.get(
            reverse("horarios_disponiveis"),
            {"servico": servico.id, "data": data or self.data},
        )
        self.assertEqual(resposta.status_code, 200)
        return {h["hora"]: h["disponivel"] for h in resposta.json()["horarios"]}

    def agendar(self, servico, hora, data=None):
        return self.client.post(
            reverse("agendamentos"),
            {"servico": servico.id, "data": data or self.data, "hora": hora},
        )

    def criar(self, servico, hora, status="agendado"):
        return Agendamento.objects.create(
            servico=servico, cliente=self.cliente,
            data=self.data, hora=hora, status=status,
        )

    # 1-3: grade respeita expediente e duração
    def test_servico_curto_tem_inicios_de_30_em_30_ate_17_30(self):
        h = self.horarios(self.corte)
        self.assertEqual(list(h)[0], "08:00")
        self.assertEqual(list(h)[-1], "17:30")
        self.assertEqual(len(h), 20)
        self.assertTrue(all(h.values()))

    def test_servico_longo_nao_ultrapassa_18h(self):
        h = self.horarios(self.progressiva)
        self.assertEqual(list(h)[-1], "16:00")  # 16:00 + 2h = 18:00
        self.assertNotIn("16:30", h)
        self.assertNotIn("17:30", h)

    # 4: agendar ocupa o período inteiro
    def test_agendamento_ocupa_periodo_da_duracao(self):
        self.agendar(self.progressiva, "08:00")
        self.assertEqual(Agendamento.objects.count(), 1)

        h = self.horarios(self.corte)
        for ocupado in ("08:00", "08:30", "09:00", "09:30"):
            self.assertFalse(h[ocupado], ocupado)
        self.assertTrue(h["10:00"])

    # 5: trocar serviço recalcula
    def test_trocar_servico_recalcula(self):
        self.criar(self.corte, "10:00")
        longo = self.horarios(self.progressiva)
        curto = self.horarios(self.corte)
        # progressiva às 09:00 invadiria o corte das 10:00; às 08:00 termina em 10:00 (ok)
        self.assertTrue(longo["08:00"])
        self.assertFalse(longo["08:30"])
        self.assertFalse(longo["09:00"])
        # corte às 09:30 termina às 10:00, então cabe
        self.assertTrue(curto["09:30"])
        self.assertFalse(curto["10:00"])
        self.assertTrue(curto["10:30"])

    # 6: trocar data recalcula
    def test_outra_data_nao_e_afetada(self):
        self.criar(self.corte, "10:00")
        outra = (timezone.localdate() + timedelta(days=8)).isoformat()
        self.assertTrue(self.horarios(self.corte, outra)["10:00"])

    # 7: cancelado libera, concluído continua bloqueando
    def test_cancelar_libera_horario(self):
        ag = self.criar(self.corte, "10:00")
        self.assertFalse(self.horarios(self.corte)["10:00"])
        ag.status = "cancelado"
        ag.save()
        self.assertTrue(self.horarios(self.corte)["10:00"])

    def test_concluido_continua_bloqueando(self):
        self.criar(self.corte, "10:00", status="concluido")
        self.assertFalse(self.horarios(self.corte)["10:00"])

    # 8: backend bloqueia envio manual
    def test_backend_bloqueia_horario_ocupado(self):
        self.criar(self.progressiva, "08:00")
        resposta = self.agendar(self.corte, "09:00")  # dentro das 08:00-10:00
        self.assertEqual(resposta.status_code, 200)  # volta ao formulário com erro
        self.assertContains(resposta, "já está ocupado")
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_backend_bloqueia_horario_invalido(self):
        for hora in ("08:15", "07:30", "18:00", "abc", ""):
            self.agendar(self.corte, hora)
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_backend_bloqueia_servico_invalido_ou_ausente(self):
        for servico in ("999", "abc", ""):
            self.client.post(reverse("agendamentos"),
                             {"servico": servico, "data": self.data, "hora": "10:00"})
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_backend_bloqueia_data_passada(self):
        ontem = (timezone.localdate() - timedelta(days=1)).isoformat()
        self.agendar(self.corte, "10:00", data=ontem)
        self.assertEqual(Agendamento.objects.count(), 0)

    # 9: expediente
    def test_backend_bloqueia_servico_que_passa_das_18h(self):
        self.agendar(self.progressiva, "16:30")
        self.agendar(self.progressiva, "17:00")
        self.agendar(self.corte, "18:00")
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_aceita_ultimo_horario_que_cabe(self):
        self.agendar(self.progressiva, "16:00")  # termina exatamente às 18:00
        self.assertEqual(Agendamento.objects.count(), 1)
        Agendamento.objects.all().delete()
        self.agendar(self.corte, "17:30")        # termina exatamente às 18:00
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_agendamento_valido_redireciona(self):
        resposta = self.agendar(self.corte, "10:00")
        self.assertRedirects(resposta, reverse("meus_agendamentos"))

    # endpoint
    def test_endpoint_rejeita_parametros_ruins(self):
        url = reverse("horarios_disponiveis")
        self.assertEqual(self.client.get(url).status_code, 400)
        self.assertEqual(self.client.get(url, {"servico": "x", "data": self.data}).status_code, 400)
        self.assertEqual(self.client.get(url, {"servico": self.corte.id, "data": "2026-13-45"}).status_code, 400)

    def test_data_passada_nao_devolve_horarios(self):
        ontem = (timezone.localdate() - timedelta(days=1)).isoformat()
        resposta = self.client.get(
            reverse("horarios_disponiveis"),
            {"servico": self.corte.id, "data": ontem},
        )
        self.assertEqual(resposta.json()["horarios"], [])
