# Validação do lab bgp-lu

> Documento de apoio ao [lab `bgp-lu`](./README.md): o que uma execução de
> referência efetivamente confirmou, e o que ela não autoriza concluir.

## Três níveis independentes

1. **estático:** coerência entre topologia, configs e documentação;
2. **plano de controle:** estado observado no IOS XR;
3. **data plane:** encaminhamento de pacotes.

Uma verificação em um nível não é promovida automaticamente ao seguinte.

## Ambiente da execução de referência

| Item | Valor |
|---|---|
| Data | 28 de agosto de 2026 |
| Host | Linux, 12 CPUs, 125 GiB RAM |
| Containerlab | 0.77.0 |
| Imagem | XRd Control Plane 7.10.2 |
| Roteadores | 8 XRd Control Plane |
| Clientes | 2 Alpine Linux 3.20 |

> A execução foi feita antes deste lab ser reorganizado no padrão do
> repositório. Naquele momento a topologia se chamava `ipe-sr-interas`, a imagem
> estava marcada como `xrd-control-plane:7.10.2` e os nós não tinham o bloco base
> do kind `cisco_xrd` nem endereços de gerência fixos. Os nomes de contêiner nas
> saídas originais seguiam o prefixo `clab-ipe-sr-interas-`. A configuração de
> roteamento - interfaces, OSPF, SR, BGP, TI-LFA, EPE e SR Policy - é a mesma
> que está hoje em `configs/`, byte a byte. O que mudou foi o empacotamento.

## Conferência estática

Antes de qualquer deploy, vale conferir à mão:

- 11 enlaces e 10 nós no `.clab.yml`;
- oito startup-configs, com loopbacks e SID index únicos;
- endereçamento e `/31` conforme a matriz de enlaces do roteiro;
- custos OSPF declarados **nos dois lados** de cada enlace;
- as três sessões LU, a sessão de serviço, o EPE e a lista de segmentos
  presentes nos `.cfg` corretos;
- ausência de LDP, RSVP, VPNv4 e L2VPN;
- toda referência de imagem no markdown resolvendo para um arquivo em `images/`.

Custo declarado em um lado só é o erro mais fácil de cometer e o mais difícil de
enxergar: o OSPF usa o custo da interface de saída, então o caminho fica
assimétrico e a análise de ramo primário/alternativo deixa de valer.

## Plano de controle e data plane

| Verificação | Estado |
|---|---|
| Deploy dos 10 contêineres | aprovado |
| OSPF `FULL` nos oito XRd | aprovado |
| Prefix-SIDs e LFIB | aprovado |
| três sessões BGP-LU | aprovado |
| recursão LU em `pe-pop-pb` | aprovado |
| filtro LU restrito às loopbacks | aprovado |
| repair path TI-LFA | aprovado, resolvido como `Local-LFA` |
| PeerNode SID 15100 | aprovado |
| SR Policy cor 100 | aprovado |
| sessão PE-PE de serviço | aprovado, `Established` |
| rota de serviço com cor 100 | aprovada, resolvida pela SR Policy |
| tráfego cliente-cliente | aprovado nos dois sentidos, 0% de perda |
| pilha MPLS no traceroute | aprovada, coerente com a lista explícita |

### Resultados observados

- Os quatro nós de borda consultados mostraram dois vizinhos OSPF `FULL`; cada
  adjacência observada confirma também o estado no nó P correspondente.
- A rota `pe-pop-pb → 10.0.0.4/32` foi instalada como SR, label `16004`,
  primário via `192.0.2.1` e backup via `192.0.2.3`, classificado
  `Backup (Local-LFA)`.
- As duas sessões de `asbr-pop-pb` - iBGP com `10.0.0.1` e eBGP com `192.0.2.9`
  - estavam `Established` e recebiam exatamente um prefixo LU cada.
- `pe-pop-pb` recebeu `10.0.0.8/32` pelo AS-path `1916` como best
  labeled-unicast, com label recebido `16008` nessa execução. O CEF impôs
  `{16004 16008}` via `p-pop-a`.
- A rede de cliente `203.0.113.0/24` chegou ao PE pela sessão IPv4 unicast, com
  Color Extended Community 100, e foi associada à policy pelo BSID `24005`.
- `pe-ipe-ce` apresentou simetricamente `10.0.0.1/32` como best LU.
- O CEF mostrou backups `Local-LFA` por `p-pop-b` no domínio do PoP e
  `p-ipe-ba` no domínio do backbone.
- `asbr-pop-pb` associou o PeerNode SID `15100` ao peer `192.0.2.9`; a LFIB
  programou `Pop`/encaminhamento em Gi0/0/0/2.
- A policy cor 100 ficou Admin/Operational `up`, candidate path ativo, lista
  explícita válida com cinco SIDs e Binding SID dinâmico `24005`.
- A sessão IPv4 unicast `pe-pop-pb`-`pe-ipe-ce` ficou `Established`, recebendo
  um prefixo, e estava estável havia 2 semanas e 6 dias no momento da captura.
- Os pings `instituicao-pb → servico-ce` e `servico-ce → instituicao-pb`
  entregaram 3 de 3 pacotes, sem perda.
- O traceroute da instituição ao serviço chegou ao destino em sete saltos. As
  extensões ICMP MPLS mostraram a pilha `{16004, 15100, 16007, 16008}` no ramo
  explícito, reduzida um label por etapa até a entrega IP.

## Critério para labels dinâmicos

Labels observados devem ser correlacionados entre saídas da **mesma** execução.
Os Prefix-SIDs `16001`-`16008` e o PeerNode SID `15100` derivam de índices
configurados; o Binding SID da policy é dinâmico.

Nesta execução o label LU `16008` coincidiu com o Prefix-SID indexado do PE
remoto. A igualdade numérica não elimina o contrato downstream: a semântica
continua sendo determinada pelo roteador que recebe o label e por sua entrada de
LFIB. Não converta um valor alocado dinamicamente em constante de configuração.

## Tempo de estabilização

Esta captura foi feita em estado estável, quase três semanas após o deploy. Uma
captura anterior, feita cedo demais, encontrou a sessão de serviço em `Active` e
**foi incorretamente tratada como limitação permanente da imagem**. Esse erro é
o motivo de o roteiro insistir que o gate seja definido por estado e alcance, e
não por um temporizador fixo.

Aguarde estes cinco em conjunto antes de concluir qualquer coisa:

```text
show bgp ipv4 labeled-unicast summary
show bgp ipv4 labeled-unicast 10.0.0.8/32
show cef 10.0.0.8/32 detail
show bgp ipv4 unicast summary
show bgp ipv4 unicast 203.0.113.0/24
```

Depois confirme o encaminhamento com ping e traceroute entre os clientes.

## Limitação conhecida

XRd Control Plane não deve ser equiparado a um roteador com data plane de
produção. Nesta execução a sessão multihop, o encaminhamento bidirecional e a
pilha da policy foram observados positivamente - mas esses resultados demonstram
o funcionamento **deste lab**, não capacidade, latência de hardware ou
convergência em 50 ms.

O estágio 5 valida a instalação do repair path. Medir perda durante uma falha
exige BFD, timestamps e uma plataforma de forwarding representativa; nenhum dos
três existe aqui.

## Ao publicar uma nova execução

- registre a data, a versão do Containerlab e a tag da imagem;
- não edite uma saída para fazê-la coincidir com o resultado esperado;
- se precisar reduzir uma saída, preserve a original e cite o recorte;
- nunca converta ping/traceroute sem resposta em prova de forwarding.
