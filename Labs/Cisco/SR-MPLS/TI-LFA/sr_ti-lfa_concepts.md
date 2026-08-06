# TI-LFA - Topology Independent Loop-Free Alternates

> As imagens `topology-*.png` de cada lab tem origem em [`diagrams/ti-lfa-topologies.drawio`](./diagrams/ti-lfa-topologies.drawio) (uma pagina por cenario, mesmo arquivo). Editar la para manter o estilo visual consistente entre labs.

## O que é TI-LFA

TI-LFA é um mecanismo de **fast reroute** para redes SR-MPLS. Quando um link ou nó falha, o roteador no ponto da falha (PLR - Point of Local Repair) já tem um caminho de backup pré-computado e instalado na FIB, ativado localmente em menos de 50ms - sem esperar o IGP reconvergir pelo domínio inteiro.

Isso resolve uma limitação de qualquer IGP: reconvergência não é instantânea. Cada roteador recalcula SPF e atualiza sua FIB no próprio tempo, e essa janela - de centenas de ms a poucos segundos numa rede pequena, mais em redes maiores - é onde o tráfego cai se não houver backup pronto de antemão.

## De LFA a TI-LFA

- **LFA (Loop-Free Alternate)**: mecanismo clássico, pré-SR. Um vizinho do PLR serve de backup se, e só se, o caminho dele até o destino não passar de volta pelo PLR (condição de loop-free). Cobertura limitada - em muitas topologias, nenhum vizinho satisfaz a condição.
- **Remote LFA (RFC 7490)**: estende o LFA usando um túnel LDP até um nó mais distante (não necessariamente vizinho) que sirva de backup. Melhora a cobertura, mas depende de LDP e de um túnel dedicado.
- **TI-LFA**: usa Segment Routing para alcançar qualquer nó relevante da rede via label stack, sem depender de túnel LDP nem de o nó ser vizinho direto. Cobertura muito maior que LFA/Remote LFA, e "topology independent" porque o mecanismo funciona igual em qualquer topologia - não depende de casos especiais.

## P-space, Q-space, Ext P-space

A pergunta central do TI-LFA: como o PLR leva o tráfego até um nó que já sabe (nativamente, sem cruzar a falha) chegar ao destino?

- **P-space(PLR, falha)**: todo nó que o PLR alcança pelo caminho mais curto sem usar o recurso que falhou.
- **Q-space(destino, falha)**: todo nó que alcança o destino pelo caminho mais curto sem usar o recurso que falhou.
- **P-space estendido**: união do P-space do PLR com o P-space de cada vizinho remanescente do PLR (todo vizinho que não seja a outra ponta do recurso protegido). Importa porque o nó-alvo do backup nem sempre é vizinho direto do PLR - pode estar dois ou mais saltos, desde que o caminho mais curto até ele (calculado a partir do PLR) já passe por um vizinho do PLR.

Quando existe um nó nos dois conjuntos ao mesmo tempo (**PQ-node**), o PLR só precisa levar o tráfego até ele - a partir dali, a rede já sabe nativamente levar ao destino sem cruzar a falha. Quando existe mais de um candidato válido, a escolha entre eles é implementação interna do IOS-XR, não normatizada por RFC - **na prática, isso significa que o PQ-node real observado num teste pode não ser o mais "óbvio" ou mais próximo, e vale sempre confirmar via `show`, não assumir pela topologia sozinha.**

## Os cenários: zero, single, double-segment

O número de labels adicionais que o PLR empilha, além do label do próprio destino, define o cenário:

- **Zero-Segment**: o PQ-node é vizinho direto do PLR (está no P-space não-estendido). Nenhum label adicional - o PLR encaminha fisicamente para o vizinho, que já está tanto no P-space quanto no Q-space.
- **Single-Segment**: o PQ-node está no P-space *estendido* mas não é vizinho direto - é alcançado através de um vizinho do PLR. O PLR empilha `{ prefix-SID(PQ-node) }` sobre o label do destino; o vizinho intermediário encaminha nativamente até o PQ-node, que por sua vez já enxerga o destino sem cruzar o recurso protegido.
- **Double-Segment**: P-space e Q-space não se intersectam em nenhum nó, mas existe um nó do P-space (P-node) adjacente a um nó do Q-space (Q-node). O PLR empilha `{ prefix-SID(P-node), adj-SID(P-node->Q-node) }`. O Adj-SID força a travessia daquele enlace específico independentemente do seu custo IGP - é o que permite "costurar" P-space e Q-space quando o caminho mais curto natural não faz a ponte entre eles.

Em topologias reais nem sempre existe um P-node adjacente a um Q-node; nesses casos raros, IOS-XR pode precisar de mais de dois segmentos, mas o algoritmo (proprietário, fora do escopo de padronização do IETF) é dimensionado para cobrir a esmagadora maioria dos casos práticos com no máximo alguns poucos segmentos.

## Node protection e SRLG protection

TI-LFA pode proteger três tipos de recurso, em ordem crescente de exigência:

- **Link protection**: protege apenas contra a falha do enlace específico. É a proteção mínima e sempre implícita - node protection e SRLG protection sempre implicam link protection.
- **Node protection**: o backup contorna completamente o próximo salto, não apenas o enlace até ele. Necessário porque falhas de link são estatisticamente muito mais comuns que falhas de nó, mas quando um nó inteiro cai (falha de hardware, reload, perda de energia), um backup que só evita o *link* ainda tentaria atravessar o nó morto.
- **SRLG protection (Shared Risk Link Group)**: protege contra a falha correlacionada de múltiplos enlaces que compartilham um recurso físico comum (mesmo duto, mesmo poste, mesma rota de fibra, mesmo cartão de linha). Um backup que reusa um enlace do mesmo SRLG do enlace protegido não oferece proteção real: se os dois links realmente compartilham o mesmo risco físico, o evento que derrubou um provavelmente derruba o outro também.

Como cada nó pode ter mais de um candidato a backup - um mais barato mas menos protegido, outro mais caro mas com cobertura melhor -, o IOS-XR usa **tiebreakers** configuráveis por interface para decidir qual característica priorizar quando os candidatos não coincidem em um único caminho:

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
- Quando um único caminho satisfaz as duas propriedades simultaneamente (o caso mais comum, e o demonstrado no lab `node-srlg-protection`), o tiebreaker apenas confirma a escolha - o `show` correspondente reporta `TI-LFA (node+srlg)`.
- SRLG é um atributo do **enlace**, não do nó - precisa ser declarado localmente em cada roteador dono de uma ponta do enlace, e é distribuído aos demais roteadores do domínio via extensões do IGP.



## Referências

- RFC 8402 - *Segment Routing Architecture*: https://datatracker.ietf.org/doc/html/rfc8402
- RFC 7490 - *Remote Loop-Free Alternate (LFA) Fast Reroute*: https://datatracker.ietf.org/doc/html/rfc7490
- RFC 8665 - *OSPF Extensions for Segment Routing*: https://datatracker.ietf.org/doc/html/rfc8665
- RFC 8667 - *IS-IS Extensions for Segment Routing*: https://datatracker.ietf.org/doc/html/rfc8667
- Cisco IOS-XR Segment Routing Configuration Guide - *Topology Independent LFA (TI-LFA)*: https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x/configure-ti-lfa.html
- segment-routing.net - *TI-LFA Tutorial*: https://www.segment-routing.net/tutorials/2017-03-07-segment-routing-ti-lfa/