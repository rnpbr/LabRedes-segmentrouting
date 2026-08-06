# SR-MPLS sobre Cisco IOS-XR — Referência Base

> Documento de referência. Define os conceitos centrais de Segment Routing MPLS no plano de dados Cisco IOS-XR, as convenções adotadas neste projeto e a configuração mínima de sinalização. Materiais sucessivos tomam este texto como pré-requisito.

## Escopo

Está em escopo:

- Ideia geral de Segment Routing aplicada ao plano de dados MPLS.
- Sinalização de prefix-SIDs por OSPFv2.
- Faixas SRGB e SRLB, e por que importam.
- Convenções de endereçamento, naming e indexação de SIDs adotadas pelo projeto.
- Topologia de referência usada como ilustração.
- Configuração de referência em IOS-XR.
- Comandos de validação que confirmam que o domínio SR está saudável.

A imagem de referência usada nos exemplos é `xrd-control-plane:7.10.2`. Comandos e saídas refletem essa versão.

## Conceitos centrais

**Segment Routing.** Modelo de encaminhamento source-routed: o nó de entrada (headend) impõe um stack de labels que descreve o caminho desejado. Os nós intermediários encaminham olhando apenas o label do topo. Não há estado por LSP nos nós intermediários. No SR-MPLS, o stack é um stack MPLS convencional; o que muda é a semântica e a forma como os labels são distribuídos.

**SID (Segment Identifier).** Identifica um segmento — uma instrução de encaminhamento. Dois tipos importam aqui:

- **Prefix-SID**: identifica um destino IP (tipicamente uma loopback) globalmente no domínio. É anunciado pelo IGP. Quando o prefixo é uma loopback que representa um nó, o prefix-SID também é chamado de **node-SID**.
- **Adjacency-SID**: identifica um link específico de saída. É local ao nó que o anuncia. Útil em segmentos explícitos que precisam atravessar uma adjacência específica.

Esta fundação usa apenas prefix-SIDs em loopbacks.

**SRGB (Segment Routing Global Block).** Faixa de labels MPLS reservada para SIDs globais. Cada nó configura sua SRGB; quando todos os nós usam a *mesma* SRGB, o label MPLS associado a um prefix-SID é o mesmo em qualquer ponto do domínio (`label = SRGB.base + index`). É o que permite ao headend simplesmente empilhar `SRGB.base + index_destino` sabendo que qualquer nó interpretará da mesma forma.

A faixa default em IOS-XR vai de 16000 a 23999. Em domínios cooperantes ou que se interconectam, faz sentido convencionar a faixa explicitamente.

**SRLB (Segment Routing Local Block).** Faixa de labels para SIDs *locais* (adjacency-SIDs configurados manualmente, binding-SIDs, etc.). Local significa que o label tem significado apenas no nó que o anuncia.

**IGP carrega SR.** OSPFv2 estende sua sinalização com Opaque LSAs (RFC 8665) para anunciar SIDs e capacidades SR. IS-IS faz o equivalente com sub-TLVs (RFC 8667). Não há protocolo separado de distribuição de label — LDP some. É um dos principais ganhos operacionais do SR sobre MPLS clássico: menos protocolos, menos sincronização, menos casos de borda.

**SR-prefer.** Em equipamentos com LDP e SR habilitados em paralelo (cenário transitório), a flag `sr-prefer` instrui o nó a preferir labels SR sobre os LDP. Em ambientes greenfield SR puro, configura-se ainda assim por consistência.

## Convenções adotadas pelo projeto

As convenções a seguir são vinculantes para os labs e materiais subsequentes deste projeto. Reusar este esquema é o que permite que diferentes artigos linkem entre si sem ambiguidade.

| Item | Valor |
|---|---|
| SRGB | `16000`–`23999` |
| SRLB | `15000`–`15999` (default IOS-XR) |
| IGP | OSPFv2, single-area `0` |
| Loopbacks | `10.0.0.0/24`, host = ID do nó |
| Endereços de links | `192.0.2.0/24` (RFC 5737), `/31` por enlace |
| Prefix-SID index | igual ao ID do nó |
| Label do node-SID | `16000 + ID` |
| Network type em interfaces de core | `point-to-point` |
| Loopback0 em OSPF | `passive` |
| `sr-prefer` | habilitado |

Implicações práticas:

- Um nó com Loopback0 `10.0.0.5/32` recebe prefix-SID index `5`, que se manifesta como label MPLS `16005` em qualquer ponto do domínio.
- O bloco `192.0.2.0/24` está reservado pela RFC 5737 para documentação. Adequado em ambientes de laboratório; não usar em produção.
- Single-area `0` simplifica os labs. Cenários multi-area saem em material próprio.

## Topologia de referência

A topologia adotada como ilustração tem cinco nós e foi dimensionada para caber confortavelmente em um host de desenvolvimento (cerca de 5 GB de RAM com a imagem XRd Control Plane) ao mesmo tempo em que cobre os comportamentos relevantes:

```text
              p1
            / | \
         pe1  p3  pe2
            \ | /
              p2
```

Adjacências: `pe1`↔`{p1,p2}`, `pe2`↔`{p1,p2}`, `p3`↔`{p1,p2}`. `p3` não tem enlace com `pe1` nem com `pe2`.

- Caminhos pe1↔pe2 via `p1` e via `p2` são equal-cost (ECMP nativo do IGP).
- O caminho via `p3` (`pe1—p1—p3—p2—pe2` ou simétrico) é estritamente mais longo, útil quando precisamos forçar tráfego por um caminho não-mais-curto em materiais subsequentes (SR-TE, Flex-Algo).

| Nó | Papel | Loopback0 | Prefix-SID index | Label |
|---|---|---|---:|---:|
| pe1 | PE | `10.0.0.1/32` | 1 | `16001` |
| p1  | P  | `10.0.0.2/32` | 2 | `16002` |
| p2  | P  | `10.0.0.3/32` | 3 | `16003` |
| p3  | P  | `10.0.0.4/32` | 4 | `16004` |
| pe2 | PE | `10.0.0.5/32` | 5 | `16005` |

| Enlace  | Lado A         | A IP            | Lado B         | B IP            |
|---|---|---|---|---|
| pe1↔p1  | pe1 Gi0/0/0/0  | `192.0.2.0/31`  | p1 Gi0/0/0/0   | `192.0.2.1/31`  |
| pe1↔p2  | pe1 Gi0/0/0/1  | `192.0.2.2/31`  | p2 Gi0/0/0/0   | `192.0.2.3/31`  |
| p1↔pe2  | p1 Gi0/0/0/1   | `192.0.2.4/31`  | pe2 Gi0/0/0/0  | `192.0.2.5/31`  |
| p2↔pe2  | p2 Gi0/0/0/1   | `192.0.2.6/31`  | pe2 Gi0/0/0/1  | `192.0.2.7/31`  |
| p1↔p3   | p1 Gi0/0/0/2   | `192.0.2.8/31`  | p3 Gi0/0/0/0   | `192.0.2.9/31`  |
| p3↔p2   | p3 Gi0/0/0/1   | `192.0.2.10/31` | p2 Gi0/0/0/2   | `192.0.2.11/31` |

A topologia é apresentada como ilustração — este artigo não inclui passo-a-passo de bring-up. Os artigos seguintes do projeto trazem ambientes próprios (variando topologia conforme o tema), e este texto é referenciado por eles para a parte conceitual e de convenções.

## Configuração de referência

Os snippets a seguir são padrões reusáveis pelos materiais sucessivos. São apresentados em três blocos consolidados — global, OSPF+SR, interface de core — e em duas instâncias completas (um PE e um P), evitando repetir cinco configurações quase idênticas.

### Bloco global SR

Idêntico em todos os nós:

```text
segment-routing global-block 16000 23999
segment-routing local-block  15000 15999
```

### Loopback0 e habilitação de SR no OSPF

```text
interface Loopback0
 ipv4 address 10.0.0.<ID> 255.255.255.255
!
router ospf 1
 router-id 10.0.0.<ID>
 segment-routing mpls
 segment-routing sr-prefer
 area 0
  segment-routing mpls
  interface Loopback0
   passive enable
   prefix-sid index <ID>
```

`<ID>` é o ID do nó (1 a 5 nesta topologia). O `prefix-sid index <ID>` em conjunto com a SRGB padrão produz o label `16000 + ID` para o node-SID.

### Interface de core

Aplicado a cada interface que participa do core SR:

```text
interface GigabitEthernet0/0/0/<X>
 description <descrição do enlace>
 ipv4 address 192.0.2.<a> 255.255.255.254
 no shutdown
!
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/<X>
   network point-to-point
```

### Configuração completa: PE (exemplo `pe1`)

```text
configure
hostname pe1
segment-routing global-block 16000 23999
segment-routing local-block  15000 15999
!
interface Loopback0
 ipv4 address 10.0.0.1 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description pe1 to p1
 ipv4 address 192.0.2.0 255.255.255.254
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description pe1 to p2
 ipv4 address 192.0.2.2 255.255.255.254
 no shutdown
!
router ospf 1
 router-id 10.0.0.1
 segment-routing mpls
 segment-routing sr-prefer
 area 0
  segment-routing mpls
  interface Loopback0
   passive enable
   prefix-sid index 1
  !
  interface GigabitEthernet0/0/0/0
   network point-to-point
  !
  interface GigabitEthernet0/0/0/1
   network point-to-point
  !
 !
!
commit
end
```

`pe2` segue o mesmo molde, trocando hostname, ID e endereços.

### Configuração completa: P (exemplo `p1`)

```text
configure
hostname p1
segment-routing global-block 16000 23999
segment-routing local-block  15000 15999
!
interface Loopback0
 ipv4 address 10.0.0.2 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description p1 to pe1
 ipv4 address 192.0.2.1 255.255.255.254
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description p1 to pe2
 ipv4 address 192.0.2.4 255.255.255.254
 no shutdown
!
interface GigabitEthernet0/0/0/2
 description p1 to p3
 ipv4 address 192.0.2.8 255.255.255.254
 no shutdown
!
router ospf 1
 router-id 10.0.0.2
 segment-routing mpls
 segment-routing sr-prefer
 area 0
  segment-routing mpls
  interface Loopback0
   passive enable
   prefix-sid index 2
  !
  interface GigabitEthernet0/0/0/0
   network point-to-point
  !
  interface GigabitEthernet0/0/0/1
   network point-to-point
  !
  interface GigabitEthernet0/0/0/2
   network point-to-point
  !
 !
!
commit
end
```

`p2` e `p3` seguem o mesmo molde, com seus respectivos hostnames, IDs e endereços.

## Validação

Os comandos a seguir confirmam que cada parte da fundação está operacional. Apresentados a partir de `pe1`, mas equivalentes em qualquer nó.

### Adjacências OSPF

```text
show ospf neighbor
```

Esperado: estado `FULL` em todas as interfaces de core. Em `pe1`, dois neighbors: `p1` e `p2`. Estados intermediários (`INIT`, `2-WAY`) durante boot são normais e devem convergir em segundos.

### Propagação de prefix-SIDs

```text
show ospf segment-routing prefix-sid-map active-policy
```

Esperado: tabela contendo cada loopback do domínio e seu SID index correspondente, originada por cada nó.

```text
show ospf database opaque-area self-originate
```

Esperado: o nó local anuncia seu próprio prefix-SID via Opaque LSA do tipo Extended Prefix.

### Resolução de rota com SR

```text
show route 10.0.0.5/32 detail
```

Esperado: rota OSPF aprendida via duas next-hops (ECMP por `p1` e por `p2`). O detalhe deve mostrar o label outgoing — `16005` — sendo imposto.

### Tabela de MPLS forwarding

```text
show mpls forwarding
```

Esperado: entradas para cada label `16001..16005` (exceto o local, que aparece como `Pop`), com label outgoing e interface.

```text
show mpls label table 0 label 16005 detail
```

Esperado: detalhe da entrada para o label 16005 (node-SID de `pe2`), confirmando resolução pelo IGP path computado.

### Plano de dados

```text
ping       10.0.0.5 source 10.0.0.1
traceroute 10.0.0.5 source 10.0.0.1
```

Esperado: ping responde; traceroute mostra dois hops intermediários (`p1` ou `p2`) carregando label `16005`.

A imagem `xrd-control-plane` é, como o nome diz, control plane apenas. Determinados comandos de OAM MPLS (`ping mpls`, `traceroute mpls`) podem não retornar dados úteis do data plane. Para verificação rigorosa do plano de dados, use uma imagem com forwarding plane completo.

### ECMP

```text
show cef ipv4 10.0.0.5/32
```

Esperado: duas entradas equal-cost referenciando os next-hops `192.0.2.1` e `192.0.2.3`. Se aparecer apenas uma, ECMP não está funcionando como esperado — reveja métricas OSPF e o `network point-to-point` das interfaces.

## Glossário

**Adjacency-SID.** SID local que identifica uma adjacência (link) de saída específica. Útil para construir caminhos explícitos que precisam atravessar um link específico, e não apenas chegar a um nó. O label é alocado da SRLB.

**Affinity.** Atributo administrativo (cor) atribuído a um link, usado por Flex-Algo e SR-TE para construir caminhos que satisfaçam restrições (incluir, excluir, preferir links com determinada cor).

**BGP-LU (BGP Labeled Unicast, RFC 8277).** Extensão do BGP que carrega prefixos junto com seus labels MPLS. Mecanismo padrão para estender alcance MPLS através de fronteiras BGP, inclusive entre ASes. Central no material de SR multi-domínio.

**Binding-SID.** SID local atribuído a uma SR Policy. Fornece um label único que representa toda uma policy multi-segment, permitindo que outros nós empilhem esse label sem precisar conhecer os segmentos internos.

**Color.** Atributo numérico associado a uma SR Policy. Junto com o endpoint, identifica a policy. Usado pelo headend para correspondência entre intent (e.g. "tráfego de baixa latência") e policy a aplicar.

**Endpoint.** Endereço IP de destino de uma SR Policy. Tipicamente a loopback de um PE remoto.

**Flexible Algorithm (Flex-Algo).** Recurso do IGP que permite computar SPFs alternativos com restrições (afinidades, métricas distintas como latência), construindo planos de encaminhamento paralelos sem RSVP-TE.

**Node-SID.** Caso especial de prefix-SID em que o prefixo é uma loopback que representa o nó. Modalidade mais comum de prefix-SID.

**Prefix-SID.** SID global associado a um prefixo IP. Mesmo label em todos os nós do domínio, assumindo SRGB consistente. Anunciado pelo IGP.

**Segment list.** Sequência ordenada de SIDs que descreve um caminho explícito. Materializa-se como um label stack MPLS no plano de dados.

**SR Policy.** Construção do headend que associa uma intent (color + endpoint) a um conjunto de candidate paths (cada um composto por uma ou mais segment lists). Identificada por um binding-SID.

**SRGB (Segment Routing Global Block).** Faixa de labels reservada para SIDs globais. Idealmente uniforme em todo o domínio.

**SRLB (Segment Routing Local Block).** Faixa de labels reservada para SIDs locais (adjacency-SIDs configurados, binding-SIDs, etc.).

**TI-LFA (Topology-Independent Loop-Free Alternate).** Mecanismo de fast reroute do SR. Pré-computa caminhos de backup para falhas de link, nó ou SRLG, com cobertura independente de topologia. Não requer RSVP-TE.

## Referências

- RFC 8402 — *Segment Routing Architecture*. <https://datatracker.ietf.org/doc/html/rfc8402>
- RFC 8660 — *Segment Routing with the MPLS Data Plane*. <https://datatracker.ietf.org/doc/html/rfc8660>
- RFC 8665 — *OSPF Extensions for Segment Routing*. <https://datatracker.ietf.org/doc/html/rfc8665>
- RFC 8667 — *IS-IS Extensions for Segment Routing*. <https://datatracker.ietf.org/doc/html/rfc8667>
- RFC 9256 — *Segment Routing Policy Architecture*. <https://datatracker.ietf.org/doc/html/rfc9256>
- RFC 8277 — *Using BGP to Bind MPLS Labels to Address Prefixes*. <https://datatracker.ietf.org/doc/html/rfc8277>
- RFC 5737 — *IPv4 Address Blocks Reserved for Documentation*. <https://datatracker.ietf.org/doc/html/rfc5737>
- Cisco IOS XR 7.10.x — *Segment Routing Configuration Guide*. <https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x.html>
- Containerlab — *Cisco XRd kind*. <https://containerlab.dev/manual/kinds/xrd/>
- CCIE SP v5.1 Labs — *Segment Routing*. <https://ccie-sp.gitbook.io/ccie-spv5.1-labs/labs/sr>
