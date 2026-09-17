> Uso interno, material em desenvolvimento.

# Laboratórios Cisco IOS-XR

Implementações de Segment Routing executadas em Containerlab com Cisco XRd. Os
cenários usam a temática da Rede Ipê.

## Preparação

1. Instale os componentes comuns descritos em [`docs/setup.md`](../../docs/setup.md).
2. Prepare a imagem e o host conforme o [`setup.md`](./setup.md) do Cisco XRd.
3. Consulte a [base SR-MPLS no IOS-XR](./sr-mpls/00-base/README.md).

## Laboratórios

### TI-LFA

Leia primeiro os [conceitos de TI-LFA](../../docs/concepts/sr-mpls/ti-lfa.md).
Os cinco labs formam uma sequência e cada um assume o anterior.

| Lab | O que mostra | Nós |
|---|---|---:|
| [zero-segment](./sr-mpls/ti-lfa/00-zero-segment/) | PQ-node vizinho direto do PLR, nenhum label extra | 4 |
| [single-segment](./sr-mpls/ti-lfa/01-single-segment/) | PQ-node no P-space estendido, um label extra | 6 |
| [double-segment](./sr-mpls/ti-lfa/02-double-segment/) | P-space e Q-space disjuntos, Adj-SID como ponte | 6 |
| [node-srlg-protection](./sr-mpls/ti-lfa/03-node-srlg-protection/) | Tiebreakers de proteção de nó e de SRLG | 6 |
| [microloop-avoidance](./sr-mpls/ti-lfa/04-microloop-avoidance/) | SID-list temporária durante a reconvergência | 6 |

### SR-TE

| Lab | O que mostra | Nós |
|---|---|---:|
| [explicit-policy](./sr-mpls/sr-te/explicit-policy/) | Segment list estática forçando um caminho de menor latência | 5 |

Conceitos: [SR-TE e SR Policy](../../docs/concepts/sr-mpls/sr-te.md).

### Inter-AS

| Lab | O que mostra | Nós |
|---|---|---:|
| [bgp-lu](./sr-mpls/inter-as/bgp-lu/) | BGP-LU entre domínios SR, recursão de next hop, TI-LFA e EPE | 8 + 2 |

Conceitos: [transporte Inter-AS](../../docs/concepts/sr-mpls/inter-as.md).

Os dois nós adicionais do `bgp-lu` são clientes Alpine. Esse cenário requer
aproximadamente 12 GB de RAM e oito CPUs.

## Executar um cenário

Cada lab contém todos os arquivos necessários:

```text
<lab>/
├── README.md
├── lab.clab.yml
├── configs/
└── images/
```

Exemplo:

```bash
cd labs/cisco/sr-mpls/ti-lfa/00-zero-segment
sudo clab deploy -t lab.clab.yml
```

O [roadmap](../../docs/roadmap.md) apresenta os cenários concluídos e planejados.
