# Ambiente Cisco XRd

Preparação específica para os laboratórios Cisco. Instale primeiro o Docker e
o Containerlab conforme o [guia comum do projeto](../../docs/setup.md).

Os labs usam de quatro a oito roteadores, com consumo aproximado de 1,5 GB de
RAM por nó XRd. Reserve de 6 a 12 GB. O `bgp-lu` é o maior cenário: oito
roteadores, dois contêineres Alpine, aproximadamente 12 GB de RAM e oito CPUs.

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

Clone o repositório e entre no diretório do lab. A topologia e as configurações
ficam juntas no mesmo diretório:

```bash
git clone https://github.com/rnpbr/LabRedes-segmentrouting.git
cd LabRedes-segmentrouting
cd labs/cisco/sr-mpls/ti-lfa/00-zero-segment
sudo clab deploy -t lab.clab.yml
```

Estrutura final antes do deploy:

```text
00-zero-segment/
├── README.md
├── lab.clab.yml
└── configs/
    ├── sp.cfg
    ├── df.cfg
    ├── mg.cfg
    └── ba.cfg
```

O padrão é sempre o mesmo, trocando a categoria e o nome do lab:

```bash
cd labs/cisco/sr-mpls/<categoria>/<lab>
sudo clab deploy -t lab.clab.yml
```

`<categoria>` é `ti-lfa`, `sr-te` ou `inter-as`. Cada roteiro informa o caminho
exato e os nomes dos nós.

Acesso: `ssh clab@<ip>`, senha `clab@123`. Cada lab documenta os IPs. Alternativa sem SSH:

```bash
sudo docker exec -it clab-tilfa-zero-segment-sp /pkg/bin/xr_cli.sh
```

Derrubar:

```bash
sudo clab destroy -t lab.clab.yml --cleanup
```

O `--cleanup` apaga o estado gerado pelo Containerlab, não os arquivos
versionados do laboratório. Sem ele, a configuração gravada pelo XRd pode ser
reutilizada no próximo deploy.

> Em geral, os `lab.clab.yml` usam `enforce-startup-config: true`, fazendo cada
> deploy reaplicar o `.cfg`. Consulte a topologia escolhida antes de contar com
> a preservação de mudanças manuais.



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
labs/cisco/sr-mpls/<categoria>/<lab>/
├── README.md                 # roteiro do laboratório
├── lab.clab.yml              # topologia Containerlab
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

Os diagramas saem dos `.drawio` em `sr-mpls/ti-lfa/diagrams/` e
`sr-mpls/sr-te/diagrams/`. Edite a fonte correspondente e reexporte.

Capturas de terminal são sempre `.png`. Diagramas podem ser `.svg`: é o caso do `bgp-lu`, cujas figuras têm variante clara e escura (`<nome>.svg` e `<nome>-escuro.svg`) servidas por `<picture>`/`prefers-color-scheme`, para continuarem legíveis no tema escuro do GitHub.

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
