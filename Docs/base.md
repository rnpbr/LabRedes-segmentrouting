# SR-MPLS sobre Cisco IOS-XR - Referência Base

> Conceitos centrais de SR-MPLS no plano de dados IOS-XR, convenções do projeto e config mínima de sinalização. Pré-requisito dos labs.

Ambiente (Docker, Containerlab, imagem XRd): [`setup.md`](./setup.md). O que existe e em que ordem seguir: [`roadmap.md`](./roadmap.md).

Imagem de referência: `ios-xr/xrd-control-plane:7.10.2` (nome local que o `docker load` produz a partir do tarball do CCO - ver `setup.md`).

## Conceitos centrais

**Segment Routing.** Encaminhamento source-routed: o nó de entrada (headend) impõe um stack de labels que descreve o caminho. Nós intermediários só olham o label do topo, sem estado por LSP. No SR-MPLS o stack é MPLS convencional - muda a semântica e como os labels são distribuídos.

**SID.** Instrução de encaminhamento identificada por um número. Dois tipos usados aqui:

- **Prefix-SID**: identifica um destino IP (loopback) globalmente no domínio, anunciado pelo IGP. Quando o prefixo representa um nó, também chamado **node-SID**.
- **Adjacency-SID**: identifica um link de saída específico. Local ao nó que o anuncia.

Esta fundação usa só prefix-SIDs em loopbacks.

**SRGB.** Faixa de labels reservada para SIDs globais. Com a mesma SRGB em todos os nós, `label = SRGB.base + index` vale em qualquer ponto do domínio - o headend empilha `base + index_destino` sem saber onde o destino está. Default IOS-XR: `16000-23999`.

**SRLB.** Faixa de labels para SIDs *locais* (adjacency-SIDs manuais, binding-SIDs). Significado só no nó que anuncia.

**IGP carrega SR.** OSPFv2 usa Opaque LSAs (RFC 8665) para anunciar SIDs; IS-IS usa sub-TLVs (RFC 8667). Sem protocolo separado de distribuição de label - LDP não entra. Menos protocolos, menos sincronização, menos caso de borda.

**SR-prefer.** Em equipamentos com LDP e SR em paralelo, a flag `sr-prefer` prioriza labels SR. Nenhum lab deste projeto roda LDP, então a flag é omitida - citada aqui só por completude.

## Convenções do projeto

Vinculantes para todo lab. É o que permite os materiais linkarem entre si sem ambiguidade.

| Item | Valor |
|---|---|
| SRGB | `16000-23999` |
| SRLB | `15000-15999` (default IOS-XR) |
| IGP | OSPFv2, single-area `0` |
| Loopbacks | `10.0.0.0/24`, host = ID do nó |
| Endereços de link | `192.0.2.0/24` (RFC 5737), `/31` por enlace |
| Prefix-SID index | igual ao ID do nó |
| Label do node-SID | `16000 + ID` |
| Interfaces de core | `network point-to-point` |
| Loopback0 em OSPF | `passive` |
| `sr-prefer` | não usado (nenhum lab roda LDP) |

- Nó com Loopback0 `10.0.0.5/32` -> prefix-SID index `5` -> label `16005` em qualquer ponto do domínio.
- `192.0.2.0/24` é reservado pela RFC 5737 para documentação - correto em lab, não usar em produção.
- Single-area `0` simplifica os labs; multi-area é material próprio (ver roadmap).

## Topologia de referência

Cinco nós, dimensionada para ~5GB de RAM (imagem XRd control-plane):

```text
              p1
            / | \
         pe1  p3  pe2
            \ | /
              p2
```

`pe1`<->`{p1,p2}`, `pe2`<->`{p1,p2}`, `p3`<->`{p1,p2}`. `p3` sem enlace direto com `pe1` ou `pe2`.

- pe1<->pe2 via `p1` ou via `p2`: equal-cost, ECMP nativo.
- pe1<->pe2 via `p3` (`pe1-p1-p3-p2-pe2`): estritamente mais longo - usado para forçar caminho não-mais-curto em SR-TE/Flex-Algo.

| Nó | Papel | Loopback0 | Prefix-SID index | Label |
|---|---|---|---:|---:|
| pe1 | PE | `10.0.0.1/32` | 1 | `16001` |
| p1 | P | `10.0.0.2/32` | 2 | `16002` |
| p2 | P | `10.0.0.3/32` | 3 | `16003` |
| p3 | P | `10.0.0.4/32` | 4 | `16004` |
| pe2 | PE | `10.0.0.5/32` | 5 | `16005` |

| Enlace | Lado A | A IP | Lado B | B IP |
|---|---|---|---|---|
| pe1-p1 | pe1 Gi0/0/0/0 | `192.0.2.0/31` | p1 Gi0/0/0/0 | `192.0.2.1/31` |
| pe1-p2 | pe1 Gi0/0/0/1 | `192.0.2.2/31` | p2 Gi0/0/0/0 | `192.0.2.3/31` |
| p1-pe2 | p1 Gi0/0/0/1 | `192.0.2.4/31` | pe2 Gi0/0/0/0 | `192.0.2.5/31` |
| p2-pe2 | p2 Gi0/0/0/1 | `192.0.2.6/31` | pe2 Gi0/0/0/1 | `192.0.2.7/31` |
| p1-p3 | p1 Gi0/0/0/2 | `192.0.2.8/31` | p3 Gi0/0/0/0 | `192.0.2.9/31` |
| p3-p2 | p3 Gi0/0/0/1 | `192.0.2.10/31` | p2 Gi0/0/0/2 | `192.0.2.11/31` |

Ilustração, não um lab com deploy próprio - os labs aplicados (TI-LFA, SR-TE) trazem ambientes com temática Rede Ipê, listados no [`roadmap.md`](./roadmap.md), e referenciam este texto para conceitos e convenções.

## Configuração de referência

Três blocos reusáveis por todo lab do projeto. Substituir `<ID>`/`<X>` conforme a tabela de nós/enlaces de cada topologia real.

**Bloco global SR** (idêntico em todo nó):

```text
segment-routing global-block 16000 23999
segment-routing local-block  15000 15999
```

**Loopback0 + SR no OSPF:**

```text
interface Loopback0
 ipv4 address 10.0.0.<ID> 255.255.255.255
!
router ospf 1
 router-id 10.0.0.<ID>
 segment-routing mpls
 area 0
  segment-routing mpls
  interface Loopback0
   passive enable
   prefix-sid index <ID>
```

**Interface de core** (repetir por enlace):

```text
interface GigabitEthernet0/0/0/<X>
 description <enlace>
 ipv4 address 192.0.2.<a> 255.255.255.254
 no shutdown
!
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/<X>
   network point-to-point
```

Configs completas prontas para deploy (`configs/*.cfg` por nó) estão nos labs individuais, não aqui - ver `roadmap.md`.

## Validação

A partir de `pe1`, equivalente em qualquer nó.

**Adjacências:** `show ospf neighbor` -> `FULL` em toda interface de core; `pe1` tem dois neighbors (`p1`, `p2`).

**Prefix-SIDs:** `show ospf segment-routing prefix-sid-map active-policy` -> tabela com cada loopback e seu SID index. `show ospf database opaque-area self-originate` -> nó local anuncia seu prefix-SID via Opaque LSA Extended Prefix.

**Rota SR:** `show route 10.0.0.5/32 detail` -> ECMP via `p1` e `p2`, label outgoing `16005` imposto.

**MPLS forwarding:** `show mpls forwarding` -> entrada para cada label `16001..16005` (local aparece como `Pop`). `show mpls label table 0 label 16005 detail` -> detalhe do node-SID de `pe2`.

**Plano de dados:** `ping`/`traceroute 10.0.0.5 source 10.0.0.1` -> responde, dois hops intermediários carregando label `16005`. Imagem é control-plane-only: `ping mpls`/`traceroute mpls` podem não retornar dado útil - para data plane rigoroso, usar imagem com forwarding plane completo.

**ECMP:** `show cef ipv4 10.0.0.5/32` -> duas entradas equal-cost (`192.0.2.1`, `192.0.2.3`). Uma entrada só = revisar métricas OSPF e `network point-to-point`.

## Glossário

**Adjacency-SID.** SID local de uma adjacência de saída específica. Base de segmentos explícitos que precisam atravessar um link, não só chegar a um nó. Label alocado da SRLB.

**Affinity.** Cor administrativa de um link, usada por Flex-Algo e SR-TE para incluir/excluir/preferir links em restrições de caminho.

**BGP-LU (RFC 8277).** BGP carregando prefixo + label MPLS. Mecanismo padrão para estender alcance MPLS entre domínios/ASes. Central em SR multi-domínio.

**Binding-SID.** SID local de uma SR Policy inteira. Outros nós empilham só esse label sem conhecer os segmentos internos.

**Color.** Atributo numérico de uma SR Policy. Com o endpoint, identifica a policy - usado para casar intent (ex: baixa latência) com a policy certa.

**Endpoint.** Destino IP de uma SR Policy, tipicamente a loopback de um PE remoto.

**Flexible Algorithm (Flex-Algo).** SPF alternativo do IGP com restrições (afinidades, métrica distinta), construindo plano de encaminhamento paralelo sem RSVP-TE.

**Node-SID.** Prefix-SID cujo prefixo é a loopback de um nó. Caso mais comum de prefix-SID.

**Prefix-SID.** SID global de um prefixo IP. Mesmo label em todo o domínio com SRGB consistente. Anunciado pelo IGP.

**Segment list.** Sequência ordenada de SIDs descrevendo um caminho explícito. No plano de dados, um label stack MPLS.

**SR Policy.** Intent (color + endpoint) associada a candidate paths (cada um, uma ou mais segment lists). Identificada por um binding-SID.

**SRGB.** Faixa de labels para SIDs globais. Idealmente uniforme no domínio.

**SRLB.** Faixa de labels para SIDs locais (adjacency-SIDs, binding-SIDs).

**TI-LFA.** Fast reroute do SR. Pré-computa backup para falha de link, nó ou SRLG, cobertura independente de topologia. Sem RSVP-TE.

## Referências

- RFC 8402 - *Segment Routing Architecture*. <https://datatracker.ietf.org/doc/html/rfc8402>
- RFC 8660 - *Segment Routing with the MPLS Data Plane*. <https://datatracker.ietf.org/doc/html/rfc8660>
- RFC 8665 - *OSPF Extensions for Segment Routing*. <https://datatracker.ietf.org/doc/html/rfc8665>
- RFC 8667 - *IS-IS Extensions for Segment Routing*. <https://datatracker.ietf.org/doc/html/rfc8667>
- RFC 9256 - *Segment Routing Policy Architecture*. <https://datatracker.ietf.org/doc/html/rfc9256>
- RFC 8277 - *Using BGP to Bind MPLS Labels to Address Prefixes*. <https://datatracker.ietf.org/doc/html/rfc8277>
- RFC 5737 - *IPv4 Address Blocks Reserved for Documentation*. <https://datatracker.ietf.org/doc/html/rfc5737>
- Cisco IOS XR 7.10.x - *Segment Routing Configuration Guide*. <https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x.html>
- Containerlab - *Cisco XRd kind*. <https://containerlab.dev/manual/kinds/xrd/>
- CCIE SP v5.1 Labs - *Segment Routing*. <https://ccie-sp.gitbook.io/ccie-spv5.1-labs/labs/sr>