# Flex-Algo com SID anycast de borda — lab multi-domínio SR-MPLS

Este lab demonstra costura interdomínio SR-MPLS com OSPF Flexible Algorithm 128 e Prefix-SIDs anycast de borda em containers Cisco XRd control-plane.

A topologia tem 10 roteadores:

```text
Domínio A              Domínio B         Domínio C

 PE1 --- P1 --- DBR-AB1 ======== DBR-BC1 --- P3 --- PE9
  |      |        ||       \     /   ||       |      |
  |red   |        ||        \red/    ||       |      |red
  |      |        ||        /   \    ||       |      |
 P2 ----+--- DBR-AB2 ======== DBR-BC2 --- P4 ---+
```

`DBR-AB1` e `DBR-AB2` são compartilhados pelos domínios A e B. `DBR-BC1` e `DBR-BC2` são compartilhados pelos domínios B e C. Cada DBR roda um processo OSPF por domínio adjacente e não redistribui rotas entre processos.

## Relação com a base

Este lab assume [base.md](base.md) como pré-requisito. Conceitos como Segment Routing, SID, Prefix-SID, node-SID, SRGB, SRLB, OSPFv2 com SR e validação básica de SR-MPLS não são redefinidos aqui.

O que é reaproveitado da base:

- SR-MPLS como plano de dados.
- IOS-XR/XRd como plataforma de referência.
- SRGB `16000 23999`.
- OSPFv2 com área `0`.
- Loopbacks anunciadas como prefixos passivos.
- Interfaces de core como `point-to-point`.
- `segment-routing sr-prefer`.

O que este lab muda de propósito:

- O endereçamento usa blocos por domínio (`10.1.0.0/16`, `10.2.0.0/16`, `10.3.0.0/16`) em vez da topologia didática única da base.
- Há três processos OSPF independentes (`100`, `200`, `300`), todos em área `0`. Isto é multi-processo, não multi-area OSPF nem IS-IS multi-level.
- Os índices de SID codificam papel e domínio, não apenas o ID simples do nó. Por exemplo, o SID Algo-128 do anycast AB usa index `1120`, que vira label `17120`.
- A topologia é maior e inclui DBRs compartilhados para expor falhas específicas de anycast de borda.

## Problema modelado

Operadores dividem IGPs em múltiplos domínios por escala, contenção de falhas, fronteiras operacionais e limites administrativos. O custo é que nenhum roteador enxerga a topologia completa. PE1 não consegue calcular um SPF normal até PE9 porque o domínio A não carrega a topologia do domínio C.

Em redes reais, a costura de transporte entre domínios costuma aparecer de uma destas formas:

- BGP-LU ou seamless MPLS, em que o BGP carrega alcance rotulado entre domínios.
- SR-PCE, normalmente alimentado por BGP-LS, em que um controlador tem a visão de topologia necessária para calcular um caminho SR interdomínio.
- ODN ou mecanismos equivalentes, em que rotas de serviço com color disparam criação ou seleção de SR Policies.

Este lab deliberadamente não implementa esses mecanismos. O stack SR-TE explícito em PE1 é montado à mão:

```text
17120  SID anycast AB, Algo 128
17230  SID anycast BC, Algo 128
17309  node-SID PE9, Algo 128
```

Isto deixa o plano de controle fácil de inspecionar, mas é uma limitação: o humano está fazendo o papel do elemento de computação interdomínio. Trate o stack estático como degrau didático, não como resposta de produção.

PE1 tem uma rota estática para `10.3.255.9/32` apontando para a SR Policy. Ela existe para que a validação injete tráfego IP real no color 128 sem adicionar BGP. Essa rota estática é conveniência de lab, não protocolo de alcance interdomínio.

## O que este lab prova

O Algo 128 é definido da mesma forma nos três domínios: usar a métrica IGP default e excluir links com affinity `red`. Os links vermelhos são intencionalmente mais baratos do que os caminhos limpos, então o SPF default os escolhe, enquanto o Algo 128 os evita.

Os SIDs anycast de borda são anunciados pelos dois DBRs de cada fronteira:

| SID | Prefixo | Index | Label |
| --- | --- | ---: | ---: |
| Anycast AB | `10.255.12.12/32` | `1120` | `17120` |
| Anycast BC | `10.255.23.23/32` | `1230` | `17230` |
| Node-SID PE9 Algo-128 | `10.3.255.9/32` | `1309` | `17309` |

A SR Policy em PE1 usa este stack:

```text
17120  SID anycast AB, Algo 128
17230  SID anycast BC, Algo 128
17309  node-SID PE9, Algo 128
```

PE1 então direciona `10.3.255.9/32` para a policy com uma rota estática `sr-policy`.

XR usa `n-flag-clear` para os Prefix-SIDs anycast. Nas Opaque LSAs do OSPF isso aparece como SID flags `0x0`, que é o comportamento esperado para anycast.

MPLS OAM está habilitado em todos os roteadores para que o lab consiga provar o stack fim a fim com `ping mpls` e `traceroute sr-mpls`, mesmo sem alcance loopback-to-loopback de retorno entre PE1 e PE9.

## Arquivos

```text
base.md                       referência conceitual e convenções do projeto
flex-algo-anycast.clab.yml    topologia containerlab
configs/*.cfg                 startup configs IOS-XR
MANUAL_ROUTER_CONFIGS.md      configurações completas para reprodução manual
scripts/xr                    helper para executar comandos XR CLI
```

## Preparação do host

XRd precisa de limites altos de inotify para um lab com 10 nós. Use sysctl normalmente:

```bash
sudo sysctl -w fs.inotify.max_user_instances=524288
sudo sysctl -w fs.inotify.max_user_watches=524288
```

Ou, se não houver sudo sem senha mas houver privilégio Docker:

```bash
docker run --rm --privileged -v /proc:/hostproc --entrypoint /bin/bash xrd-control-plane:7.10.2 -lc \
  'echo 524288 > /hostproc/sys/fs/inotify/max_user_instances && echo 524288 > /hostproc/sys/fs/inotify/max_user_watches'
```

Suba o lab:

```bash
containerlab deploy -t flex-algo-anycast.clab.yml --reconfigure
```

XRd leva alguns minutos para terminar o boot.

## Progressão sugerida

Os configs versionados sobem o lab completo. Para transformar o material em exercício, reconstrua em etapas:

1. Suba os três domínios OSPF/SR independentes sem os Prefix-SIDs anycast em `Loopback12` e `Loopback23`, sem a SR Policy de PE1 e sem a rota estática `sr-policy`. PE1 não deve ter rota para PE9 nem label que leve tráfego além da fronteira AB.
2. Adicione os Prefix-SIDs anycast AB e BC. Verifique que os labels `17120` e `17230` aparecem apenas onde cada domínio local consegue resolvê-los.
3. Adicione a policy explícita em PE1 com stack `17120,17230,17309`, depois adicione a rota estática para direcionar `10.3.255.9/32` para essa policy. Confirme que a policy está operacional e execute a prova de plano de dados abaixo.
4. Quebre os casos benigno e maligno nas seções de falha. Explique por que um converge de forma limpa e o outro cria black-hole.

Se usar os startup configs diretamente, trate os comandos seguintes como checklist de validação e troubleshooting do estado completo.

## Validação

Verifique aceitação dos startup configs:

```bash
for n in pe1 p1 p2 dbr-ab1 dbr-ab2 dbr-bc1 dbr-bc2 p3 p4 pe9; do
  scripts/xr "$n" "show configuration failed startup"
done
```

Esperado: apenas o cabeçalho com timestamp é impresso; não aparecem linhas de configuração rejeitadas.

Verifique adjacências:

```bash
scripts/xr pe1 "show ospf 100 neighbor"
scripts/xr dbr-ab1 "show ospf 100 neighbor" "show ospf 200 neighbor"
scripts/xr dbr-bc1 "show ospf 200 neighbor" "show ospf 300 neighbor"
scripts/xr pe9 "show ospf 300 neighbor"
```

Esperado: PE1 tem dois neighbors no domínio A; DBR-AB1 tem um neighbor no domínio A e três no domínio B; DBR-BC1 tem três neighbors no domínio B e dois no domínio C; PE9 tem dois neighbors no domínio C.

Verifique que a topologia interna não vaza fim a fim:

```bash
scripts/xr pe1 "show route 10.2.255.21/32" "show route 10.2.255.22/32"
scripts/xr pe9 "show route 10.1.255.1/32" "show route 10.2.255.11/32"
```

Esperado: `% Network not in table`.

Verifique a rota de serviço em PE1 que direciona tráfego para PE9 pela SR Policy:

```bash
scripts/xr pe1 "show route 10.3.255.9/32" "show cef 10.3.255.9/32 detail"
```

Esperado: `10.3.255.9/32` é conhecido via `static`, e o CEF aponta para `srte_c_128_ep_10.3.255.9`.

Verifique as decisões principais do Algo 128:

```bash
scripts/xr pe1 \
  "show route 10.255.12.12/32" \
  "show ospf routes flex-algo 128 10.255.12.12/32 detail" \
  "show mpls forwarding labels 17120 detail"
```

Esperado: o SPF default chega ao prefixo anycast AB via P2 pelo caminho vermelho barato, next-hop `10.1.0.3`. O Algo 128 chega via P1, next-hop `10.1.0.1`, usando label `17120`.

```bash
scripts/xr dbr-ab1 \
  "show route 10.255.23.23/32" \
  "show ospf routes flex-algo 128 10.255.23.23/32 detail" \
  "show mpls forwarding labels 17230 detail"
```

Esperado: o SPF default chega ao prefixo anycast BC pelo link vermelho AB1-BC2, next-hop `10.2.0.3`. O Algo 128 chega via BC1, next-hop `10.2.0.1`, usando label `17230`.

```bash
scripts/xr dbr-bc1 \
  "show route 10.3.255.9/32" \
  "show ospf routes flex-algo 128 10.3.255.9/32 detail" \
  "show mpls forwarding labels 17309 detail"
```

Esperado: o SPF default chega a PE9 via BC2/P4 e pelo caminho vermelho barato P4-PE9, next-hop `10.3.0.11`. O Algo 128 chega via P3, next-hop `10.3.0.1`, usando label `17309`.

Verifique a policy explícita em PE1:

```bash
scripts/xr pe1 "show segment-routing traffic-eng policy color 128"
```

Esperado: a policy está `Operational: up`, o candidate path está ativo e a segment list explícita contém `17120`, `17230` e `17309`.

Verifique o plano de dados sobre o stack explícito.

Um ping com source na loopback de PE1 ainda falha porque PE9 não tem rota de retorno para o domínio A:

```bash
scripts/xr pe1 "ping 10.3.255.9 source 10.1.255.1"
```

Esperado: o ping falha. A requisição é direcionada para a SR Policy, mas o retorno para `10.1.255.1` está ausente de propósito.

Para uma prova bidirecional de serviço neste containerlab, use o endereço de `MgmtEth0/RP0/CPU0/0` de PE1 como source. A rota de destino continua direcionando a requisição para a SR Policy; o source de gerência apenas dá a PE9 um caminho de retorno pelo segmento de gerência compartilhado.

```bash
scripts/xr pe1 "show ipv4 interface brief"
scripts/xr pe1 "ping 10.3.255.9 source 172.20.20.11"
scripts/xr pe1 "traceroute 10.3.255.9 source 172.20.20.11"
```

Se o endereço de gerência de PE1 não for `172.20.20.11`, substitua pelo endereço mostrado em `MgmtEth0/RP0/CPU0/0`.

Esperado para o ping de serviço: `Success rate is 100 percent`.

Formato esperado do traceroute de serviço:

```text
 1  10.1.0.1 [MPLS: Labels 17120/17230/17309 Exp 0]
 2  10.1.0.7 [MPLS: Labels 17230/17309 Exp 0]
 3  10.2.0.1 [MPLS: Label 17309 Exp 0]
 4  10.3.0.1 [MPLS: Label 17309 Exp 0]
 5  10.3.0.7
```

Isto é tráfego IP real atravessando os três domínios: PE1 resolve `10.3.255.9/32` para a SR Policy color 128, impõe `17120/17230/17309`, P1 expõe `17230/17309`, DBR-AB1 expõe `17309`, e PE9 recebe o pacote.

Execute também a visão SR-MPLS OAM do mesmo stack:

```bash
scripts/xr pe1 \
  "ping mpls nil-fec labels 17120,17230,17309 output interface GigabitEthernet0/0/0/0 nexthop 10.1.0.1 source 172.20.20.11"
scripts/xr pe1 \
  "traceroute sr-mpls policy name srte_c_128_ep_10.3.255.9 lsp-end-point 10.3.255.9 source 172.20.20.11 timeout 1"
```

Esperado para o MPLS ping: `Success rate is 100 percent`.

Formato esperado do traceroute SR-MPLS:

```text
  0 10.1.0.0 MRU 1500 [Labels: 17120/17230/17309 Exp: 0/0/0]
L 1 10.1.0.1 MRU 1500 [Labels: implicit-null/17230/17309 Exp: 0/0/0]
L 2 10.1.0.7 MRU 1500 [Labels: implicit-null/17309 Exp: 0/0]
L 3 10.2.0.1 MRU 1500 [Labels: 17309 Exp: 0]
L 4 10.3.0.1 MRU 1500 [Labels: implicit-null Exp: 0]
! 5 10.3.0.7
```

Verifique sinalização do SID anycast e da affinity vermelha:

```bash
scripts/xr dbr-ab1 \
  "show ospf 100 database opaque-area self-originate | begin 10.255.12.12" \
  "show ospf 200 database opaque-area self-originate | begin 10.255.12.12"
```

Esperado: os dois processos OSPF anunciam `10.255.12.12/32` com SID index `1120`, algo `128` e flags `0x0`. A saída do domínio B também mostra o link vermelho com admin group `0x00000400`.

## Falha benigna

Desligue o link de `DBR-AB1` voltado para o domínio A:

```bash
scripts/xr dbr-ab1 \
  "configure terminal" \
  "interface GigabitEthernet0/0/0/0" \
  "shutdown" \
  "commit" \
  "end"
```

Aguarde um dead interval do OSPF e verifique PE1:

```bash
scripts/xr pe1 "show ospf routes flex-algo 128 10.255.12.12/32 detail"
```

Esperado: `DBR-AB2` (`From 1.1.1.5`) vira o contribuidor anycast em uso, com métrica `31`. O primeiro salto continua sendo P1 porque o Algo 128 ainda evita o link vermelho direto PE1-P2.

Restaure o link:

```bash
scripts/xr dbr-ab1 \
  "configure terminal" \
  "interface GigabitEthernet0/0/0/0" \
  "no shutdown" \
  "commit" \
  "end"
```

Esperado após reconvergência: `DBR-AB1` (`From 1.1.1.4`) volta a ser o contribuidor em uso, com métrica `21`.

## Risco do SID anycast

A falha anterior é benigna porque DBR-AB1 deixa de ser alcançável a partir do domínio A. A falha perigosa é quando DBR-AB1 mantém sua adjacência no domínio A, mas perde toda conectividade com o domínio B. PE1 ainda enxerga DBR-AB1 como melhor contribuidor para o SID anycast AB, mas DBR-AB1 não consegue mais resolver o próximo label, `17230`, rumo à fronteira BC.

Desligue os três links de DBR-AB1 voltados para o domínio B:

```bash
scripts/xr dbr-ab1 \
  "configure terminal" \
  "interface GigabitEthernet0/0/0/1" \
  "shutdown" \
  "interface GigabitEthernet0/0/0/2" \
  "shutdown" \
  "interface GigabitEthernet0/0/0/3" \
  "shutdown" \
  "commit" \
  "end"
```

Verifique o estado ruim:

```bash
scripts/xr dbr-ab1 "show ospf 100 neighbor" "show ospf 200 neighbor"
scripts/xr pe1 "show ospf routes flex-algo 128 10.255.12.12/32 detail"
scripts/xr dbr-ab1 \
  "show route 10.255.23.23/32" \
  "show ospf routes flex-algo 128 10.255.23.23/32 detail" \
  "show mpls forwarding labels 17230 detail"
scripts/xr pe1 \
  "traceroute sr-mpls policy name srte_c_128_ep_10.3.255.9 lsp-end-point 10.3.255.9 source 172.20.20.11 timeout 1"
```

Esperado:

- `show ospf 100 neighbor` em DBR-AB1 ainda mostra P1 up.
- `show ospf 200 neighbor` em DBR-AB1 fica vazio.
- PE1 ainda seleciona `DBR-AB1` (`From 1.1.1.4`) como contribuidor AB anycast em uso para o label `17120`.
- DBR-AB1 não tem mais rota nem entrada LFIB para o label anycast BC `17230`.
- O traceroute SR-MPLS falha em DBR-AB1 com `N 2 10.1.0.7 MRU 0 [No Label]`.

Este é o caveat clássico de SID anycast de borda. O SID anycast prova que um nó de borda é alcançável a partir do domínio local; ele não prova que esse mesmo nó ainda consegue encaminhar para o próximo domínio. Desenhos de produção precisam de um mecanismo para retirar o anúncio ou dar menor preferência ao contribuidor anycast quando a conectividade downstream falha, por exemplo anúncio condicionado por saúde, object tracking, routing policy ou restrições no controller/PCE.

Restaure os links de DBR-AB1 voltados para o domínio B:

```bash
scripts/xr dbr-ab1 \
  "configure terminal" \
  "interface GigabitEthernet0/0/0/1" \
  "no shutdown" \
  "interface GigabitEthernet0/0/0/2" \
  "no shutdown" \
  "interface GigabitEthernet0/0/0/3" \
  "no shutdown" \
  "commit" \
  "end"
```

Esperado após reconvergência: DBR-AB1 volta a ter três neighbors OSPF 200, `show mpls forwarding labels 17230 detail` aponta para DBR-BC1 e o traceroute SR-MPLS volta a funcionar.

## Limpeza

```bash
containerlab destroy -t flex-algo-anycast.clab.yml --cleanup
```
