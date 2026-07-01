# SR Microloop Avoidance

## Contexto

Todos os labs anteriores tratam do intervalo entre a falha e a ativação do backup - o TI-LFA garante que esse intervalo seja coberto em menos de 50ms por um caminho pré-calculado e livre de loops. Este lab trata do que acontece **depois** desse intervalo: a reconvergência "de verdade" do IGP, quando cada roteador do domínio recalcula SPF e atualiza sua FIB para refletir a topologia definitiva.

Esse processo não é instantâneo nem simultâneo entre roteadores - é aí que mora o **microloop**, um problema anterior e independente do Segment Routing, presente em qualquer rede IP com roteamento hop-by-hop. Ver [`sr_ti-lfa_concepts.md`](../sr_ti-lfa_concepts.md) para a explicação completa do mecanismo antes de seguir.

---

## Este lab

Um anel hexagonal de seis PoPs, com um arco curto (dois saltos) e um arco longo (quatro saltos) entre o PLR e o destino:

```text
              SP
             /    \
           RJ      PR
            |        \
           MG          DF
             \        /
               BA ══100══ (último salto do arco longo)
```

Mais precisamente, o ciclo é `SP – PR – DF – BA – MG – RJ – SP`. O arco curto `SP-PR-DF` (custo 10+10=20) é o caminho primário. O arco longo `SP-RJ-MG-BA-DF` (custo 10+10+10+100=130) só é usado se o arco curto estiver indisponível - o último salto do arco longo (BA-DF) tem custo 100 de propósito, simulando um circuito de menor qualidade reservado para contingência.

### O experimento: falha no meio do arco curto

O link testado é `PR-DF` - o segundo salto do caminho primário, mais próximo do destino. Quando ele cai, o único caminho remanescente de SP até DF é o arco longo inteiro: `SP -> RJ -> MG -> BA -> DF`.

O TI-LFA em SP já tem um backup pré-calculado para essa falha, ativo em milissegundos. O ponto deste lab é o que acontece **depois**: à medida que RJ, MG e BA individualmente processam a notificação de topologia (LSA/LSU) e recalculam seu próprio SPF, cada um converge no seu próprio tempo. Nessa janela - tipicamente dezenas a poucas centenas de milissegundos - é possível que, por exemplo, MG já tenha atualizado sua rota para DF apontando para BA, mas BA ainda não tenha atualizado a sua e continue apontando de volta para MG (ou para RJ). Um pacote que chegue nesse instante fica saltando entre nós até que a convergência termine - um **microloop**, com perda de pacotes real, exatamente na janela imediatamente após um evento de FRR, quando o volume de tráfego redirecionado costuma ser maior.

### A mitigação: SID-list temporário

Com `microloop avoidance segment-routing` habilitado, SP não espera a rede convergir organicamente. Assim que detecta a mudança de topologia:

1. Calcula a **SPT pós-convergência** - a topologia final, como ficará depois que RJ, MG e BA tiverem terminado de convergir.
2. Constrói uma SID-list que força o tráfego a seguir exatamente esse caminho final, sem ambiguidade, mesmo que RJ, MG e BA ainda não tenham individualmente chegado à mesma conclusão.
3. Neste lab, essa SID-list é `{ prefix-SID(BA) 16007, Adj-SID(BA->DF) }` - o suficiente para garantir que, uma vez o pacote alcançando BA, ele seja empurrado explicitamente para DF (via Adj-SID) em vez de seguir qualquer rota nativa que BA ainda possa ter desatualizada.
4. Passado o tempo estimado de convergência de todo o domínio, SP remove a SID-list temporária - a rede já está estável e o steering explícito deixou de ser necessário.

---

## Configuração

Uma única linha, no processo OSPF, sem necessidade de configuração por interface:

```text
router ospf 1
 microloop avoidance segment-routing
```

Este lab habilita a flag em todos os seis nós (política uniforme), mas vale lembrar - como destacado em `sr_ti-lfa_concepts.md` - que o benefício é incremental por nó: mesmo habilitar apenas em SP já reduz a contribuição de SP para o problema, independentemente do que RJ, MG e BA estejam fazendo.

TI-LFA continua habilitado normalmente em todas as interfaces (`fast-reroute per-prefix` + `ti-lfa enable`) - microloop avoidance é um complemento ao FRR, não um substituto: FRR cobre o primeiro instante da falha, microloop avoidance cobre a janela de reconvergência que vem logo depois.

---

## Topologia

![SR Microloop Avoidance](./images/topology-microloop-avoidance.png)

Em vermelho, o link testado (PR-DF). Em verde, o arco longo - o caminho pós-convergência, sujeito a microloop entre RJ, MG e BA enquanto a rede converge organicamente. Em dourado, o último salto do arco longo (BA-DF, custo 100), o trecho final coberto pelo Adj-SID no SID-list temporário.

---

## Endereçamento

| PoP | Papel | Loopback0 | SID index | Label | Mgmt |
|---|---|---|---:|---:|---|
| SP | PLR / origina o SID-list temporário | `10.0.1.254/32` | 1 | 16001 | 172.20.25.11 |
| PR | arco curto | `10.0.1.249/32` | 6 | 16006 | 172.20.25.16 |
| DF | destino | `10.0.1.253/32` | 2 | 16002 | 172.20.25.12 |
| BA | arco longo, último salto | `10.0.1.248/32` | 7 | 16007 | 172.20.25.17 |
| MG | arco longo | `10.0.1.250/32` | 5 | 16005 | 172.20.25.15 |
| RJ | arco longo | `10.0.1.252/32` | 3 | 16003 | 172.20.25.13 |

| Link | Subnet | Custo |
|---|---|---:|
| SP-PR | 10.10.16.0/30 | 10 |
| PR-DF (falha testada) | 10.10.26.0/30 | 10 |
| DF-BA | 10.10.27.0/30 | 100 |
| BA-MG | 10.10.57.0/30 | 10 |
| MG-RJ | 10.10.35.0/30 | 10 |
| RJ-SP | 10.10.13.0/30 | 10 |

---

## Deploy

```bash
mkdir -p ~/labs/sr-mpls/cisco/tilfa-microloop-avoidance
cd ~/labs/sr-mpls/cisco/tilfa-microloop-avoidance
cp IaC/Clabs/Cisco/ti_lfa_rede-ipe/tilfa-microloop-avoidance.yml lab.clab.yml
cp -r TI-LFA/microloop-avoidance/configs .
sudo clab deploy -t lab.clab.yml
```

```bash
# Derrubar o lab
sudo clab destroy -t lab.clab.yml
```

---

## Verificação

### 1. Adjacências OSPF e caminho primário

```
show ospf neighbor
show route 10.0.1.253/32
```

Esperado: adjacências `FULL/-` em todos os seis nós; rota para DF via PR, custo 20 (arco curto).

### 2. Confirmar a flag ativa

```
show running-config router ospf 1 | include microloop
```

Esperado: `microloop avoidance segment-routing` presente na saída, em cada um dos seis nós.

### 3. Backup TI-LFA (o instantâneo, sub-50ms)

```
show cef 10.0.1.253/32 detail
```

Confirma que já existe um backup TI-LFA pré-instalado para a falha do link PR-DF, independente do microloop avoidance - este é o mecanismo que cobre o primeiro instante, antes mesmo de a reconvergência começar.

### 4. Observar o SID-list temporário durante a falha

Este é o passo mais sensível a timing - a janela em que o SID-list temporário existe é curta. Em um terminal separado, prepare-se para consultar SP imediatamente após derrubar o link:

Em PR:

```
conf t
interface GigabitEthernet0/0/0/1
 shutdown
commit
end
```

Imediatamente em SP:

```
show ospf mpls traffic-eng
show mpls forwarding
```

Nos primeiros instantes após a falha (antes de a rede convergir por completo), a entrada MPLS para o label de DF deve apresentar uma pilha de dois labels - o Prefix-SID de BA seguido do Adj-SID de BA para DF - em vez do encaminhamento nativo de estado estável de um único label. Depois de alguns segundos, repetir o comando deve mostrar a entrada já simplificada, sem o SID-list adicional: a rede convergiu e SP removeu o steering temporário.

### 5. Caminho final, em regime permanente

```
traceroute 10.0.1.253 source 10.0.1.254
```

Esperado, já em regime estável (alguns segundos após a falha): quatro saltos pelo arco longo -

```
1  10.10.13.2   (RJ)
2  10.10.35.2   (MG)
3  10.10.57.2   (BA)
4  10.10.27.1   (DF, ultimo hop, custo 100 no ultimo salto)
```

Esse é o caminho pós-convergência nativo - o mesmo que o SID-list temporário já estava forçando durante a janela de reconvergência, só que agora sem precisar de nenhum steering explícito, porque todos os nós já concordam com a nova topologia.

---

## Por que isso é difícil de "ver" de forma determinística

Diferente de TI-LFA (onde o backup fica instalado esperando, visível a qualquer momento via `show cef`), o SID-list de microloop avoidance só existe durante a janela de reconvergência propriamente dita - potencialmente algumas centenas de milissegundos em uma rede pequena como esta. Capturar esse estado exige rodar o `show` quase simultaneamente à falha, e o resultado pode variar de execução para execução dependendo de quão rápido o XRd processa a notificação. O objetivo deste lab não é garantir reproduzir o estado transitório em todo teste, mas entender exatamente o que aconteceria e por quê - e, quando a janela for capturada com sucesso, confirmar visualmente a pilha de labels temporária descrita acima.
