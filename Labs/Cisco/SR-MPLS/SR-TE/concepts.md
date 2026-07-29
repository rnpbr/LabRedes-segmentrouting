# SR-TE - conceitos

> O diagrama deste lab sai de [`diagrams/sr-te-rede-ipe-topology.drawio`](./diagrams/sr-te-rede-ipe-topology.drawio).

## O que é

SR-TE é a engenharia de tráfego do Segment Routing. O nó de entrada (headend) impõe uma lista de SIDs que descreve o caminho desejado, ignorando o que o IGP escolheria por custo.

Não há RSVP-TE nem estado por caminho nos nós do meio. Cada um só olha o topo da pilha e encaminha, como no SR normal.

O problema que isso resolve: o IGP decide por um critério só, o custo, e manda todo o tráfego de um destino pelo mesmo caminho. Quando existe motivo para separar tráfego, como latência ou isolamento de risco, o IGP sozinho não expressa isso.

## Termos

| Termo | Significado |
|---|---|
| **Headend** | Nó que origina a policy e impõe a pilha de labels. É o único que conhece a policy. |
| **Endpoint** | IP de destino da policy, normalmente a loopback de um PE remoto. |
| **Color** | Número que identifica a intenção da policy. Junto com o endpoint, identifica a policy. |
| **Candidate path** | Um caminho possível, com uma preferência. A policy usa o de maior preferência que estiver válido. |
| **Segment list** | Sequência de SIDs que vira a pilha de labels MPLS. |
| **Binding-SID** | Label que representa a policy inteira. Outro nó empilha só ele, sem conhecer os segmentos de dentro. |
| **Waypoint** | Nó intermediário colocado de propósito na segment list, para forçar passagem por ele. |

## Explicit e dynamic

Uma SR Policy pode ter dois tipos de candidate path:

- **Explicit**: a segment list é escrita à mão. É o que o lab `explicit-policy` usa. Fácil de entender e depurar, mas não se adapta: se um nó do caminho cair, a policy fica down até alguém reconfigurar.
- **Dynamic**: o headend ou um controlador (SR-PCE com BGP-LS) calcula o caminho por um objetivo, como menor latência, e recalcula sozinho quando a topologia muda.

Em produção quase todo deployment usa dynamic, ou os dois juntos. Explicit é o ponto de entrada didático porque o resultado é previsível e dá para conferir na pilha de labels.

## Como o tráfego entra na policy

Criar a policy não basta. Alguma coisa precisa decidir qual tráfego usa ela. Três formas:

- **Rota estática com `sr-policy`**: o que o lab usa. Simples, mas cada prefixo precisa da própria rota.
- **Automated Steering por Color**: o BGP anuncia o prefixo com uma community de Color, e o headend casa com a policy de mesmo Color. É o que se usa em produção, porque escala.
- **ODN (On-Demand Nexthop)**: a policy nem existe antes. É criada a partir de um template quando chega o primeiro prefixo com aquele Color.

## Binding-SID

O Binding-SID permite compor policies. Um headend de um domínio empilha só o Binding-SID de uma policy que vive no domínio seguinte, sem conhecer os segmentos de lá. É a base dos cenários inter-domínio.

## SR-TE e Flex-Algo

Os dois fogem do SPF padrão, mas por mecanismos diferentes:

- **SR-TE** age no headend, por color e endpoint. Granularidade de fluxo: policies diferentes levam tráfegos diferentes para o mesmo destino por caminhos diferentes.
- **Flex-Algo** age no IGP inteiro. Todo nó calcula um SPF alternativo com as mesmas restrições, e o resultado é um prefix-SID por algoritmo. Granularidade de topologia.

Na prática se combinam: o Flex-Algo constrói o plano restrito, e uma segment list de SR-TE pode usar SIDs desse algoritmo.

Nenhum lab de Flex-Algo existe ainda. Ver [`roadmap.md`](../../roadmap.md).

## Referências

- RFC 9256 - *Segment Routing Policy Architecture*: https://datatracker.ietf.org/doc/html/rfc9256
- RFC 8402 - *Segment Routing Architecture*: https://datatracker.ietf.org/doc/html/rfc8402
- Cisco IOS-XR - *Configure SR-TE Policies*: https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x/configure-sr-te-policies.html
