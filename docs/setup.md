# Preparação do ambiente

Requisitos comuns para executar os laboratórios Containerlab deste projeto. A
instalação da imagem e os ajustes próprios de cada fabricante ficam no setup da
plataforma; para os labs atuais, consulte o [setup do Cisco XRd](../labs/cisco/setup.md).

## Requisitos

- Linux bare-metal ou uma VM com virtualização aninhada;
- Docker Engine;
- Containerlab;
- recursos de CPU e memória compatíveis com a quantidade de nós do cenário.

## Docker e Containerlab

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # encerre a sessão e entre novamente
bash -c "$(curl -sL https://get.containerlab.dev)"
```

Confira a instalação:

```bash
docker --version
containerlab version
```

## Obter o projeto

```bash
git clone https://github.com/rnpbr/LabRedes-segmentrouting.git
cd LabRedes-segmentrouting
```

Cada laboratório é autocontido. Entre no diretório escolhido e use a topologia
que está ao lado das configurações:

```bash
cd labs/<fabricante>/<data-plane>/<categoria>/<lab>
sudo clab deploy -t lab.clab.yml
```

Para encerrar o cenário:

```bash
sudo clab destroy -t lab.clab.yml --cleanup
```

O `--cleanup` remove o estado gerado pelo Containerlab dentro do diretório do
lab. Consulte o roteiro do cenário antes de usá-lo se quiser preservar mudanças
feitas durante a execução.
