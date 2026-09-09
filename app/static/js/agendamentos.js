const servicos = document.querySelectorAll(".servico");

servicos.forEach(function(servico) {

    servico.addEventListener("click", function() {

        servicos.forEach(function(outroServico) {
            outroServico.classList.remove("selecionado");
        });

        servico.classList.add("selecionado");

        const idServico = servico.dataset.id;

        console.log("Serviço escolhido:", idServico);

    });

});
const dias = document.querySelectorAll(".dias button");
dias.forEach(function(dia) {
    dia.addEventListener("click", function() {
        if (dia.classList.contains("selecionado")) {
            dia.classList.remove("selecionado");
            console.log("Dia desmarcado:", dia.textContent);
        } else {
            dias.forEach(function(outroDia) {
                outroDia.classList.remove("selecionado");
            });
            dia.classList.add("selecionado");
            console.log("Dia escolhido:", dia.textContent);
        }
    });
});