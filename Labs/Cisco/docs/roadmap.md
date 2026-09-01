# Roadmap - cenários clássicos de Segment Routing

Índice de todo cenário clássico de SR que este projeto pretende cobrir, exista ou não ainda. Status usados:

- **Concluído** - lab funcional, com configs, topologia containerlab e roteiro de verificação.
- **Planejado** - no escopo do projeto, sem lab ainda.
- **Em andamento (branch separada)** - em desenvolvimento por outra pessoa em outra branch, ainda não mergeado em `main`. Listado aqui para reservar o lugar e evitar retrabalho de estrutura quando mergear.

Para instruções de instalação e a lista dos labs prontos hoje, ver o [`README.md`](../README.md) na raiz de `Labs/Cisco/`. Este arquivo cobre o quadro completo, incluindo o que ainda não existe.

## Fundamentos SR-MPLS

| Cenário | Status | Onde |
|---|---|---|
| Prefix-SID e node-SID, SRGB e SRLB, OSPFv2 com extensões SR | Concluído | [`base.md`](./base.md) |
| Mesmo fundamento sobre IS-IS em vez de OSPFv2 | Planejado | - |
| BGP-LU (RFC 8277) para estender alcance MPLS além do IGP | Concluído | `Labs/Cisco/SR-MPLS/Inter-AS/bgp-lu/` |

## TI-LFA / Fast Reroute

| Cenário | Status | Onde |
|---|---|---|
| Zero-segment (PQ-node vizinho direto do PLR) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/00-zero-segment/` |
| Single-segment (PQ-node via P-space estendido) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/01-single-segment/` |
| Double-segment (P-node mais Adj-SID até o Q-node) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/02-double-segment/` |
| Node protection (tiebreaker) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/03-node-srlg-protection/` |
| SRLG protection (tiebreaker e grupos) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/03-node-srlg-protection/` |
| Microloop avoidance (reconvergência pós-FRR) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/04-microloop-avoidance/` |
| LFA e Remote LFA (contexto histórico, pré-TI-LFA) | Concluído (conceitual, sem lab próprio) | `concepts.md` e `00-zero-segment/zero-segment.md` |
| TI-LFA sobre IS-IS | Planejado | - |

## SR-TE / SR Policy

| Cenário | Status | Onde |
|---|---|---|
| Explicit policy (segment list estática, waypoints) | Concluído | `Labs/Cisco/SR-MPLS/SR-TE/explicit-policy/` |
| ODN (On-Demand Nexthop) | Planejado | - |
| Automated Steering por Color BGP | Planejado | citado em `SR-MPLS/SR-TE/sr-te_concepts.md`, sem lab |
| Dynamic path via SR-PCE / BGP-LS | Planejado | requer controller externo, fora do escopo XRd-only atual |
| Policy stitching / binding-SID recursivo | Planejado | - |
| Weighted ECMP entre candidate paths | Planejado | - |

## Flexible Algorithm

| Cenário | Status | Onde |
|---|---|---|
| Flex-Algo básico (affinity exclude, SID por algoritmo) | Planejado | será feito como lab Rede Ipê |
| Flex-Algo com SID anycast de borda entre domínios | Em andamento (branch separada) | `feature/multidomain-ospf` |

## SRv6

| Cenário | Status | Onde |
|---|---|---|
| SRv6 básico (locators, End SIDs) | Planejado | - |
| SRv6 Network Programming (uSID) | Planejado | - |

## Multi-domínio / Inter-domínio

| Cenário | Status | Onde |
|---|---|---|
| OSPF multi-processo com DBRs compartilhados e Flex-Algo anycast | Em andamento (branch separada) | `feature/multidomain-ospf` |
| Seamless MPLS / BGP-LU interdomínio | Concluído | `Labs/Cisco/SR-MPLS/Inter-AS/bgp-lu/` |
| Transporte inter-AS estilo Option C (sem a camada VPN) | Concluído | `Labs/Cisco/SR-MPLS/Inter-AS/bgp-lu/` |
| L3VPN inter-AS Option C completa (VPNv4/vpnv6, VRF, RD/RT) | Planejado | o lab `bgp-lu` implementa só o substrato de transporte |
| BGP-EPE com PeerNode SID em SR Policy | Concluído | `Labs/Cisco/SR-MPLS/Inter-AS/bgp-lu/` |
| BGP-EPE centralizado (controlador + BGP-LS, RFC 9087) | Planejado | requer controller externo, fora do escopo XRd-only atual |
| SR-PCE com visão de topologia interdomínio | Planejado | - |

O lab de multi-domínio em desenvolvimento é de outra pessoa. Quando mergear, entra em `Labs/Cisco/SR-MPLS/Multidominio-OSPF/` com o `.clab.yml` em `IaC/Clabs/Cisco/Multidominio-OSPF/`, seguindo o mesmo padrão dos demais.

## Multivendor

| Cenário | Status | Onde |
|---|---|---|
| Huawei VRP, equivalente a TI-LFA e SR-TE básicos | Planejado | `Labs/Huawei/` |
| Juniper Junos, idem | Planejado | `Labs/Juniper/` |
| Nokia SR OS, idem | Planejado | `Labs/Nokia/` |
| Interoperabilidade Cisco com outro vendor no mesmo domínio SR | Planejado | - |
