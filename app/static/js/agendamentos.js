console.log("JS carregou!");
let servicoSelecionado = null;
let dataSelecionada = null;
let horaSelecionada = null;

const inputServico = document.querySelector("#servico");
const inputData = document.querySelector("#data");
const inputHora = document.querySelector("#hora");

// ================================
// SELEÇÃO DE SERVIÇOS
// ================================

const servicos = document.querySelectorAll(".servico");

servicos.forEach(function (servico) {
    servico.addEventListener("click", function () {
        servicos.forEach(function (outroServico) {
            outroServico.classList.remove("selecionado");
        });

        servico.classList.add("selecionado");

        servicoSelecionado = servico.dataset.id;
        inputServico.value = servicoSelecionado;

        console.log("Serviço escolhido:", servicoSelecionado);
        carregarHorarios();
    });
});

// ================================
// CALENDÁRIO
// ================================

const calendarioDias = document.querySelector(".dias");
const tituloMes = document.querySelector("#mes-ano");
const botaoAnterior = document.querySelector(".mes-anterior");
const botaoProximo = document.querySelector(".mes-proximo");

let mesAtual = new Date();

mesAtual = new Date(
    mesAtual.getFullYear(),
    mesAtual.getMonth(),
    1
);

function renderizarCalendario() {
    const ano = mesAtual.getFullYear();
    const mes = mesAtual.getMonth();

    tituloMes.textContent = mesAtual.toLocaleDateString(
        "pt-BR",
        {
            month: "long",
            year: "numeric"
        }
    );

    // Dia da semana do primeiro dia do mês:
    // 0 = domingo, 1 = segunda... 6 = sábado.
    const primeiroDia = new Date(ano, mes, 1).getDay();

    // Quantidade de dias do mês atual.
    const totalDias = new Date(ano, mes + 1, 0).getDate();

    // Apaga os dias do mês que estava sendo exibido.
    calendarioDias.innerHTML = "";

    // Espaços para alinhar o primeiro dia
    // com o dia da semana correto.
    for (let i = 0; i < primeiroDia; i++) {
        const vazio = document.createElement("span");
        vazio.classList.add("dia-vazio");

        calendarioDias.appendChild(vazio);
    }

    // Gera os botões de 1 até o último dia.
    for (let dia = 1; dia <= totalDias; dia++) {
        const botao = document.createElement("button");

        botao.type = "button";
        botao.textContent = dia;

        const mesFormatado = String(mes + 1).padStart(2, "0");
        const diaFormatado = String(dia).padStart(2, "0");

        botao.dataset.data =
            `${ano}-${mesFormatado}-${diaFormatado}`;

        // Dias anteriores a hoje não podem ser agendados.
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);
        if (new Date(ano, mes, dia) < hoje) {
            botao.disabled = true;
        }

        botao.addEventListener("click", function () {
            calendarioDias
                .querySelectorAll("button")
                .forEach(function (outroDia) {
                    outroDia.classList.remove("selecionado");
                });

            botao.classList.add("selecionado");

            dataSelecionada = botao.dataset.data;
            inputData.value = dataSelecionada;

            console.log("Data escolhida:", dataSelecionada);
            carregarHorarios();
        });

        calendarioDias.appendChild(botao);
    }
}

// Mês anterior.
botaoAnterior.addEventListener("click", function () {
    mesAtual.setMonth(mesAtual.getMonth() - 1);

    dataSelecionada = null;
    inputData.value = "";
    carregarHorarios();

    renderizarCalendario();
});

// Próximo mês.
botaoProximo.addEventListener("click", function () {
    mesAtual.setMonth(mesAtual.getMonth() + 1);

    dataSelecionada = null;
    inputData.value = "";
    carregarHorarios();

    renderizarCalendario();
});

// Exibe o calendário inicial.
renderizarCalendario();

// ================================
// HORÁRIOS (calculados pelo Django)
// ================================

const gradeHorarios = document.querySelector(".horarios-grid");
const urlHorarios = gradeHorarios.dataset.url;

// Evita que uma resposta antiga sobrescreva uma mais nova.
let numeroDaBusca = 0;

function mostrarAviso(texto) {
    gradeHorarios.innerHTML = "";

    const aviso = document.createElement("p");
    aviso.className = "horarios-aviso";
    aviso.textContent = texto;

    gradeHorarios.appendChild(aviso);
}

function carregarHorarios() {
    // Trocar serviço ou data sempre apaga o horário escolhido.
    horaSelecionada = null;
    inputHora.value = "";

    if (!servicoSelecionado || !dataSelecionada) {
        mostrarAviso("Selecione um serviço e uma data.");
        return;
    }

    const busca = ++numeroDaBusca;
    mostrarAviso("Carregando horários...");

    const parametros = new URLSearchParams({
        servico: servicoSelecionado,
        data: dataSelecionada
    });

    fetch(`${urlHorarios}?${parametros}`)
        .then(function (resposta) {
            if (!resposta.ok) {
                throw new Error("Resposta " + resposta.status);
            }
            return resposta.json();
        })
        .then(function (dados) {
            if (busca !== numeroDaBusca) {
                return;
            }
            renderizarHorarios(dados);
        })
        .catch(function (erro) {
            console.error("Erro ao buscar horários:", erro);

            if (busca === numeroDaBusca) {
                mostrarAviso("Não foi possível carregar os horários. Tente novamente.");
            }
        });
}

function renderizarHorarios(dados) {
    gradeHorarios.innerHTML = "";

    if (!dados.horarios.length) {
        mostrarAviso(dados.mensagem || "Não há horários para este serviço.");
        return;
    }

    let temDisponivel = false;

    dados.horarios.forEach(function (item) {
        const botao = document.createElement("button");

        botao.type = "button";
        botao.textContent = item.hora;
        botao.dataset.hora = item.hora;

        if (item.disponivel) {
            temDisponivel = true;
        } else {
            botao.classList.add("indisponivel");
            botao.disabled = true;
        }

        gradeHorarios.appendChild(botao);
    });

    if (!temDisponivel) {
        const aviso = document.createElement("p");
        aviso.className = "horarios-aviso";
        aviso.textContent = "Não há horários livres neste dia para este serviço.";
        gradeHorarios.appendChild(aviso);
    }
}

// Os botões são criados dinamicamente, então o clique é tratado na grade.
gradeHorarios.addEventListener("click", function (evento) {
    const botao = evento.target.closest("button[data-hora]");

    if (!botao || botao.disabled) {
        return;
    }

    gradeHorarios
        .querySelectorAll("button")
        .forEach(function (outroHorario) {
            outroHorario.classList.remove("selecionado");
        });

    botao.classList.add("selecionado");

    horaSelecionada = botao.dataset.hora;
    inputHora.value = horaSelecionada;

    console.log("Horário escolhido:", horaSelecionada);
});

// Não deixa enviar o formulário sem serviço, data e horário.
document.querySelector("#form-agendamento").addEventListener("submit", function (evento) {
    if (!inputServico.value || !inputData.value || !inputHora.value) {
        evento.preventDefault();
        alert("Escolha o serviço, a data e o horário.");
    }
});

// ================================
// SELEÇÃO INICIAL
// ================================
// Ao abrir a página, já deixa o primeiro serviço e a data de hoje
// selecionados (amanhã, se o expediente de hoje já acabou), para
// os horários aparecerem sem precisar clicar. Dá para trocar depois.

(function selecionarPadrao() {
    const agora = new Date();
    const inicial = new Date(
        agora.getFullYear(),
        agora.getMonth(),
        agora.getDate() + (agora.getHours() >= 18 ? 1 : 0)
    );

    mesAtual = new Date(inicial.getFullYear(), inicial.getMonth(), 1);
    renderizarCalendario();

    const iso =
        `${inicial.getFullYear()}-` +
        `${String(inicial.getMonth() + 1).padStart(2, "0")}-` +
        `${String(inicial.getDate()).padStart(2, "0")}`;

    const botaoDia = calendarioDias.querySelector(`button[data-data="${iso}"]`);

    if (servicos.length > 0) {
        servicos[0].click();
    }

    if (botaoDia && !botaoDia.disabled) {
        botaoDia.click();
    }
})();
