# Roadmap de Segment Routing

Cobertura atual e cenários que o projeto pretende desenvolver.

- **Concluído:** lab funcional, com configurações, topologia e roteiro.
- **Planejado:** cenário no escopo, ainda sem lab.
- **Em andamento:** desenvolvimento conhecido ainda não integrado à branch principal.

Para a sequência de leitura e os labs disponíveis, consulte o
[`README.md`](../README.md) do projeto.

## Fundamentos SR-MPLS

| Cenário | Status | Onde |
|---|---|---|
| Prefix-SID, Node-SID, SRGB, SRLB e OSPFv2 com extensões SR | Concluído | [Fundamentos](./concepts/sr-mpls/README.md) e [base Cisco](../labs/cisco/sr-mpls/00-base/) |
| Mesmos fundamentos sobre IS-IS | Planejado | - |
| BGP-LU para estender o alcance MPLS além do IGP | Concluído | [bgp-lu](../labs/cisco/sr-mpls/inter-as/bgp-lu/) |

## TI-LFA / Fast Reroute

| Cenário | Status | Onde |
|---|---|---|
| Zero-segment | Concluído | [zero-segment](../labs/cisco/sr-mpls/ti-lfa/00-zero-segment/) |
| Single-segment | Concluído | [single-segment](../labs/cisco/sr-mpls/ti-lfa/01-single-segment/) |
| Double-segment | Concluído | [double-segment](../labs/cisco/sr-mpls/ti-lfa/02-double-segment/) |
| Node protection e SRLG protection | Concluído | [node-srlg-protection](../labs/cisco/sr-mpls/ti-lfa/03-node-srlg-protection/) |
| Microloop avoidance | Concluído | [microloop-avoidance](../labs/cisco/sr-mpls/ti-lfa/04-microloop-avoidance/) |
| LFA e Remote LFA | Concluído, conceitual | [Conceitos de TI-LFA](./concepts/sr-mpls/ti-lfa.md) |
| TI-LFA sobre IS-IS | Planejado | - |

## SR-TE / SR Policy

| Cenário | Status | Onde |
|---|---|---|
| Explicit policy com segment list estática | Concluído | [explicit-policy](../labs/cisco/sr-mpls/sr-te/explicit-policy/) |
| ODN (On-Demand Nexthop) | Planejado | - |
| Automated Steering por Color BGP | Planejado | [Conceitos de SR-TE](./concepts/sr-mpls/sr-te.md) |
| Dynamic path via SR-PCE / BGP-LS | Planejado | Requer controlador externo |
| Policy stitching / Binding-SID recursivo | Planejado | - |
| Weighted ECMP entre candidate paths | Planejado | - |

## Flexible Algorithm

| Cenário | Status | Onde |
|---|---|---|
| Flex-Algo básico com afinidades e SID por algoritmo | Planejado | - |
| Flex-Algo com SID anycast de borda entre domínios | Em andamento | `feature/multidomain-ospf` |

## SRv6

| Cenário | Status | Onde |
|---|---|---|
| SRv6 básico com locators e End SIDs | Planejado | - |
| SRv6 Network Programming com uSID | Planejado | - |

## Multi-domínio / Interdomínio

| Cenário | Status | Onde |
|---|---|---|
| OSPF multiprocesso com DBRs compartilhados e Flex-Algo anycast | Em andamento | `feature/multidomain-ospf` |
| Seamless MPLS / BGP-LU interdomínio | Concluído | [bgp-lu](../labs/cisco/sr-mpls/inter-as/bgp-lu/) |
| Transporte inter-AS inspirado na Option C, sem a camada VPN | Concluído | [bgp-lu](../labs/cisco/sr-mpls/inter-as/bgp-lu/) |
| L3VPN inter-AS Option C completa | Planejado | O lab atual implementa apenas o substrato de transporte |
| BGP-EPE com PeerNode SID em SR Policy | Concluído | [bgp-lu](../labs/cisco/sr-mpls/inter-as/bgp-lu/) |
| BGP-EPE centralizado com controlador e BGP-LS | Planejado | Requer controlador externo |
| SR-PCE com visão de topologia interdomínio | Planejado | - |

Quando integrado, o lab de multi-domínio deverá entrar em
`labs/cisco/sr-mpls/multidominio-ospf/`, reunindo o `lab.clab.yml`, as
configurações e o roteiro no mesmo diretório.

## Multivendor

| Cenário | Status | Onde |
|---|---|---|
| Huawei VRP, equivalente a TI-LFA e SR-TE básicos | Planejado | `labs/huawei/` |
| Juniper Junos, equivalente aos cenários básicos | Planejado | `labs/juniper/` |
| Nokia SR OS, equivalente aos cenários básicos | Planejado | `labs/nokia/` |
| Interoperabilidade Cisco com outro fabricante no mesmo domínio SR | Planejado | - |
