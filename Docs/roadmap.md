# Roadmap - cenários clássicos de Segment Routing

Índice de todo cenário clássico de SR que este projeto pretende cobrir, exista ou não ainda. Status usados:

- **Concluído** - lab funcional, com configs e verificação.
- **Planejado** - no escopo do projeto, sem lab ainda.
- **Em andamento (branch separada)** - em desenvolvimento por outra pessoa em outra branch, ainda não mergeado em `main`/`feature/sr-mpls`. Listado aqui só para reservar o lugar e evitar retrabalho de estrutura quando mergear.

Para instalar o ambiente, ver [`setup.md`](./setup.md). Para os conceitos, [`base.md`](./base.md).

## Por onde começar

1. [`base.md`](./base.md) - conceitos, convenções, topologia de referência.
2. [`setup.md`](./setup.md) - Docker, Containerlab, imagem XRd.
3. TI-LFA, na ordem: zero-segment -> single-segment -> double-segment -> node-srlg-protection -> microloop-avoidance. Cada lab assume o anterior. Ver [`concepts.md`](../Labs/Cisco/SR-MPLS/TI-LFA/concepts.md) antes do primeiro.
4. SR-TE: [`explicit-policy`](../Labs/Cisco/SR-MPLS/SR-TE/explicit-policy/explicit-policy.md), independente da trilha de TI-LFA.
5. Demais categorias abaixo, conforme forem saindo do papel.


## TI-LFA / Fast Reroute

| Cenário | Status | Onde |
|---|---|---|
| Zero-segment (PQ-node vizinho direto do PLR) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/zero-segment/` |
| Single-segment (PQ-node via Ext P-space) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/single-segment/` |
| Double-segment (P-node + Adj-SID até Q-node) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/double-segment/` |
| Node protection (tiebreaker) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/node-srlg-protection/` |
| SRLG protection (tiebreaker + grupos) | Concluído | `Labs/Cisco/SR-MPLS/TI-LFA/node-srlg-protection/` |
| Microloop avoidance (reconvergência pós-FRR) | Planejado | `Labs/Cisco/SR-MPLS/TI-LFA/microloop-avoidance/` |


## SR-TE / SR Policy

| Cenário | Status | Onde |
|---|---|---|
| Explicit policy (segment list estática, waypoints) | Concluído | `Labs/Cisco/SR-MPLS/SR-TE/explicit-policy/` |
| ODN (On-Demand Nexthop) | Planejado | - |
| Dynamic path via SR-PCE / BGP-LS | Planejado | requer controller externo, fora do escopo XRd-only atual |
| Policy stitching / binding-SID recursivo | Planejado | - |
| Weighted ECMP entre candidate paths | Planejado | - |

## Flexible Algorithm

| Cenário | Status | Onde |
|---|---|---|
| Flex-Algo básico (affinity exclude, SID por algoritmo) | Planejado | existia como referência solta em inglês (`Docs/References/`), removida nesta rodada; será refeita como lab Rede Ipê |
| Flex-Algo com SID anycast de borda entre domínios | Em andamento (branch separada) | `feature/multidomain-ospf` |

## SRv6

| Cenário | Status | Onde |
|---|---|---|
| SRv6 básico (locators, End SIDs) | Planejado | stub vazio removido nesta rodada, sem conteúdo ainda |
| SRv6 Network Programming (uSID) | Planejado | - |

## Multi-domínio / Inter-domínio

| Cenário | Status | Onde |
|---|---|---|
| OSPF multi-processo com DBRs compartilhados + Flex-Algo anycast | Em andamento (branch separada) | `feature/multidomain-ospf`, `Labs/Cisco/SR-MPLS/Multidominio OSPF/` |
| Seamless MPLS / BGP-LU interdomínio | Planejado | - |
| SR-PCE com visão de topologia interdomínio | Planejado | - |

O lab de multi-domínio em desenvolvimento é de outra pessoa. Não foi incorporado nesta rodada de padronização - a entrada acima existe só para reservar o lugar na estrutura e evitar conflito quando a branch for mergeada.

## Multivendor

| Cenário | Status | Onde |
|---|---|---|
| Huawei VRP - equivalente a TI-LFA/SR-TE básicos | Planejado | `feature/multidomain-ospf` tem stub (`Labs/Huawei/`) |
| Juniper Junos - idem | Planejado | idem (`Labs/Juniper/`) |
| Nokia SR OS - idem | Planejado | idem (`Labs/Nokia/`) |
| Interoperabilidade Cisco + outro vendor no mesmo domínio SR | Planejado | - |

Os stubs de vendor vistos em `feature/multidomain-ospf` estão vazios e com caminho incorreto (`Labs/Juniper/Huawei/juniper.md`, `Labs/Nokia/Huawei/nokia.md`) - corrigir o caminho ao mergear, não recriar a partir daqui.

## OAM e operação

| Cenário | Status | Onde |
|---|---|---|
| Verificação básica de plano de controle (neighbors, prefix-sid-map, CEF) | Concluído | coberto em todo lab individual |
| `ping`/`traceroute mpls nil-fec` com stack explícito | Planejado | mencionado em referência removida, sem lab dedicado |
| `traceroute sr-mpls policy` (requer forwarding-plane completo) | Bloqueado | imagem XRd control-plane não suporta; precisa de imagem com forwarding plane |
