> Uso interno — material em desenvolvimento.

# SR-MPLS | Cisco IOS-XR

Padronização do ambiente necessário para executar os labs de SR-MPLS sobre Cisco IOS-XR com Containerlab. 
## Ambiente

| Componente | Detalhe |
|---|---|
| Orquestrador | Containerlab 0.75.0 |
| Nodes | Cisco IOS-XR (XRd Control Plane) |
| Imagem | `sbezverk/xrd-control-plane:7.10.2` |


---

## Instalação

### Docker

https://docs.docker.com/engine/install/

### Containerlab

```bash
curl -sL https://containerlab.dev/setup | sudo -E bash -s "all"
```

### Imagem XRd (Uso exclusivamente interno)

```bash
# Baixar uma unica vez — fica disponivel para todos os labs
docker pull sbezverk/xrd-control-plane:7.10.2
```

---

## Pre-requisito obrigatorio antes de qualquer deploy

```bash
sudo sysctl -w fs.inotify.max_user_instances=64000
sudo sysctl -w fs.inotify.max_user_watches=64000
```

Para persistir apos reboot:

```bash
echo "fs.inotify.max_user_instances=64000" | sudo tee -a /etc/sysctl.conf
echo "fs.inotify.max_user_watches=64000"   | sudo tee -a /etc/sysctl.conf
```

---

## Deploy e acesso

```bash
# Subir o lab
containerlab deploy -t lab.clab.yml

# Derrubar o lab
containerlab destroy -t lab.clab.yml

# Recriar do zero (use apenas se mudar topologia)
containerlab deploy -t lab.clab.yml --reconfigure
```

### Acesso aos nos

```bash
# Via SSH (quando disponivel)
ssh clab@ip
# Senha: clab@123

```

---

## Recursos por node

| Recurso | XRd Control Plane |
|---|---|
| RAM por no | ~1 GB |
| Boot | ~30 segundos |
| KVM obrigatorio | Nao |

### Dimensionamento de RAM

| Nodes | RAM |
|---|---|
| 4 | 8 GB |
| 8 | 12 GB |
| 11 | 16 GB |
| 20 | 32 GB |

---

## Referencias

- CCIE SPv5.1 Labs (SR): https://ccie-sp.gitbook.io/ccie-spv5.1-labs/labs/sr
- Containerlab XRd: https://containerlab.dev/manual/kinds/xrd/
- Cisco IOS-XR SR Configuration Guide: https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x.html