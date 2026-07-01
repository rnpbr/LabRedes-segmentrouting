# TI-LFA - Topology Independent Loop-Free Alternates
 
## O que é TI-LFA
 
TI-LFA é um mecanismo de **fast reroute** para redes SR-MPLS. Quando um link ou node falha, o roteador no ponto da falha (PLR - Point of Local Repair) já tem um caminho de backup **pré-calculado** e o ativa em menos de 50ms, sem esperar a reconvergência do IGP.
 
O backup é expresso como uma **SID-list** (stack de labels MPLS) que força o pacote a contornar a falha seguindo exatamente o caminho que a rede adotaria após convergir, garantindo ausência de loops por construção.
 
O Segment Routing (SR) é o paradigma de encaminhamento que viabiliza o TI-LFA. Nele, o caminho de um pacote é codificado no próprio cabeçalho como uma lista ordenada de segmentos (SIDs). No plano de dados MPLS, cada SID é representado por um label. Os principais tipos são:
 
- **Node-SID (Prefix-SID):** identifica um node na topologia. É globalmente significativo dentro do domínio SR. Deriva do SRGB + índice configurado no node.
- **Adjacency-SID (Adj-SID):** identifica um enlace específico entre dois nós. É localmente significativo e alocado dinamicamente pelo IGP.
O bloco de labels reservado para uso do SR é o **SRGB (Segment Routing Global Block)**. Neste laboratório o SRGB configurado é `16000-23999`.
 
### Conceitos-chave
 
| Termo | Significado |
|-------|-------------|
| **PLR** | Point of Local Repair - roteador que detecta a falha e ativa o backup |
| **P-space** | Conjunto de nós que o PLR alcança sem cruzar o link ou node protegido |
| **Q-space** | Conjunto de nós que alcançam o destino sem cruzar o link ou node protegido |
| **PQ-node** | Node que pertence simultaneamente ao P-space e ao Q-space |
| **SID-list** | Stack de labels imposta pelo PLR para expressar o caminho de backup |
| **SRGB** | Segment Routing Global Block - intervalo de labels reservado para Prefix-SIDs |
 
O número de labels adicionais na SID-list define o tipo do cenário de proteção:
 
- **Zero-Segment:** o PQ-node é vizinho direto do PLR. Nenhum label adicional é necessário, apenas o Node-SID do destino.
- **One-Segment:** um Prefix-SID adicional é empilhado para direcionar o tráfego até o PQ-node.
- **Two-Segment:** dois Prefix-SIDs adicionais são necessários para alcançar o PQ-node.
---
 
## Extended P-space e a origem do single-segment / double-segment

A definição de P-space acima é o caso não-estendido: nós que o próprio PLR alcança, via caminho mais curto, sem cruzar o recurso protegido. Na prática, o **P-space estendido** (Ext P-space) é maior: é a união do P-space de cada vizinho remanescente do PLR (todo vizinho que não seja a outra ponta do link protegido). Isso importa porque o PQ-node nem sempre é vizinho direto do PLR - pode estar dois ou mais saltos de distância, desde que o caminho mais curto até ele (calculado a partir do PLR, sem usar o recurso protegido) já passe por um vizinho do PLR.

O número de labels adicionais empilhados pelo PLR além do Prefix-SID do destino define o cenário:

- **Zero-Segment:** o PQ-node é vizinho direto do PLR (está no P-space não-estendido). Nenhum label adicional - o PLR simplesmente encaminha fisicamente para o vizinho, que já está tanto no P-space quanto no Q-space.
- **Single-Segment** (um segmento adicional): o PQ-node está no P-space *estendido* mas não é vizinho direto - é alcançado através de um vizinho do PLR. O PLR empilha `{ prefix-SID(PQ-node) }` sobre o label do destino; o vizinho intermediário encaminha nativamente até o PQ-node, que por sua vez já enxerga o destino sem cruzar o recurso protegido.
- **Double-Segment** (dois segmentos adicionais): P-space e Q-space não se intersectam em nenhum node, mas existe um node do P-space (P-node) adjacente a um node do Q-space (Q-node). O PLR empilha `{ prefix-SID(P-node), adj-SID(P-node->Q-node) }`. O Adj-SID força a travessia daquele enlace específico independentemente do seu custo IGP - é o que permite "costurar" P-space e Q-space quando o caminho mais curto natural não faz a ponte entre eles.

Em topologias reais nem sempre existe um P-node adjacente a um Q-node; nesses casos raros, IOS-XR pode precisar de mais de dois segmentos, mas o algoritmo (proprietário, fora do escopo de padronização do IETF) é dimensionado para cobrir a esmagadora maioria dos casos práticos com no máximo alguns poucos segmentos.

## Node protection e SRLG protection

TI-LFA pode proteger três tipos de recurso, em ordem crescente de exigência:

- **Link protection:** protege apenas contra a falha do enlace específico. É a proteção mínima e sempre implícita - node protection e SRLG protection sempre implicam link protection.
- **Node protection:** o backup contorna completamente o próximo salto, não apenas o enlace até ele. Necessário porque falhas de link são estatisticamente muito mais comuns que falhas de node, mas quando um node inteiro cai (falha de hardware, reload, perda de energia), um backup que só evita o *link* ainda tentaria atravessar o node morto.
- **SRLG protection (Shared Risk Link Group):** protege contra a falha correlacionada de múltiplos enlaces que compartilham um recurso físico comum (mesmo duto, mesmo poste, mesma rota de fibra, mesmo cartão de linha). Um backup que reusa um enlace do mesmo SRLG do enlace protegido não oferece proteção real: se os dois links realmente compartilham o mesmo risco físico, o evento que derrubou um provavelmente derruba o outro também.

Como cada node pode ter mais de um candidato a backup - um mais barato mas menos protegido, outro mais caro mas com cobertura melhor - o IOS-XR usa **tiebreakers** configuráveis por interface para decidir qual característica priorizar quando os candidatos não coincidem em um único caminho:

```text
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/X
   fast-reroute per-prefix
   fast-reroute per-prefix ti-lfa enable
   fast-reroute per-prefix tiebreaker node-protecting index 200
   fast-reroute per-prefix tiebreaker srlg-disjoint index 100
```

Regras práticas:

- **Link protection** tem sempre a prioridade mais baixa e não é configurável - é a base sobre a qual as demais se constroem.
- Quanto **maior o índice**, maior a preferência. Nesse exemplo, `node-protecting` (200) é preferido sobre `srlg-disjoint` (100) quando as duas propriedades não puderem ser satisfeitas ao mesmo tempo pelo mesmo caminho.
- Quando um único caminho satisfaz as duas propriedades simultaneamente (o caso mais comum e o demonstrado no lab `node-srlg-protection`), o tiebreaker apenas confirma a escolha - o `show` correspondente reporta `TI-LFA (node+srlg)`.
- SRLG é um atributo do **enlace**, não do node - precisa ser declarado localmente em cada roteador dono de uma ponta do enlace, e é distribuído aos demais roteadores do domínio via extensões do IGP.

## SR Microloop Avoidance

TI-LFA resolve o intervalo entre a falha e a reconvergência (backup pré-computado, ativado em milissegundos). Mas depois desse intervalo inicial, a rede ainda precisa fazer a reconvergência "de verdade": todo roteador recalcula SPF e atualiza sua FIB para refletir a nova topologia. Esse processo não é instantâneo nem simultâneo - cada roteador converge no seu próprio tempo, dependendo de quando recebeu o LSA/LSU e de quanto SPF+FIB update demoram localmente.

Essa **janela de convergência assimétrica** é a origem do **microloop**: um problema anterior e independente do SR, presente em qualquer rede IP desde sempre (RFC-clássico, "day-one IP drawback"). Se o roteador A já atualizou sua rota para um destino D e passou a apontar para o roteador B, mas B ainda não atualizou a sua e continua apontando de volta para A, um pacote que chegue nesse instante fica saltando entre A e B até que B termine de convergir - um loop transitório, tipicamente da ordem de dezenas a poucas centenas de milissegundos, mas suficiente para gerar perda de pacotes perceptível, especialmente logo após um evento de FRR (quando o volume de tráfego re-roteado é maior).

**SR Microloop Avoidance** ataca esse problema usando o mesmo mecanismo de steering explícito do TI-LFA, mas num momento diferente do ciclo de vida da falha:

1. O node detecta a mudança de topologia (a mesma notificação que também aciona o TI-LFA).
2. Além do backup imediato, o node calcula a **SPT pós-convergência** (a topologia final, depois que todos os roteadores tiverem convergido) e verifica, para cada destino, se o caminho pós-convergência natural passaria por um microloop.
3. Onde houver risco, o node constrói uma **SID-list temporária** que força o tráfego a seguir exatamente o caminho pós-convergência, sem ambiguidade, mesmo enquanto os nós intermediários ainda não convergiram individualmente.
4. Passado o tempo estimado de convergência de todo o domínio, o node remove a SID-list temporária e volta a encaminhar nativamente - a rede já está no estado estável e a SID-list deixou de ser necessária.

Configuração (idêntica em espírito à do TI-LFA, mas é uma flag única no processo IGP, não por interface):

```text
router ospf 1
 microloop avoidance segment-routing
```

Dois pontos importantes:

- **Microloop avoidance é um comportamento local.** Cada node decide, sozinho, impor ou não a SID-list temporária para o tráfego que ele origina ou repassa. Não é preciso habilitar em todos os nós do domínio para obter benefício - cada node habilitado reduz sua própria contribuição para o problema, incrementalmente.
- Diferente do TI-LFA (que reage a um evento local - a interface caiu), o microloop avoidance reage à notificação da mudança de topologia via IGP, então também se aplica a falhas detectadas por um node remoto, não apenas ao PLR direto.
