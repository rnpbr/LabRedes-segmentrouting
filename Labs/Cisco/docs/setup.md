# Ambiente

O que precisa estar instalado antes do primeiro `clab deploy`. Conceitos ficam em [`base.md`](./base.md).

## Requisitos

- Linux, bare-metal ou VM com virtualização aninhada.
- Docker Engine.
- Containerlab.
- RAM: cerca de 1,5 GB por nó. Os labs têm de 4 a 6 nós, então reserve de 6 a 12 GB.
- Limites de `inotify` aumentados (ver abaixo).

## Docker e Containerlab

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # relogar depois
bash -c "$(curl -sL https://get.containerlab.dev)"
```

Conferir:

```bash
docker --version
containerlab version
```

## Imagem XRd

A imagem não está em registry público. Baixe o tarball em [software.cisco.com](https://software.cisco.com) com login CCO, procurando por "IOS XRd Control-Plane Container".

```bash
docker load -i xrd-control-plane-x64-7.10.2.tgz
docker images | grep xrd
```

O `docker load` já cria a tag usada nos labs: `ios-xr/xrd-control-plane:7.10.2`. Se vier diferente:

```bash
docker tag <tag-original> ios-xr/xrd-control-plane:7.10.2
```

## Limites de inotify

O XRd consome muitos watches. Sem isso os nós travam no boot:

```bash
sudo sysctl -w fs.inotify.max_user_instances=524288
sudo sysctl -w fs.inotify.max_user_watches=524288
```

Para deixar permanente, grave em `/etc/sysctl.d/99-xrd.conf`.

## Subir um lab

Repositório: <https://github.com/rnpbr/LabRedes-segmentrouting.git>

Clone uma vez, depois copie o `.clab.yml` e a pasta `configs/` do lab desejado para um diretório de trabalho:

```bash
git clone https://github.com/rnpbr/LabRedes-segmentrouting.git
cd LabRedes-segmentrouting

mkdir -p ~/labs/ti-lfa/zero-segment
cp IaC/Clabs/Cisco/ti-lfa/zero-segment.clab.yml ~/labs/ti-lfa/zero-segment/
cp -r Labs/Cisco/SR-MPLS/TI-LFA/00-zero-segment/configs ~/labs/ti-lfa/zero-segment/

cd ~/labs/ti-lfa/zero-segment
sudo clab deploy -t zero-segment.clab.yml
```

Estrutura final antes do deploy:

```text
zero-segment/
├── zero-segment.clab.yml
└── configs/
    ├── sp.cfg
    ├── df.cfg
    ├── mg.cfg
    └── ba.cfg
```

O padrão é sempre o mesmo, trocando categoria e nome do lab:

```bash
mkdir -p ~/labs/<categoria>/<lab>
cp IaC/Clabs/Cisco/<categoria>/<lab>.clab.yml ~/labs/<categoria>/<lab>/
cp -r Labs/Cisco/SR-MPLS/<CATEGORIA>/<lab>/configs ~/labs/<categoria>/<lab>/

cd ~/labs/<categoria>/<lab>
sudo clab deploy -t <lab>.clab.yml
```

`<categoria>` é `ti-lfa` ou `sr-te` (minúsculo, é a pasta em `IaC/Clabs/Cisco/`). `<CATEGORIA>` é `TI-LFA` ou `SR-TE` (maiúsculo, é a pasta em `Labs/Cisco/SR-MPLS/`). Cada lab documenta os nomes exatos na própria seção de Deploy.

Acesso: `ssh clab@<ip>`, senha `clab@123`. Cada lab documenta os IPs. Alternativa sem SSH:

```bash
sudo docker exec -it clab-tilfa-zero-segment-sp /pkg/bin/xr_cli.sh
```

Derrubar:

```bash
sudo clab destroy -t zero-segment.clab.yml --cleanup
```

O `--cleanup` apaga o diretório do lab. Sem ele, a config gravada pelo XRd fica guardada e é reusada no próximo deploy.

> Os `.clab.yml` trazem `enforce-startup-config: true`, então todo deploy reaplica o `.cfg`. Se você quiser preservar mudanças feitas à mão entre um deploy e outro, remova essa linha.



## Formato dos arquivos `.cfg`

São startup-configs completos de IOS-XR, não trechos para colar no terminal:

- não têm `conf t` nem `commit`, e terminam com `end`;
- incluem o bloco base do kind `cisco_xrd`: hostname, usuário `clab`, gRPC, netconf, SSH e rota default de gerência;
- usam `{{ .ShortName }}` e `{{ .MgmtIPv4Gateway }}`, que o containerlab resolve no deploy.

Para criar um lab novo, copie um `.cfg` existente e edite. Um arquivo só com a configuração de roteamento sobe um nó sem hostname, sem usuário e sem SSH.

Para aplicar algo à mão em um nó já rodando, aí sim vale o formato interativo:

```text
conf t
router ospf 1
 ...
commit
end
```

## Nomes de arquivo dentro de um lab

```text
Labs/Cisco/SR-MPLS/<categoria>/<lab>/
├── <lab>.md                  # o roteiro, mesmo nome da pasta
├── configs/<no>.cfg          # um por nó
└── images/
    ├── topology-<lab>.png    # diagrama
    └── terminal-<assunto>.png
```

O sufixo de `terminal-*.png` diz o comando que a captura mostra, não a ordem no texto:

| Arquivo | Comando |
|---|---|
| `terminal-deploy.png` | tabela de nós depois do `clab deploy` |
| `terminal-ospf-neighbor.png` | `show ospf neighbor` |
| `terminal-ospf-interface.png` | `show ospf interface <intf>` |
| `terminal-show-route.png` | `show route <prefixo>` |
| `terminal-show-cef.png` | `show cef <prefixo> detail` |
| `terminal-backup-path.png` | `show ospf routes <prefixo> backup-path` |
| `terminal-adjacency-sids.png` | `show ospf segment-routing adjacency-sids` |
| `terminal-mpls-forwarding.png` | `show mpls forwarding` |
| `terminal-sr-policy.png` | `show segment-routing traffic-eng policy` |
| `terminal-traceroute.png` | `traceroute` |

Não usar numeração de ordem (`1_topology`) nem nome genérico (`image-3.png`): os dois quebram quando um passo é inserido ou trocado de lugar.

No markdown, o texto alternativo descreve o comando:

```markdown
![show cef 10.0.1.251/32 detail em SP](./images/terminal-show-cef.png)
```

Os diagramas saem dos `.drawio` em `SR-MPLS/TI-LFA/diagrams/` e `SR-MPLS/SR-TE/diagrams/`. Editar lá e reexportar.

## Problemas comuns

| Sintoma | Causa provável |
|---|---|
| Nó travado em `starting` | RAM insuficiente ou limite de `inotify` baixo |
| Nó sem hostname, sem usuário `clab` e sem SSH | O `.cfg` não tem o bloco base do kind `cisco_xrd` |
| Config antiga volta depois de editar o `.cfg` | Diretório do lab preservado. Use `--cleanup` no destroy |
| Adjacência OSPF não sobe | Interface errada no `.clab.yml` (`Gi0-0-0-N` tem que casar com `GigabitEthernet0/0/0/N`), ou falta `network point-to-point` |
| Custo IGP diferente do documentado | Custo declarado em um lado só. OSPF usa o custo da interface de saída, então precisa nos dois |
| `docker load` com tag diferente | Remarcar com `docker tag` |
| `ping mpls` sem saída útil | Esperado. A imagem control-plane não tem OAM MPLS completo. Use `traceroute` e `show cef` |
