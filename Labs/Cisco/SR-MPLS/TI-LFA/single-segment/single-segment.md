# TI-LFA Single-Segment

## Contexto

Este lab assume os conceitos apresentados em [`concepts.md`](../concepts.md) e a fundação de SR-MPLS em [`Docs/base.md`](../../../../../Docs/base.md). Se o cenário Zero-Segment ainda não foi executado, vale rodar aquele primeiro - a diferença entre os dois cenários é justamente o ponto central deste material.

No Zero-Segment, o PQ-node é vizinho direto do PLR: o backup não precisa de nenhum label além do Node-SID do destino, porque "chegar ao PQ-node" é apenas "sair por essa interface física". Aqui o PQ-node está **dois saltos** do PLR - alcançável através de um vizinho, mas não sendo ele próprio vizinho. Isso muda o backup de zero labels adicionais para **um** label adicional: o Node-SID do PQ-node, empilhado abaixo do Node-SID do destino final.

---

## Este lab

Estende a rede do Zero-Segment com dois PoPs novos - RJ e ES - formando um anel de cinco PoPs (SP, RJ, MG, BA, DF) com um PoP adicional (ES) pendurado além de DF. SP continua como PLR, protegendo o link direto SP-DF. A diferença é o destino observado: em vez de calcular o backup para DF (o vizinho do outro lado do link protegido), calculamos para **ES**, um PoP que só existe atrás de DF.

```text
        SP ─────────────────── DF ─── ES
         \                     /
          \                   /
           RJ ─── MG ─── BA ─┘
```

Adjacências: `SP↔DF` (protegido), `SP↔RJ`, `RJ↔MG`, `MG↔BA`, `BA↔DF`, `DF↔ES`. Todos os enlaces com custo **10** - sem artifícios de custo neste lab, o link SP-DF é genuinamente o caminho mais curto até DF (`10` contra `40` dando a volta pelo anel), exatamente como seria em produção.

### Por que single-segment e não zero-segment

Com o link SP-DF fora do ar, o único caminho restante de SP até ES é `SP -> RJ -> MG -> BA -> DF -> ES`. O TI-LFA em SP calcula P-space e Q-space **em cima da topologia original** (sem remover o link - apenas verificando, para cada nó, se o caminho mais curto até ele evita usar o link protegido):

**P-space(SP, SP-DF)** - nós que SP alcança pelo caminho mais curto sem usar o link SP-DF:

| Nó | Caminho mais curto a partir de SP | Usa SP-DF? | No P-space? |
|---|---|:-:|:-:|
| RJ | `SP-RJ` (10) | não | **sim** |
| MG | `SP-RJ-MG` (20) contra `SP-DF-BA-MG` (30) | não | **sim** |
| BA | `SP-DF-BA` (20) contra `SP-RJ-MG-BA` (30) | **sim** | não |

**Q-space(ES, SP-DF)** - nós que alcançam ES pelo caminho mais curto sem usar o link SP-DF:

| Nó | Caminho mais curto até ES | Usa SP-DF? | No Q-space? |
|---|---|:-:|:-:|
| BA | `BA-DF-ES` (20) | não | **sim** |
| MG | `MG-BA-DF-ES` (30) contra `MG-RJ-SP-DF-ES` (40) | não | **sim** |
| RJ | `RJ-SP-DF-ES` (30) contra `RJ-MG-BA-DF-ES` (40) | **sim** | não |

A interseção P-space ∩ Q-space é **{MG}**. RJ - o vizinho direto de SP - cai fora do Q-space, porque o caminho mais curto de RJ até ES depende exatamente do link que acabou de falhar. MG entra nos dois conjuntos, mas não é vizinho de SP: está a dois saltos, alcançável através de RJ. Esse é o padrão que caracteriza o **single-segment**: o PQ-node existe, mas só aparece quando se estende o P-space através de um vizinho do PLR (RJ), não no P-space direto do próprio PLR.

Backup calculado: `push { prefix-SID(MG) 16005 }` abaixo do `prefix-SID(ES) 16004` já presente no pacote. RJ recebe os dois labels empilhados, olha apenas o topo (16005) e encaminha nativamente até MG pelo seu próprio caminho mais curto - RJ não precisa saber nada sobre ES, TI-LFA ou a falha. Ao chegar em MG, o topo da pilha (16005) corresponde ao próprio MG, que faz PHP e encaminha o pacote restante (com label 16004) pelo seu caminho nativo até ES via BA-DF.

---

## Topologia

![single-segment](./images/topology-single-segment.png)

MG (verde) é o PQ-node: está na interseção de P-space e Q-space, mas fora do alcance direto de SP. O caminho verde (SP->RJ->MG) é onde o label extra importa - é a parte "roteada" do backup. O caminho azul (MG->BA->DF->ES) é encaminhamento nativo, sem SID adicional: uma vez em MG, a rede já sabe levar o pacote até ES sem cruzar o link protegido.

---

## Endereçamento

| PoP | Papel | Loopback0 | SID index | Label | Mgmt |
|---|---|---|---:|---:|---|
| SP | PLR | `10.0.1.254/32` | 1 | 16001 | 172.20.22.11 |
| DF | trânsito (outro lado do link protegido) | `10.0.1.253/32` | 2 | 16002 | 172.20.22.12 |
| RJ | vizinho direto do PLR (P-space) | `10.0.1.252/32` | 3 | 16003 | 172.20.22.13 |
| ES | destino final do backup | `10.0.1.251/32` | 4 | 16004 | 172.20.22.14 |
| MG | **PQ-node** | `10.0.1.250/32` | 5 | 16005 | 172.20.22.15 |
| BA | trânsito | `10.0.1.248/32` | 7 | 16007 | 172.20.22.17 |

| Link | Subnet | Custo |
|---|---|---:|
| SP-DF (protegido) | 10.10.12.0/30 | 10 |
| SP-RJ | 10.10.13.0/30 | 10 |
| RJ-MG | 10.10.35.0/30 | 10 |
| MG-BA | 10.10.57.0/30 | 10 |
| BA-DF | 10.10.27.0/30 | 10 |
| DF-ES | 10.10.24.0/30 | 10 |

SRGB `16000-23999`, sem `local-block` explícito - Adj-SIDs saem do range dinâmico logo acima do SRGB (a partir de 24000), mesma convenção do Zero-Segment.

---

## Deploy

```bash
mkdir -p ~/labs/sr-mpls/cisco/ti-lfa/single-segment
cd ~/labs/sr-mpls/cisco/ti-lfa/single-segment
```

Copiar a topologia e as configurações do repositório:

```bash
cp IaC/Clabs/Cisco/ti-lfa/single-segment.yml lab.clab.yml
cp -r Labs/Cisco/SR-MPLS/TI-LFA/single-segment/configs .
```

O YAML referencia cada arquivo `.cfg` via `startup-config`, então os seis nós já sobem configurados - não é necessário aplicar manualmente, embora a tabela de endereçamento acima sirva de referência caso seja preciso revisar algo via `ssh clab@<mgmt-ip>` (senha `clab@123`).

```bash
sudo clab deploy -t lab.clab.yml
```

Seis XRd control-plane consomem mais RAM que o Zero-Segment (quatro nós) - reserve ao menos 7-8 GB livres antes do deploy. Aguardar alguns minutos para todos os nós inicializarem.

```bash
# Derrubar o lab
sudo clab destroy -t lab.clab.yml
```

---

## Verificação

### 1. Adjacências OSPF

Em todos os seis nós:

```
show ospf neighbor
```

Esperado: `FULL/-` em cada interface de core. SP deve ter exatamente dois vizinhos (DF e RJ). Sem isso, o restante da verificação não faz sentido - o TI-LFA depende de uma base de dados de topologia sincronizada.

### 2. Confirmar que o link SP-DF é mesmo o caminho primário

```
show route 10.0.1.251/32
```

(rota para ES, a Loopback0 de destino). Esperado: next-hop único via Gi0/0/0/0 (interface para DF), custo total 20 - dois saltos de custo 10, SP-DF e DF-ES. Se aparecer ECMP ou um custo diferente, revise as configurações de custo nas interfaces antes de prosseguir.

### 3. Backup TI-LFA para ES

```
show cef 10.0.1.251/32 detail
```

Esperado: uma entrada primária via Gi0/0/0/0 (para DF) marcada `protected`, e uma entrada de backup via Gi0/0/0/1 (para RJ) marcada `TI-LFA` - **não** `Local-LFA`, que é a marcação usada no Zero-Segment quando o backup é um vizinho físico direto do destino. A ausência de `Local-LFA` aqui é o primeiro sinal visual de que o backup não é mais "zero-segmento".

O campo `labels imposed` na entrada de backup deve mostrar dois labels na pilha: `{16005, 16004}` - 16005 (prefix-SID de MG) no topo, 16004 (prefix-SID de ES) embaixo. Esse par é exatamente o resultado do cálculo de P-space/Q-space feito acima.

### 4. Confirmar o PQ-node via show ospf segment-routing

```
show ospf segment-routing prefix-sid-map active-policy
```

Confirma que todos os seis PoPs anunciam corretamente seus prefix-SIDs - MG deve aparecer com index 5, ES com index 4, e assim por diante, batendo com a tabela de endereçamento.

### 5. Simulação de falha

Em SP:

```
conf t
interface GigabitEthernet0/0/0/0
 shutdown
commit
end
```

Depois:

```
traceroute 10.0.1.251 source 10.0.1.254
```

Esperado: três saltos -

```
1  10.10.13.2  [MPLS: Label 16005 Exp 0]   (RJ)
2  10.10.35.2  [MPLS: Label 16004 Exp 0]   (MG)
3  10.10.24.2                              (ES, ultimo hop, label removido)
```

O primeiro salto (RJ) mostra os **dois labels empilhados** sendo carregados - RJ não faz pop de nada, apenas encaminha olhando o topo (16005). O segundo salto (MG) mostra só o label 16004: MG já fez PHP do seu próprio label (16005, o topo, correspondia a ele) e repassa o pacote com o label restante, exatamente como aconteceria em qualquer encaminhamento SR normal a partir dali - MG não sabe que está participando de um backup TI-LFA, apenas está fazendo swap/pop de rótulos da forma de sempre.

Isso é o cerne do single-segment: um único hop adicional de "roteamento explícito" (SP->RJ, sob controle do label extra) antes de o pacote reentrar em encaminhamento nativo pelo resto do caminho.

---

## Comparando com Zero-Segment

| | Zero-Segment | Single-Segment |
|---|---|---|
| PQ-node | vizinho direto do PLR | alcançado via um vizinho do PLR (Ext P-space) |
| Labels empilhados pelo PLR | 0 (além do label do destino) | 1 (Node-SID do PQ-node) |
| Marcação em `show cef` | `Local-LFA` | `TI-LFA` |
| Interpretação do primeiro hop | "sair fisicamente por esta porta" | "usar SR para chegar até o PQ-node" |

A rede é a mesma família - SRGB, convenções de endereçamento e o próprio PLR (SP) idênticos ao Zero-Segment - mas o destino escolhido (ES, atrás de DF, em vez do próprio DF) muda a geometria do problema o suficiente para exigir um segmento a mais.
