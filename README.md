# Laboratórios de Segment Routing

Material conceitual e laboratórios reproduzíveis de Segment Routing. O projeto
separa os conceitos independentes de fabricante das implementações específicas
de cada plataforma.

> Uso interno, material em desenvolvimento.

## Por onde começar

1. Prepare Docker e Containerlab com o [guia de ambiente](./docs/setup.md).
2. Leia os [fundamentos de SR-MPLS](./docs/concepts/sr-mpls/README.md).
3. Prepare a plataforma com o [setup do Cisco XRd](./labs/cisco/setup.md).
4. Escolha uma trilha no [índice de laboratórios Cisco](./labs/cisco/README.md).
5. Antes de cada lab, leia o documento conceitual indicado no roteiro.

O [roadmap](./docs/roadmap.md) apresenta a cobertura atual e os cenários
planejados.

## Estrutura

```text
LabRedes-segmentrouting/
├── README.md
├── docs/
│   ├── README.md
│   ├── setup.md
│   ├── roadmap.md
│   ├── concepts/             # conteúdo independente de fabricante
│   └── references/           # material de referência externo
└── labs/
    └── cisco/
        ├── README.md
        ├── setup.md
        └── sr-mpls/
            ├── 00-base/
            ├── ti-lfa/
            ├── sr-te/
            ├── inter-as/
            └── multidominio/
```

Cada laboratório reúne no mesmo diretório o roteiro (`README.md`), a topologia
Containerlab (`lab.clab.yml`), as configurações dos nós (`configs/`) e as
imagens usadas na documentação (`images/`).
