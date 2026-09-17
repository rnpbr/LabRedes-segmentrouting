# Fundamentos de SR-MPLS

Base conceitual comum aos laboratórios de SR-MPLS deste projeto. A configuração
de referência em IOS-XR está no [laboratório base Cisco](../../../labs/cisco/sr-mpls/00-base/README.md).

## Segment Routing

No Segment Routing, o nó de entrada codifica no pacote uma sequência de
instruções, ou segmentos, que descreve o encaminhamento desejado. Os nós
intermediários executam a instrução ativa sem manter estado por LSP.

No data plane MPLS, cada Segment Identifier (SID) é representado por um label.
A lista de segmentos torna-se uma pilha de labels imposta pelo nó de entrada.

## Tipos de SID

- **Prefix-SID:** identifica um prefixo IP e tem significado global no domínio
  SR. Quando identifica a loopback de um roteador, também é chamado de Node-SID.
- **Adjacency-SID:** identifica um enlace de saída e tem significado local no
  nó que o anuncia.
- **Binding-SID:** representa uma política ou lista de segmentos completa e
  permite compor políticas sem expor todos os segmentos internos.

## Blocos de labels

O **SRGB** (Segment Routing Global Block) contém os labels usados pelos SIDs
globais. Quando os nós usam o mesmo bloco, um Prefix-SID index é traduzido de
forma consistente em `label = base do SRGB + index`.

O **SRLB** (Segment Routing Local Block) reserva labels cujo significado é
local, como determinados Adjacency-SIDs e Binding-SIDs.

## Distribuição pelo IGP

O próprio IGP anuncia os SIDs e atributos de Segment Routing. O OSPFv2 utiliza
as extensões da RFC 8665 e o IS-IS, as extensões da RFC 8667. Não é necessário
um protocolo separado de distribuição de labels dentro do domínio SR.

## Próximas leituras

- [TI-LFA](./ti-lfa.md): proteção e reconvergência.
- [SR-TE](./sr-te.md): engenharia de tráfego com SR Policy.
- [Inter-AS](./inter-as.md): transporte rotulado entre domínios.

## Glossário

**Color.** Identificador numérico da intenção associada a uma SR Policy.

**Endpoint.** Endereço de destino de uma SR Policy.

**Flex-Algo.** Algoritmo SPF adicional, com restrições próprias, distribuído
pelo IGP.

**Segment list.** Sequência ordenada de SIDs; no SR-MPLS, uma pilha de labels.

**SR Policy.** Política identificada por color e endpoint que conduz tráfego por
um caminho SR específico.

## Referências

- RFC 8402 — *Segment Routing Architecture*: <https://datatracker.ietf.org/doc/html/rfc8402>
- RFC 8660 — *Segment Routing with the MPLS Data Plane*: <https://datatracker.ietf.org/doc/html/rfc8660>
- RFC 8665 — *OSPF Extensions for Segment Routing*: <https://datatracker.ietf.org/doc/html/rfc8665>
- RFC 8667 — *IS-IS Extensions for Segment Routing*: <https://datatracker.ietf.org/doc/html/rfc8667>
- RFC 9256 — *Segment Routing Policy Architecture*: <https://datatracker.ietf.org/doc/html/rfc9256>
