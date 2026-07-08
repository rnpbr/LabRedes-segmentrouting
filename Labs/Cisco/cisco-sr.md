> Uso interno - material em desenvolvimento.

# LabRedes - Segment Routing

Parte do projeto **LabRedes**: laboratórios práticos de Segment Routing, com cenários próximos de rede real (temática Rede Ipê) rodando sobre Containerlab + Cisco XRd.

Segment Routing simplifica redes MPLS eliminando protocolos de sinalização como RSVP-TE e LDP: o caminho vai codificado no próprio pacote como uma pilha de labels, a rede fica stateless e o headend é o único ponto de controle do tráfego.

## Por onde começar


1. [`Docs/Cisco Labs/roadmap.md`](./Docs/roadmap.md) - todo cenário clássico de SR no escopo do projeto, com status e ordem sugerida.
2. [`Docs/Cisco Labs/base.md`](./Docs/base.md) - conceitos, convenções do projeto, topologia de referência.
3. [`Docs/Cisco Labs/setup.md`](./Docs/setup.md) - Docker, Containerlab, imagem XRd, problemas comuns.
 

## Estrutura

```text
LabRedes-segmentrouting/
├── Docs/Cisco Labs/
│   ├── base.md            # conceitos e convenções (pré-requisito de todo lab)
│   ├── setup.md           # ambiente: Docker, Containerlab, imagem XRd
│   └── roadmap.md         # índice de cenários, status, ordem sugerida
│
├── Labs/
│   └── Cisco/
│       └── SR-MPLS/
│           ├── TI-LFA/     # zero/single/double-segment, node+SRLG
│           └── SR-TE/      # explicit-policy
│
└── IaC/
    └── Clabs/
        └── Cisco/          # topologias containerlab (.yml), uma pasta por categoria
```

Cada lab fica em `Labs/Cisco/SR-MPLS/<categoria>/<lab>/`, com o markdown do lab, `configs/*.cfg` por nó e `images/` quando houver capturas. O `.clab.yml` correspondente fica em `IaC/Clabs/Cisco/<categoria>/<lab>.yml` e é copiado para a pasta de deploy - ver `Docs/setup.md` para o fluxo padrão.

## Labs disponíveis

### Cisco IOS-XR

| Lab | Categoria | Descrição |
|---|---|---|
| [zero-segment](./Labs/Cisco/SR-MPLS/TI-LFA/zero-segment/zero-segment.md) | TI-LFA | PQ-node vizinho direto do PLR |
| [single-segment](./Labs/Cisco/SR-MPLS/TI-LFA/single-segment/single-segment.md) | TI-LFA | PQ-node via Ext P-space, um segmento extra |
| [double-segment](./Labs/Cisco/SR-MPLS/TI-LFA/double-segment/double-segment.md) | TI-LFA | P-space e Q-space disjuntos, Adj-SID como ponte |
| [node-srlg-protection](./Labs/Cisco/SR-MPLS/TI-LFA/node-srlg-protection/node-srlg-protection.md) | TI-LFA | Tiebreakers de proteção de nó e SRLG |
| [explicit-policy](./Labs/Cisco/SR-MPLS/SR-TE/explicit-policy/explicit-policy.md) | SR-TE | Segment list estática forçando caminho de menor latência |

Todo cenário clássico de SR fora desta lista (Flex-Algo, SRv6, multi-domínio, ODN, etc.) está listado com status em `Docs/Cisco Labs/roadmap.md`, concluído ou não.


### Multi-domínio / Inter-domínio

Em desenvolvimento 
