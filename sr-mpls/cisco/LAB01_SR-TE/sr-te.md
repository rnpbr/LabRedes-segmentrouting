> Uso interno — material em desenvolvimento.

# Lab 01 | SR-TE 

## O que é

Segment Routing Traffic Engineering (SR-TE) é a evolução do RSVP-TE. Em vez de sinalizar um caminho hop-by-hop pela rede e manter estado em cada nó intermediário, o SR-TE codifica o caminho diretamente no cabeçalho do pacote como um stack de labels MPLS.

O resultado é uma rede stateless: apenas o nó de entrada (headend) precisa ser configurado.

Nenhum roteador intermediário sabe que o caminho existe.

## O que este lab cobre

- Configuração base de SR-MPLS com OSPF
- Criação de SR Policy com Segment List explícita
- Binding-SID como representação abstrata da policy
- Diferença entre caminho IGP (ECMP) e caminho forçado via SR-TE
- Steering de tráfego via rota estática apontando para a SR Policy
- Validação do caminho via traceroute MPLS

## Objetivos

1. Configurar SR-MPLS com OSPF em IOS-XR
2. Criar uma SR Policy com caminho explícito via Segment List
3. Verificar o estado da policy e o Binding-SID na LFIB
4. Direcionar tráfego para a policy e validar o caminho efetivo
5. Compreender a diferença entre o encaminhamento IGP e o encaminhamento SR-TE

## Topologia

![Topologia SR-TE](./topology_sr-te.png)
| Node | Loopback0  | Prefix-SID | Label |
|------|------------|------------|-------|
| R1   | 1.1.1.1/32 | index 1    | 16001 |
| R2   | 1.1.1.2/32 | index 2    | 16002 |
| R3   | 1.1.1.3/32 | index 3    | 16003 |
| R4   | 1.1.1.4/32 | index 4    | 16004 |

O OSPF elege ECMP (Equal-Cost Multi-Path) entre R2 e R3 para alcançar R4. A SR Policy força 100% do tráfego pelo caminho R1 → R3 → R4, ignorando o ECMP do IGP.

## Referencia

- WWT Multi-Domain SR-TE Lab: https://www.wwt.com/lab/multi-domain-sr-te-lab
- RFC 9256 — Segment Routing Policy Architecture: https://datatracker.ietf.org/doc/html/rfc9256
- Cisco IOS-XR SR-TE Configuration Guide: https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x/configure-sr-te-policies.html