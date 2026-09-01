> Uso interno, material em desenvolvimento.

# Segment Routing sobre Cisco IOS-XR

Laboratórios de Segment Routing rodando em Containerlab com Cisco XRd. Os cenários usam a temática da Rede Ipê.

## Por onde começar

1. [`docs/base.md`](./docs/base.md) - conceitos e convenções.
2. [`docs/setup.md`](./docs/setup.md) - Docker, Containerlab, imagem XRd.
3. TI-LFA, nesta ordem: `00-zero-segment`, `01-single-segment`, `02-double-segment`, `03-node-srlg-protection`, `04-microloop-avoidance`. Cada lab assume o anterior. Ler [`concepts.md`](./SR-MPLS/TI-LFA/concepts.md) antes do primeiro.
4. SR-TE: `explicit-policy`, independente da trilha de TI-LFA.
5. Inter-AS: `bgp-lu`, o maior lab do repositório. Assume TI-LFA e SR-TE já lidos. Ler [`inter-as_concepts.md`](./SR-MPLS/Inter-AS/inter-as_concepts.md) antes.

Índice completo de cenários, incluindo o que ainda não tem lab: [`docs/roadmap.md`](./docs/roadmap.md).

## Estrutura

```text
LabRedes-segmentrouting/
├── Docs/References/          # material de referência externo
│
├── Labs/Cisco/
│   ├── README.md              # este arquivo
│   ├── docs/
│   │   ├── base.md            # conceitos e convenções
│   │   ├── setup.md           # ambiente
│   │   └── roadmap.md         # índice completo de cenários
│   └── SR-MPLS/
│       ├── TI-LFA/            # concepts.md + 5 labs
│       ├── SR-TE/             # sr-te_concepts.md + explicit-policy
│       └── Inter-AS/          # inter-as_concepts.md + bgp-lu
│
└── IaC/Clabs/Cisco/
    ├── ti-lfa/                # topologias containerlab
    ├── sr-te/
    └── inter-as/
```

Cada lab fica em `Labs/Cisco/SR-MPLS/<categoria>/<lab>/`, com o markdown, `configs/*.cfg` por nó e `images/`. A topologia correspondente fica em `IaC/Clabs/Cisco/<categoria>/<lab>.clab.yml`.

## Subir um lab

```bash
git clone https://github.com/rnpbr/LabRedes-segmentrouting.git
cd LabRedes-segmentrouting

mkdir -p ~/labs/<categoria>/<lab>
cp IaC/Clabs/Cisco/<categoria>/<lab>.clab.yml ~/labs/<categoria>/<lab>/
cp -r Labs/Cisco/SR-MPLS/<CATEGORIA>/<lab>/configs ~/labs/<categoria>/<lab>/

cd ~/labs/<categoria>/<lab>
sudo clab deploy -t <lab>.clab.yml
```

`<categoria>` é `ti-lfa`, `sr-te` ou `inter-as`. `<CATEGORIA>` é `TI-LFA`, `SR-TE` ou `Inter-AS`. Detalhes, deploy direto do GitHub e problemas comuns em [`docs/setup.md`](./docs/setup.md).

## Labs

### TI-LFA

| Lab | O que mostra | Nós |
|---|---|---:|
| [zero-segment](./SR-MPLS/TI-LFA/00-zero-segment/zero-segment.md) | PQ-node vizinho direto do PLR, nenhum label extra | 4 |
| [single-segment](./SR-MPLS/TI-LFA/01-single-segment/single-segment.md) | PQ-node no P-space estendido, um label extra | 6 |
| [double-segment](./SR-MPLS/TI-LFA/02-double-segment/double-segment.md) | P-space e Q-space disjuntos, Adj-SID como ponte | 6 |
| [node-srlg-protection](./SR-MPLS/TI-LFA/03-node-srlg-protection/node-srlg-protection.md) | Tiebreakers de proteção de nó e de SRLG | 6 |
| [microloop-avoidance](./SR-MPLS/TI-LFA/04-microloop-avoidance/microloop-avoidance.md) | SID-list temporária durante a reconvergência | 6 |

Conceitos: [`SR-MPLS/TI-LFA/concepts.md`](./SR-MPLS/TI-LFA/concepts.md).

### SR-TE

| Lab | O que mostra | Nós |
|---|---|---:|
| [explicit-policy](./SR-MPLS/SR-TE/explicit-policy/explicit-policy.md) | Segment list estática forçando o caminho de menor latência | 5 |

Conceitos: [`SR-MPLS/SR-TE/sr-te_concepts.md`](./SR-MPLS/SR-TE/sr-te_concepts.md).

### Inter-AS

| Lab | O que mostra | Nós |
|---|---|---:|
| [bgp-lu](./SR-MPLS/Inter-AS/bgp-lu/bgp-lu.md) | BGP-LU costurando dois domínios SR; recursão do next hop, TI-LFA e SR Policy com PeerNode SID | 8 + 2 |

Conceitos: [`SR-MPLS/Inter-AS/inter-as_concepts.md`](./SR-MPLS/Inter-AS/inter-as_concepts.md).

Os "+ 2" são clientes Alpine, não roteadores. É o único lab do repositório com nós que não são XRd, e o único que precisa de ~12 GB de RAM.

### O que vem depois

Flex-Algo, SRv6, multi-domínio e outros fabricantes estão no radar mas ainda sem lab pronto. Lista completa, com status de cada um, em [`docs/roadmap.md`](./docs/roadmap.md).
