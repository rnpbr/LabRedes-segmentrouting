# TI-LFA Single-Segment

## Contexto

Este lab assume os conceitos apresentados em [`concepts.md`](../concepts.md) e a fundação de SR-MPLS em [`Docs/base.md`](../../../../../Docs/base.md). Se o cenário Zero-Segment ainda não foi executado, vale rodar aquele primeiro - a diferença entre os dois cenários é justamente o ponto central deste material.

No Zero-Segment, o PQ-node é vizinho direto do PLR: o backup não precisa de nenhum label além do Node-SID do destino, porque "chegar ao PQ-node" é apenas "sair por essa interface física". Aqui o PQ-node está **dois saltos** do PLR - alcançável através de um vizinho, mas não sendo ele próprio vizinho. Isso muda o backup de zero labels adicionais para **um** label adicional: o Node-SID do PQ-node, empilhado abaixo do Node-SID do destino final.

---

## Este lab

Estende a rede do Zero-Segment com dois PoPs novos - RJ e ES - formando um anel de cinco PoPs (SP, RJ, MG, BA, DF) com um PoP adicional (ES) pendurado além de DF. SP continua como PLR, protegendo o link direto SP-DF. A diferença é o destino observado: em vez de calcular o backup para DF (o vizinho do outro lado do link protegido), calculamos para **ES**, um PoP que só existe atrás de DF.

Adjacências: `SP<->DF` (protegido), `SP<->RJ`, `RJ<->MG`, `MG<->BA`, `BA<->DF`, `DF<->ES`. Todos os enlaces com custo **10** - sem artifícios de custo neste lab, o link SP-DF é genuinamente o caminho mais curto até DF (`10` contra `40` dando a volta pelo anel), exatamente como seria em produção.

### Por que single-segment e não zero-segment

Com o link SP-DF fora do ar, o único caminho restante de SP até ES é `SP -> RJ -> MG -> BA -> DF -> ES`. TI-LFA em SP calcula P-space e Q-space **em cima da topologia original** (sem remover o link - apenas verificando, para cada nó, se o caminho mais curto até ele evita usar o link protegido). O ponto que faz single-segment acontecer é que o P-space **direto** de SP não é suficiente - é preciso estender através do vizinho RJ.

**P-space direto(SP, SP-DF)** - nós que SP alcança pelo caminho mais curto sem usar o link SP-DF:

| Nó | Caminho mais curto a partir de SP | Usa SP-DF? | No P-space direto? |
|---|---|:-:|:-:|
| RJ | `SP-RJ` (10) | não | **sim** |
| MG | `SP-RJ-MG` (20) contra `SP-DF-BA-MG` (30) | não | **sim** |
| BA | `SP-DF-BA` (20) contra `SP-RJ-MG-BA` (30) | **sim** | não |

Só RJ e MG. Sozinho, isso não seria suficiente para explicar o backup real - falta estender.

**P-space estendido(SP, SP-DF)** - une o P-space direto de SP com o P-space de cada vizinho remanescente de SP (aqui, só RJ):

| Nó | Caminho mais curto a partir de RJ | Usa SP-DF? | No P-space de RJ? |
|---|---|:-:|:-:|
| MG | `RJ-MG` (10) | não | **sim** |
| BA | `RJ-MG-BA` (20) contra `RJ-SP-DF-BA` (30) | não | **sim** |

P-space estendido = `{RJ, MG}` ∪ `{MG, BA}` = **`{RJ, MG, BA}`**. BA entra aqui porque, do ponto de vista de RJ (não de SP), o caminho mais curto até BA passa por MG e nunca toca o link protegido.

**Q-space(ES, SP-DF)** - nós que alcançam ES pelo caminho mais curto sem usar o link SP-DF:

| Nó | Caminho mais curto até ES | Usa SP-DF? | No Q-space? |
|---|---|:-:|:-:|
| BA | `BA-DF-ES` (20) | não | **sim** |
| MG | `MG-BA-DF-ES` (30) contra `MG-RJ-SP-DF-ES` (40) | não | **sim** |
| RJ | `RJ-SP-DF-ES` (30) contra `RJ-MG-BA-DF-ES` (40) | **sim** | não |

A interseção P-space estendido ∩ Q-space é **`{MG, BA}`** - dois candidatos válidos, não um só. Isso é normal: quando existe mais de um PQ-node possível, a implementação escolhe um segundo critérios próprios (custo do caminho de backup resultante, entre outros) que não fazem parte da formalização RFC - **na prática, o IOS-XR deste lab escolheu BA**.

Backup calculado: `push { prefix-SID(BA) 16007 }` abaixo do `prefix-SID(ES) 16004` já presente no pacote. RJ recebe os dois labels empilhados, olha apenas o topo (16007) e encaminha nativamente até BA (passando fisicamente por MG no caminho, sem que MG precise fazer nada além de forwarding normal) - RJ não precisa saber nada sobre ES, TI-LFA ou a falha. Ao chegar em BA, o topo da pilha (16007) corresponde ao próprio BA, que faz PHP e encaminha o pacote restante (com label 16004) pelo seu caminho nativo até ES via DF.

---

## Topologia

![single-segment](./images/topology-single-segment.png)

> A imagem acima ainda mostra MG como PQ-node - desatualizada em relação ao comportamento real medido neste lab (o IOS-XR escolheu BA). MG e BA são ambos matematicamente válidos como PQ-node; a imagem será atualizada para refletir BA.

O caminho SP->RJ->MG->BA é onde o label extra importa - é a parte "roteada" do backup (MG é atravessado por forwarding nativo comum, não por ser ele mesmo o alvo do label). O caminho BA->DF->ES é encaminhamento nativo, sem SID adicional: uma vez em BA, a rede já sabe levar o pacote até ES sem cruzar o link protegido.

---

## Endereçamento

| PoP | Papel | Loopback0 | SID index | Label | Mgmt |
|---|---|---|---:|---:|---|
| SP | PLR | `10.0.1.254/32` | 1 | 16001 | 172.20.22.11 |
| DF | trânsito (outro lado do link protegido) | `10.0.1.253/32` | 2 | 16002 | 172.20.22.12 |
| RJ | vizinho direto do PLR (P-space) | `10.0.1.252/32` | 3 | 16003 | 172.20.22.13 |
| ES | destino final do backup | `10.0.1.251/32` | 4 | 16004 | 172.20.22.14 |
| MG | candidato a PQ-node (não escolhido) | `10.0.1.250/32` | 5 | 16005 | 172.20.22.15 |
| BA | **PQ-node escolhido pelo IOS-XR** | `10.0.1.248/32` | 7 | 16007 | 172.20.22.17 |

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

O YAML referencia cada arquivo `.cfg` via `startup-config`, então os seis nós já sobem configurados. **Atenção ao redeployar um lab já usado antes**: use sempre `clab destroy -t lab.clab.yml --cleanup` para limpar o diretório do lab; sem o `--cleanup`, o containerlab reaproveita a config antiga presa no diretório em vez de reaplicar do zero.

```bash
sudo clab deploy -t lab.clab.yml
```

Seis XRd control-plane consomem mais RAM que o Zero-Segment (quatro nós) - reserve ao menos 10-12 GB livres antes do deploy. Aguardar alguns minutos para todos os nós inicializarem.

![alt text](image-1.png)

```bash
# Derrubar o lab
sudo clab destroy -t lab.clab.yml --cleanup
```

---

## Verificação

### 1. Adjacências OSPF

Em todos os seis nós:

```
show ospf neighbor
```

![alt text](image.png)

Esperado: `FULL/-` em cada interface de core. SP deve ter exatamente dois vizinhos (DF e RJ). Sem isso, o restante da verificação não faz sentido - o TI-LFA depende de uma base de dados de topologia sincronizada.

### 2. Confirmar que o link SP-DF é mesmo o caminho primário

```
show route 10.0.1.251/32
```

![alt text](image-2.png)

(rota para ES, a Loopback0 de destino). Esperado: next-hop primário via Gi0/0/0/0 (interface para DF), custo total 21, com uma entrada de backup marcada `Backup (TI-LFA)` via Gi0/0/0/1, `Repair Node(s): 10.0.1.248` (BA).

### 3. Backup TI-LFA para ES

```
show cef 10.0.1.251/32 detail
```

![alt text](image-3.png)

Esperado: uma entrada primária via Gi0/0/0/0 (para DF) marcada `protected`, e uma entrada de backup via Gi0/0/0/1 (para RJ) marcada `backup (TI-LFA)` - **não** `Local-LFA`, que é a marcação usada no Zero-Segment quando o backup é um vizinho físico direto do destino.

O campo `labels imposed` na entrada de backup deve mostrar dois labels na pilha: `{16007, 16004}` - 16007 (prefix-SID de BA) no topo, 16004 (prefix-SID de ES) embaixo. `Repair Node(s): 10.0.1.248` confirma BA como o nó de reparo.

### 4. Confirmar o PQ-node

```
show ospf routes 10.0.1.251/32 backup-path
```

![alt text](image-4.png)

Esperado:

```text
O    10.0.1.251/32, metric 21
       via 10.10.12.2, GigabitEthernet0/0/0/0, Protected
         Backup path: TI-LFA, via 10.10.13.2, GigabitEthernet0/0/0/1
           P node: 10.0.1.252 (RJ)   Q node: 10.0.1.248 (BA)
```

O campo mostra o next-hop físico do backup (RJ) e o repair node real (BA) num único print, sem precisar interpretar `labels imposed` manualmente. Esse é o print que fecha a prova do lab - o backup já está instalado na FIB antes de qualquer falha acontecer, o que é o ponto inteiro do TI-LFA (pré-computado, não reativo).

---

## Comparando com Zero-Segment

| | Zero-Segment | Single-Segment |
|---|---|---|
| PQ-node | vizinho direto do PLR | alcançado via um vizinho do PLR (P-space estendido) |
| Labels empilhados pelo PLR | 0 (além do label do destino) | 1 (Node-SID do PQ-node) |
| Marcação em `show cef` | `Local-LFA` | `backup (TI-LFA)` |
| Interpretação do primeiro hop | "sair fisicamente por esta porta" | "usar SR para chegar até o PQ-node" |

A rede é a mesma família - SRGB, convenções de endereçamento e o próprio PLR (SP) idênticos ao Zero-Segment - mas o destino escolhido (ES, atrás de DF, em vez do próprio DF) muda a geometria do problema o suficiente para exigir um segmento a mais.