const socket = io();

    // Atualiza temperatura e umidade
    socket.on("atualizacao_dados", (dados) => {
        document.getElementById("temp").textContent =
            `${dados.temperatura.toFixed(1)} °C`;

        document.getElementById("umid").textContent =
            `${dados.umidade.toFixed(1)} %`;
    });

    // Adiciona logs ao painel
    socket.on("log_mensagem", (data) => {
        const logs = document.getElementById("logs");
        logs.textContent += data.mensagem + "\n";
        logs.scrollTop = logs.scrollHeight;
    });