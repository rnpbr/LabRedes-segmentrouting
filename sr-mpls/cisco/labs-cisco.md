> Uso interno — material em desenvolvimento.

# SR-MPLS | Pre requisitos para os labs Cisco IOS-XR

Padronização do ambiente necessário para executar os labs de SR-MPLS sobre Cisco IOS-XR com Containerlab. 

### Ambiente
Os laboratórios utilizam o Containerlab como orquestrador de topologias de rede. O Containerlab lê um arquivo YAML com a definição dos nodes e links, cria os containers Docker correspondentes e interliga as interfaces virtuais entre eles. 
 
A imagem utilizada é o Cisco XRd Control Plane, uma versão containerizada do IOS-XR desenvolvida pela Cisco para ambientes de laboratório e testes. Por ser um container nativo, o XRd inicializa em segundos e consome em torno de 1 GB de RAM por node, o que permite rodar topologias com vários nós em uma única máquina com recursos modestos.

| Recurso | XRd Control Plane |
|---|---|
| RAM por node | ~1 GB |
| Boot | ~30 segundos |
| KVM | Não é necessário |


---

## Instalação

### Docker

É necessário consultar o processo de instalação de acordo com o SO Linux que está sendo utilizado:

https://docs.docker.com/engine/install/

### Containerlab

Instalação do containerlab

```bash
curl -sL https://containerlab.dev/setup | sudo -E bash -s "all"
```

### Ajustes e imagem
Para executar os containers XRd, é necessário ajustar os parâmetros do inotify no Linux. Por padrão, esses limites são configurados de forma restritiva para evitar consumo excessivo de memória pelo monitoramento de arquivos do sistema.

```bash
# max_user_instances: Limite de programas (ou processos) que podem observar os arquivos.
sudo sysctl -w fs.inotify.max_user_instances=64000

# max_user_watches: Limite de arquivos e pastas totais sendo observados.
sudo sysctl -w fs.inotify.max_user_watches=64000
```

Download da imagem (uso exclusivamente interno)
```bash
# Baixar uma unica vez — fica disponivel para todos os labs
docker pull sbezverk/xrd-control-plane:7.10.2
```

---

## Referencias

- Docker: https://docs.docker.com/engine/install/
- Containerlab XRd: https://containerlab.dev/manual/kinds/xrd/
- Containerlab XRd Kind: https://containerlab.dev/manual/kinds/xrd/#__tabbed_1_1
- Cisco XRd Docs: https://xrdocs.io/virtual-routing/tutorials/2022-08-22-setting-up-host-environment-to-run-xrd#making-suggested-corrections-to-the-host-machine
