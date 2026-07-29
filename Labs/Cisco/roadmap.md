# Roadmap - cenários clássicos de Segment Routing

Índice de todo cenário clássico de SR que este projeto pretende cobrir, exista ou não ainda. Status usados:

- **Concluído** - lab funcional, com configs, topologia containerlab e roteiro de verificação.
- **Planejado** - no escopo do projeto, sem lab ainda.
- **Em andamento (branch separada)** - em desenvolvimento por outra pessoa em outra branch, ainda não mergeado em `main`. Listado aqui para reservar o lugar e evitar retrabalho de estrutura quando mergear.

Para instalar o ambiente, ver [`setup.md`](./setup.md). Para os conceitos e convenções, [`base.md`](./base.md). Índice de labs com descrição curta, [`cisco-sr.md`](./cisco-sr.md).

## Por onde começar

1. [`base.md`](./base.md) - conceitos, convenções, topologia de referência.
2. [`setup.md`](./setup.md) - Docker, Containerlab, imagem XRd.
3. TI-LFA, nesta ordem: zero-segment, single-segment, double-segment, node-srlg-protection, microloop-avoidance. Cada lab assume o anterior. Ler [`concepts.md`](./SR-MPLS/TI-LFA/concepts.md) antes do primeiro.
4. SR-TE: [`explicit-policy`](./SR-MPLS/SR-TE/explicit-policy/explicit-policy.md), independente da trilha de TI-LFA. Conceitos em [`concepts.md`](./SR-MPLS/SR-TE/concepts.md).
5. Demais categorias abaixo, conforme forem saindo do papel.

## Fundamentos SR-MPLS

| Cenário | Status | Onde |
|---|---|---|
| Prefix-SID e node-SID, SRGB e SRLB, OSPFv2 com extensões SR | Concluído | [`base.md`](./base.md) |
| Mesmo fundamento sobre IS-IS em vez de OSPFv2 | Planejado | - |
| BGP-LU (RFC 8277) para estender alcance MPLS além do IGP | Planejado | citado no glossário de `base.md`, sem lab |

## TI-LFA / Fast Reroute

| Cenário | Status | Onde |
|---|---|---|
| Zero-segment (PQ-node vizinho direto do PLR) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/zero-segment/` |
| Single-segment (PQ-node via P-space estendido) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/single-segment/` |
| Double-segment (P-node mais Adj-SID até o Q-node) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/double-segment/` |
| Node protection (tiebreaker) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/node-srlg-protection/` |
| SRLG protection (tiebreaker e grupos) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/node-srlg-protection/` |
| Microloop avoidance (reconvergência pós-FRR) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/microloop-avoidance/` |
| LFA e Remote LFA (contexto histórico, pré-TI-LFA) | Concluído (conceitual, sem lab próprio) | `concepts.md` e `zero-segment.md` |
| TI-LFA sobre IS-IS | Planejado | - |

## SR-TE / SR Policy

| Cenário | Status | Onde |
|---|---|---|
| Explicit policy (segment list estática, waypoints) | Concluído | `Labs/Cisco/SR-MPLS/SR-TE/explicit-policy/` |
| ODN (On-Demand Nexthop) | Planejado | - |
| Automated Steering por Color BGP | Planejado | citado em `SR-MPLS/SR-TE/concepts.md`, sem lab |
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
| Seamless MPLS / BGP-LU interdomínio | Planejado | - |
| SR-PCE com visão de topologia interdomínio | Planejado | - |

O lab de multi-domínio em desenvolvimento é de outra pessoa. Quando mergear, entra em `Labs/Cisco/SR-MPLS/Multidominio-OSPF/` com o `.clab.yml` em `IaC/Clabs/Cisco/Multidominio-OSPF/`, seguindo o mesmo padrão dos demais.

## Multivendor

| Cenário | Status | Onde |
|---|---|---|
| Huawei VRP, equivalente a TI-LFA e SR-TE básicos | Planejado | `Labs/Huawei/` |
| Juniper Junos, idem | Planejado | `Labs/Juniper/` |
| Nokia SR OS, idem | Planejado | `Labs/Nokia/` |
| Interoperabilidade Cisco com outro vendor no mesmo domínio SR | Planejado | - |
