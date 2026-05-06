> Uso interno — material em desenvolvimento.

# SR-MPLS | Cisco IOS-XR

## Ambiente

| Componente | Detalhe |
|---|---|
| Orquestrador | Containerlab |
| NOS | Cisco IOS-XR (XRd Control Plane) |
| Imagem | `sbezverk/xrd-control-plane:7.10.2` |

```bash
# Pre-requisito obrigatorio antes de qualquer deploy
sudo sysctl -w fs.inotify.max_user_instances=64000
sudo sysctl -w fs.inotify.max_user_watches=64000

# Baixar a imagem uma unica vez
docker pull sbezverk/xrd-control-plane:7.10.2
```


## Referencias

- CCIE SPv5.1 Labs (SR): https://ccie-sp.gitbook.io/ccie-spv5.1-labs/labs/sr
- Containerlab XRd: https://containerlab.dev/manual/kinds/xrd/
- Cisco IOS-XR SR Configuration Guide: https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x.html