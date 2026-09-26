let servicoSelecionado = null;
let dataSelecionada = null;
let horaSelecionada = null;

const servicos = document.querySelectorAll(".servico");

servicos.forEach(function(servico) {

    servico.addEventListener("click", function() {

        servicos.forEach(function(outroServico) {
            outroServico.classList.remove("selecionado");
        });

        servico.classList.add("selecionado");

        const idServico = servico.dataset.id;

        servicoSelecionado = idServico;

        console.log("Serviço escolhido:", servicoSelecionado);
    });

});


const dias = document.querySelectorAll(".dias button");

dias.forEach(function(dia) {

    dia.addEventListener("click", function() {

        if (dia.classList.contains("selecionado")) {

            dia.classList.remove("selecionado");

            dataSelecionada = null;

            console.log("Dia desmarcado:", dia.textContent);

        } else {

            dias.forEach(function(outroDia) {
                outroDia.classList.remove("selecionado");
            });

            dia.classList.add("selecionado");

            dataSelecionada = dia.dataset.data;

            console.log("Dia escolhido:", dataSelecionada);
        }

    });

});
const horarios = document.querySelectorAll(".horarios-grid button:not(.indisponivel)");

horarios.forEach(function(horario) {

    horario.addEventListener("click", function() {

        horarios.forEach(function(outroHorario) {
            outroHorario.classList.remove("selecionado");
        });

        horario.classList.add("selecionado");

        horaSelecionada = horario.dataset.hora;

        console.log("Horário escolhido:", horaSelecionada);
    });

});