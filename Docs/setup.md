# Ambiente - Docker, Containerlab, imagem XRd

> Pré-requisito operacional para qualquer lab deste projeto. `base.md` cobre conceitos; este documento cobre só o que precisa estar instalado e funcionando antes do primeiro `clab deploy`.

## Requisitos de host

- Linux (bare-metal ou VM) com virtualização aninhada habilitada se for VM.
- Docker Engine.
- Containerlab.
- RAM: ~1-1.5 GB por nó XRd control-plane. Labs deste projeto vão de 4 a 6 nós - reserve 6-9 GB livres, mais folga se for rodar mais de um lab ao mesmo tempo.
- Limites de `inotify` altos o suficiente para o número de nós do lab (ver abaixo).

## Instalar Docker e Containerlab

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # relogar depois
bash -c "$(curl -sL https://get.containerlab.dev)"
```

Confirmar versões:

```bash
docker --version
containerlab version
```

## Obter a imagem XRd

A imagem `xrd-control-plane` não está em um registry público - vem de um tarball baixado com login CCO (Cisco Connection Online) em [software.cisco.com](https://software.cisco.com), procurando por "IOS XRd Control-Plane Container".

```bash
docker load -i xrd-control-plane-x64-7.10.2.tgz
docker images | grep xrd
```

O `docker load` já produz a tag local usada em todos os labs deste projeto: `ios-xr/xrd-control-plane:7.10.2`. Se a tag vier diferente, re-marque:

```bash
docker tag <tag-original> ios-xr/xrd-control-plane:7.10.2
```

Sem acesso a CCO, uma alternativa para estudo (não suportada pela Cisco, mantida pela comunidade) é a imagem espelhada por [sbezverk](https://hub.docker.com/r/sbezverk/xrd-control-plane) no Docker Hub - troque a referência `image:` nos arquivos `.clab.yml` de acordo.

## Preparar limites de inotify

Labs com muitos nós (a partir de ~6-8) costumam esbarrar em limites default de `inotify` do host:

```bash
sudo sysctl -w fs.inotify.max_user_instances=524288
sudo sysctl -w fs.inotify.max_user_watches=524288
```

Sem `sudo` mas com permissão Docker:

```bash
docker run --rm --privileged -v /proc:/hostproc --entrypoint /bin/bash \
  ios-xr/xrd-control-plane:7.10.2 -lc \
  'echo 524288 > /hostproc/sys/fs/inotify/max_user_instances && echo 524288 > /hostproc/sys/fs/inotify/max_user_watches'
```

## Fluxo padrão de um lab

Todo lab deste projeto segue o mesmo padrão de deploy:

```bash
mkdir -p ~/labs/sr-mpls/<caminho-do-lab>
cd ~/labs/sr-mpls/<caminho-do-lab>
cp IaC/Clabs/Cisco/<categoria>/<lab>.yml lab.clab.yml
cp -r Labs/Cisco/SR-MPLS/<Categoria>/<lab>/configs .
sudo clab deploy -t lab.clab.yml
```

O `.yml` referencia cada `.cfg` via `startup-config`, então os nós já sobem configurados - não é necessário colar configuração manualmente. Acesso via SSH, usuário `clab`, senha `clab@123`.

Para derrubar:

```bash
sudo clab destroy -t lab.clab.yml
```

## Problemas comuns

| Sintoma | Causa provável |
|---|---|
| Nó XRd não sai do estado `starting` | RAM insuficiente no host, ou limite de `inotify` |
| `startup-config` não aplicado | Caminho relativo errado - `configs/` precisa estar ao lado do `.clab.yml` |
| Adjacência OSPF não sobe | Interface errada no `.clab.yml` (`Gi0-0-0-N` != `GigabitEthernet0/0/0/N` na config) ou custo/`network point-to-point` ausente |
| `docker load` não gera a tag esperada | Verificar `docker images`, retaguear manualmente conforme acima |
