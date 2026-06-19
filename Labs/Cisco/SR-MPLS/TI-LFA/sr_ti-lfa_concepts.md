# TI-LFA - Topology Independent Loop-Free Alternates
 
## O que é TI-LFA
 
TI-LFA é um mecanismo de **fast reroute** para redes SR-MPLS. Quando um link ou nó falha, o roteador no ponto da falha (PLR - Point of Local Repair) já tem um caminho de backup **pré-calculado** e o ativa em menos de 50ms, sem esperar a reconvergência do IGP.
 
O backup é expresso como uma **SID-list** (stack de labels MPLS) que força o pacote a contornar a falha seguindo exatamente o caminho que a rede adotaria após convergir, garantindo ausência de loops por construção.
 
O Segment Routing (SR) é o paradigma de encaminhamento que viabiliza o TI-LFA. Nele, o caminho de um pacote é codificado no próprio cabeçalho como uma lista ordenada de segmentos (SIDs). No plano de dados MPLS, cada SID é representado por um label. Os principais tipos são:
 
- **Node-SID (Prefix-SID):** identifica um nó na topologia. É globalmente significativo dentro do domínio SR. Deriva do SRGB + índice configurado no nó.
- **Adjacency-SID (Adj-SID):** identifica um enlace específico entre dois nós. É localmente significativo e alocado dinamicamente pelo IGP.
O bloco de labels reservado para uso do SR é o **SRGB (Segment Routing Global Block)**. Neste laboratório o SRGB configurado é `16000-23999`.
 
### Conceitos-chave
 
| Termo | Significado |
|-------|-------------|
| **PLR** | Point of Local Repair - roteador que detecta a falha e ativa o backup |
| **P-space** | Conjunto de nós que o PLR alcança sem cruzar o link ou nó protegido |
| **Q-space** | Conjunto de nós que alcançam o destino sem cruzar o link ou nó protegido |
| **PQ-node** | Nó que pertence simultaneamente ao P-space e ao Q-space |
| **SID-list** | Stack de labels imposta pelo PLR para expressar o caminho de backup |
| **SRGB** | Segment Routing Global Block - intervalo de labels reservado para Prefix-SIDs |
 
O número de labels adicionais na SID-list define o tipo do cenário de proteção:
 
- **Zero-Segment:** o PQ-node é vizinho direto do PLR. Nenhum label adicional é necessário, apenas o Node-SID do destino.
- **One-Segment:** um Prefix-SID adicional é empilhado para direcionar o tráfego até o PQ-node.
- **Two-Segment:** dois Prefix-SIDs adicionais são necessários para alcançar o PQ-node.
---
 