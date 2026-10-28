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
        });

        calendarioDias.appendChild(botao);
    }
}

// Mês anterior.
botaoAnterior.addEventListener("click", function () {
    mesAtual.setMonth(mesAtual.getMonth() - 1);

    dataSelecionada = null;
    inputData.value = "";

    renderizarCalendario();
});

// Próximo mês.
botaoProximo.addEventListener("click", function () {
    mesAtual.setMonth(mesAtual.getMonth() + 1);

    dataSelecionada = null;
    inputData.value = "";

    renderizarCalendario();
});

// Exibe o calendário inicial.
renderizarCalendario();

// ================================
// SELEÇÃO DE HORÁRIOS
// ================================

const horarios = document.querySelectorAll(
    ".horarios-grid button:not(.indisponivel)"
);

horarios.forEach(function (horario) {
    horario.addEventListener("click", function () {
        horarios.forEach(function (outroHorario) {
            outroHorario.classList.remove("selecionado");
        });

        horario.classList.add("selecionado");

        horaSelecionada = horario.dataset.hora;
        inputHora.value = horaSelecionada;

        console.log("Horário escolhido:", horaSelecionada);
    });
});
