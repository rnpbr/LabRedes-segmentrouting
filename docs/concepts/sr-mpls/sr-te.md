# SR-TE - Traffic Engineering com Segment Routing

> Pré-requisito: [fundamentos de SR-MPLS](./README.md).
> Implementação Cisco: [lab `explicit-policy`](../../../labs/cisco/sr-mpls/sr-te/explicit-policy/).

## O que e SR-TE

SR-TE e o mecanismo de engenharia de trafego do Segment Routing: o headend impoe uma lista explicita de segmentos (SIDs) que descreve o caminho desejado, ignorando o que o IGP escolheria por custo metrico. Nao ha sinalizacao RSVP-TE nem estado por caminho nos nos intermediarios - cada no apenas encaminha olhando o topo da pilha de labels, exatamente como no encaminhamento SR nativo.

Isso resolve uma limitacao estrutural do IGP: o SPF escolhe um unico criterio (custo), e todo o trafego para um destino segue o mesmo caminho (ou faz ECMP entre caminhos de custo igual). Quando existe uma razao para separar trafego por caminhos diferentes - latencia, afinidade, isolamento de risco -, o IGP sozinho nao tem como expressar isso. SR-TE resolve no plano de controle do headend, sem alterar o IGP nem os nos de transito.

## Conceitos-chave

| Termo | Significado |
|---|---|
| **Headend** | No que origina a SR Policy e impoe a pilha de labels. Unico ponto com conhecimento da policy. |
| **Endpoint** | Endereco IP de destino da policy - tipicamente a loopback de um PE remoto. |
| **Color** | Atributo numerico da policy. Junto com o endpoint, identifica a policy de forma unica. Usado para casar intent (ex: "baixa latencia") com a policy certa. |
| **Candidate path** | Um caminho possivel para a policy, com uma preferencia. A policy usa o de maior preferencia que estiver valido. |
| **Segment list** | Sequencia ordenada de SIDs que descreve um caminho explicito. No plano de dados, vira a pilha de labels MPLS. |
| **Binding-SID** | Label local que representa a policy inteira. Permite que outro no (ou uma rota estatica) empilhe so esse label sem conhecer os segmentos internos. |
| **Waypoint** | No intermediario incluido deliberadamente na segment list para forcar a passagem por ele. |

## Explicit path vs dynamic path

Uma SR Policy pode ter dois tipos de candidate path:

- **Explicit**: a segment list e definida a mao pelo operador, como uma lista fixa de labels. E o que o lab `explicit-policy` usa. Simples de entender e depurar, mas nao se adapta a mudancas de topologia - se um no do caminho cair, a policy fica down ate alguem reconfigurar.
- **Dynamic**: o headend (ou um controlador externo, tipicamente via SR-PCE alimentado por BGP-LS) calcula o caminho com base em um objetivo (menor IGP metric, menor latencia, afinidades a incluir/excluir) e o recalcula automaticamente se a topologia mudar. Fora do escopo deste projeto por enquanto - ver [`roadmap.md`](../../roadmap.md).

Em producao, a maioria dos deployments reais usa dynamic paths ou uma combinacao dos dois (explicit como fallback, dynamic como preferencial). Explicit path e o ponto de entrada didatico porque o resultado e previsivel e facil de conferir na pilha de labels.

## Como o trafego entra na policy (steering)

Uma SR Policy existir nao basta - precisa de algo que decida qual trafego usar ela. Tres formas:

- **Rota estatica com `sr-policy`**: o metodo usado no lab `explicit-policy`. Simples, mas manual - cada prefixo que deve usar a policy precisa de uma rota estatica dedicada.
- **Automated Steering (Color)**: BGP anuncia o prefixo com uma community de Color. O headend casa o Color do prefixo com o Color de uma SR Policy existente e estiera automaticamente, sem rota estatica por prefixo. E o mecanismo usado em producao para escala.
- **ODN (On-Demand Nexthop)**: o headend nem tem a policy pre-configurada - a criacao e disparada dinamicamente quando chega o primeiro prefixo com aquele Color, usando um template de politica. Reduz configuracao manual em redes com muitas policies. Planejado, ver [`roadmap.md`](../../roadmap.md).

## Binding-SID e stitching

O Binding-SID e o que permite compor policies: um headend em um dominio pode empilhar o Binding-SID de uma policy que vive so no dominio seguinte, sem precisar conhecer os segmentos internos daquele dominio. Isso e a base de cenarios inter-dominio (stitching de policies atraves de fronteiras administrativas) - ver [`roadmap.md`](../../roadmap.md), ainda nao coberto por um lab.

## SR-TE vs Flexible Algorithm

Os dois resolvem problemas parecidos (caminho diferente do SPF default) por mecanismos diferentes:

- **SR-TE** opera por policy, no headend, por color+endpoint. Granularidade de fluxo/servico - policies diferentes podem levar trafegos diferentes para o mesmo destino por caminhos diferentes.
- **Flex-Algo** opera no IGP inteiro: todo no do dominio calcula um SPF alternativo com as mesmas restricoes (afinidades, metrica alternativa), e o resultado e um Prefix-SID por algoritmo, valido para qualquer origem. Granularidade de topologia, nao de fluxo.

Na pratica se combinam: Flex-Algo constroi o plano de encaminhamento restrito, e SR-TE pode usar SIDs desse algoritmo dentro de uma segment list. Nenhum lab de Flex-Algo existe ainda neste projeto - ver [`roadmap.md`](../../roadmap.md).
