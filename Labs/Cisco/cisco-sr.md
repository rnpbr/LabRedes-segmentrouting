> Uso interno, material em desenvolvimento.

# Segment Routing sobre Cisco IOS-XR

Laboratórios de Segment Routing rodando em Containerlab com Cisco XRd. Os cenários usam a temática da Rede Ipê.

## Por onde começar

1. [`base.md`](./base.md) - conceitos e convenções.
2. [`setup.md`](./setup.md) - Docker, Containerlab, imagem XRd.
3. TI-LFA, nesta ordem: zero-segment, single-segment, double-segment, node-srlg-protection, microloop-avoidance.
4. SR-TE: explicit-policy. Independente da trilha de TI-LFA.

Índice completo de cenários, com status: [`roadmap.md`](./roadmap.md).

## Estrutura

```text
LabRedes-segmentrouting/
├── Docs/References/          # material de referência externo
│
├── Labs/Cisco/
│   ├── base.md               # conceitos e convenções
│   ├── setup.md              # ambiente
│   ├── roadmap.md            # índice de cenários
│   ├── cisco-sr.md           # este arquivo
│   └── SR-MPLS/
│       ├── TI-LFA/           # concepts.md + 5 labs
│       └── SR-TE/            # concepts.md + explicit-policy
│
└── IaC/Clabs/Cisco/
    ├── ti-lfa/               # topologias containerlab
    └── sr-te/
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

`<categoria>` é `ti-lfa` ou `sr-te`. `<CATEGORIA>` é `TI-LFA` ou `SR-TE`. Os nós já sobem configurados. Detalhes, deploy direto do GitHub e problemas comuns em [`setup.md`](./setup.md).

## Labs

### TI-LFA

| Lab | O que mostra | Nós |
|---|---|---:|
| [zero-segment](./SR-MPLS/TI-LFA/zero-segment/zero-segment.md) | PQ-node vizinho direto do PLR, nenhum label extra | 4 |
| [single-segment](./SR-MPLS/TI-LFA/single-segment/single-segment.md) | PQ-node no P-space estendido, um label extra | 6 |
| [double-segment](./SR-MPLS/TI-LFA/double-segment/double-segment.md) | P-space e Q-space disjuntos, Adj-SID como ponte | 6 |
| [node-srlg-protection](./SR-MPLS/TI-LFA/node-srlg-protection/node-srlg-protection.md) | Tiebreakers de proteção de nó e de SRLG | 6 |
| [microloop-avoidance](./SR-MPLS/TI-LFA/microloop-avoidance/microloop-avoidance.md) | SID-list temporária durante a reconvergência | 6 |

Conceitos: [`SR-MPLS/TI-LFA/concepts.md`](./SR-MPLS/TI-LFA/concepts.md).

### SR-TE

| Lab | O que mostra | Nós |
|---|---|---:|
| [explicit-policy](./SR-MPLS/SR-TE/explicit-policy/explicit-policy.md) | Segment list estática forçando o caminho de menor latência | 5 |

Conceitos: [`SR-MPLS/SR-TE/concepts.md`](./SR-MPLS/SR-TE/concepts.md).

### Multi-domínio


