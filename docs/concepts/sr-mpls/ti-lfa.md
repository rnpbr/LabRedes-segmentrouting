# TI-LFA — conceitos

> Pré-requisito: [fundamentos de SR-MPLS](./README.md).
> Implementações Cisco: [trilha de TI-LFA](../../../labs/cisco/README.md#ti-lfa).

## O que é

TI-LFA é o fast reroute do Segment Routing, padronizado na RFC 9855.

Quando um link ou nó cai, o roteador do lado da falha (o PLR, Point of Local Repair) já tem um caminho de backup pronto na FIB. Ele comuta em menos de 50ms, sem esperar o IGP reconvergir.

Isso existe porque reconvergência não é instantânea. Cada roteador recalcula SPF no próprio tempo, e nessa janela o tráfego cai se não houver backup pronto.

## De LFA a TI-LFA

- **LFA** (RFC 5286): usa um vizinho como backup, desde que o caminho dele até o destino não volte pelo PLR. Simples, mas em muitas topologias nenhum vizinho serve.
- **Remote LFA** (RFC 7490): estende o LFA com um túnel LDP até um nó mais distante. Cobre mais casos, mas exige LDP.
- **TI-LFA** (RFC 9855): usa uma pilha de labels SR para alcançar o nó de reparo. Não precisa de LDP nem de o nó ser vizinho. Cobertura garantida em qualquer rede duplamente conectada.

O backup do TI-LFA é sempre o **caminho pós-convergência**, ou seja, o caminho que a rede vai usar depois de convergir. Isso evita ter que escolher entre vários backups possíveis na mão.

## P-space, Q-space e PQ-node

A pergunta central: como o PLR leva o tráfego até um nó que já sabe chegar ao destino sem cruzar a falha?

- **P-space**: nós que o PLR alcança pelo caminho mais curto sem usar o recurso que falhou.
- **P-space estendido**: o P-space do PLR mais o P-space de cada vizinho que sobrou. Serve para alcançar nós que estão a dois ou mais saltos.
- **Q-space**: nós que alcançam o destino pelo caminho mais curto sem usar o recurso que falhou.

Um nó que está nos dois conjuntos é um **PQ-node**. O PLR só precisa levar o tráfego até ele.

Quando existe mais de um PQ-node válido, a escolha fica a cargo da
implementação. Na prática, a seleção deve ser confirmada no estado de
encaminhamento da plataforma, não deduzida apenas pela topologia.

## Zero, single e double-segment

O nome do cenário vem de quantos labels o PLR empilha **além** do label do destino:

| Cenário | Situação | Labels extras | Pilha |
|---|---|:-:|---|
| Zero-segment | PQ-node é vizinho direto do PLR | 0 | `{dest}` |
| Single-segment | PQ-node está no P-space estendido | 1 | `{PQ, dest}` |
| Double-segment | P-space e Q-space não se cruzam | 2 | `{P-node, adj-SID, dest}` |

No double-segment, o Adj-SID força a passagem por um enlace específico, ignorando o custo IGP dele. É o que costura o P-space ao Q-space quando o caminho mais curto não faz essa ponte.

Casos com mais de dois segmentos existem, mas são raros. A RFC 9855 mediu redes reais: para proteção de link e de SRLG, 1 segmento cobre mais de 99% dos prefixos; para proteção de nó, 2 segmentos cobrem 99%. Por isso a trilha de labs para no double-segment.

## Proteção de nó e de SRLG

TI-LFA protege três coisas, em ordem crescente de exigência:

- **Link**: só o enlace. É a proteção mínima, sempre ativa.
- **Nó**: o backup contorna o próximo salto inteiro, não só o enlace até ele. Necessário quando o roteador vizinho cai por completo.
- **SRLG** (Shared Risk Link Group): o backup evita enlaces que compartilham risco físico com o protegido, como mesmo duto, mesmo poste ou mesmo cartão. Um backup no mesmo SRLG não protege de verdade, porque o evento que derruba um enlace tende a derrubar o outro.

Quando há mais de um backup candidato, a implementação usa critérios de
desempate para priorizar propriedades como proteção de nó e disjunção de SRLG.
O SRLG é um atributo do enlace e precisa ser anunciado de maneira consistente
para que o cálculo evite todos os recursos sujeitos ao mesmo risco.

## Microloops

TI-LFA cobre o instante da falha. Não cobre a reconvergência que vem logo depois.

Nessa janela aparece o **microloop**: A já atualizou a rota e aponta para B, mas B ainda aponta de volta para A. Os pacotes ficam saltando entre os dois até B terminar de convergir. Dura de dezenas a centenas de milissegundos e causa perda, jitter e pacotes fora de ordem.

O problema pode ocorrer em qualquer rede IP hop-by-hop; não é exclusivo do
Segment Routing. O loop pode envolver o nó próximo à falha ou roteadores a
vários saltos de distância.

**SR Microloop Avoidance** resolve assim:

1. O nó recebe a notificação de mudança pelo IGP.
2. Calcula a árvore pós-convergência e vê se algum destino passaria por um nó que ainda não convergiu.
3. Se houver risco, instala uma SID-list temporária que força o caminho pós-convergência. Como o caminho vai no pacote, não dá loop.
4. Passado o atraso definido para a atualização da RIB, a SID-list sai e o
   encaminhamento volta ao normal.

Três coisas que confundem:

- **Complementa o TI-LFA, não substitui.** FRR cobre o instante da falha, microloop avoidance cobre a reconvergência. Os dois ficam ligados juntos.
- **É local.** Cada nó decide sozinho. Não precisa habilitar em todo o domínio para ter ganho.
- **Reage a falha remota.** O TI-LFA reage a uma interface local caindo. O microloop avoidance reage a um LSA, então vale para falha em qualquer ponto da rede.

Configuração e limites do IOS-XR são tratados no lab
[`microloop-avoidance`](../../../labs/cisco/sr-mpls/ti-lfa/04-microloop-avoidance/).

## Referências

- RFC 9855 - *Topology Independent Fast Reroute Using Segment Routing*: https://datatracker.ietf.org/doc/html/rfc9855
- RFC 8333 - *Micro-loop Prevention by Introducing a Local Convergence Delay*: https://datatracker.ietf.org/doc/html/rfc8333
- RFC 5286 - *IP Fast Reroute: Loop-Free Alternates*: https://datatracker.ietf.org/doc/html/rfc5286
- RFC 7490 - *Remote Loop-Free Alternate (LFA) Fast Reroute*: https://datatracker.ietf.org/doc/html/rfc7490
- RFC 8402 - *Segment Routing Architecture*: https://datatracker.ietf.org/doc/html/rfc8402
