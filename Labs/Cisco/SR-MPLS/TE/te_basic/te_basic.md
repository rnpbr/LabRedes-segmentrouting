> Uso interno - material em desenvolvimento.

# Traffic Engineering Basic

> Pré-requisito: leia o `base.md` antes de continuar. Este lab pressupõe familiaridade com os conceitos de Segment Routing, SRGB, Prefix-SID e OSPF com extensões SR definidos lá.

---

## O que este lab demonstra

O OSPF distribui caminhos de menor custo. Quando dois caminhos têm custo igual, ele usa ECMP e divide o tráfego entre eles. O SR-TE ignora essa decisão e força um caminho específico, definido pelo operador, independente do que o IGP escolheria.

Neste lab, o OSPF elegeria ECMP entre R2 e R3 para alcançar R4. A SR Policy criada em R1 força 100% do tráfego pelo caminho R1 → R3 → R4.

O caminho via R2 continua existindo no IGP. A SR Policy simplesmente não o usa.

---

## Topologia

![Topologia SR-TE](./topology_sr-te.png)

| Node | Papel   | Loopback0  | Prefix-SID | Label |
|------|---------|------------|------------|-------|
| R1   | Headend | 1.1.1.1/32 | index 1    | 16001 |
| R2   | P       | 1.1.1.2/32 | index 2    | 16002 |
| R3   | P       | 1.1.1.3/32 | index 3    | 16003 |
| R4   | Tailend | 1.1.1.4/32 | index 4    | 16004 |

| Enlace  | IP A          | IP B          |
|---------|---------------|---------------|
| R1 ↔ R2 | 10.0.12.1/30  | 10.0.12.2/30  |
| R1 ↔ R3 | 10.0.13.1/30  | 10.0.13.2/30  |
| R2 ↔ R4 | 10.0.24.1/30  | 10.0.24.2/30  |
| R3 ↔ R4 | 10.0.34.1/30  | 10.0.34.2/30  |

---

## Deploy

> Siga o `SETUP.md` para instalar Docker, Containerlab e baixar a imagem antes de continuar.

### 1. Criar a pasta do lab

```bash
mkdir -p ~/labs/sr-mpls/cisco/lab01_sr-te
cd ~/labs/sr-mpls/cisco/lab01_sr-te
```

### 2. Criar o arquivo de topologia

```bash
nano lab01_sr-te.clab.yml
```

Cole o conteúdo abaixo e salve:

```yaml
name: lab01-sr-te

mgmt:
  network: mgmt-lab01-sr-te
  ipv4-subnet: 172.20.20.0/24

topology:
  kinds:
    cisco_xrd:
      image: sbezverk/xrd-control-plane:7.10.2

  nodes:
    R1:
      kind: cisco_xrd
      mgmt-ipv4: 172.20.20.11
    R2:
      kind: cisco_xrd
      mgmt-ipv4: 172.20.20.12
    R3:
      kind: cisco_xrd
      mgmt-ipv4: 172.20.20.13
    R4:
      kind: cisco_xrd
      mgmt-ipv4: 172.20.20.14

  links:
    - endpoints: ["R1:Gi0-0-0-0", "R2:Gi0-0-0-0"]
    - endpoints: ["R1:Gi0-0-0-1", "R3:Gi0-0-0-0"]
    - endpoints: ["R2:Gi0-0-0-1", "R4:Gi0-0-0-0"]
    - endpoints: ["R3:Gi0-0-0-1", "R4:Gi0-0-0-1"]
```

### 3. Subir o lab

```bash
containerlab deploy -t lab01_sr-te.clab.yml
```

---

## Configuração

Credenciais de acesso: usuário `clab` / senha `clab@123`

| Node | IP de acesso   |
|------|----------------|
| R1   | 172.20.20.11   |
| R2   | 172.20.20.12   |
| R3   | 172.20.20.13   |
| R4   | 172.20.20.14   |

Abra um terminal para cada node e aplique as configurações abaixo. R1 é o único com SR Policy - os demais recebem apenas a base de SR-MPLS.

---

### R1 - Headend

O Segment List `[16003, 16004]` instrui o tráfego a passar por R3 antes de chegar em R4. O Binding-SID `15100` representa essa policy como um único label. A rota estática direciona o tráfego para 1.1.1.4 para dentro da policy.

```bash
ssh clab@172.20.20.11
```

```
conf t
interface Loopback0
 ipv4 address 1.1.1.1 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description R1-to-R2
 ipv4 address 10.0.12.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description R1-to-R3
 ipv4 address 10.0.13.1 255.255.255.252
 no shutdown
!
segment-routing
 global-block 16000 23999
!
router ospf 1
 router-id 1.1.1.1
 segment-routing mpls
 segment-routing forwarding mpls
 area 0
  interface Loopback0
   passive enable
   prefix-sid index 1
  !
  interface GigabitEthernet0/0/0/0
   network point-to-point
  !
  interface GigabitEthernet0/0/0/1
   network point-to-point
  !
 !
!
segment-routing
 traffic-eng
  segment-list VIA-R3-TO-R4
   index 10 mpls label 16003
   index 20 mpls label 16004
  !
  policy SR-TE-VIA-R3
   color 100 end-point ipv4 1.1.1.4
   binding-sid mpls 15100
   candidate-paths
    preference 100
     explicit segment-list VIA-R3-TO-R4
    !
   !
  !
 !
!
router static
 address-family ipv4 unicast
  1.1.1.4/32 sr-policy srte_c_100_ep_1.1.1.4
 !
!
commit
end
```

---

### R2

```bash
ssh clab@172.20.20.12
```

```
conf t
interface Loopback0
 ipv4 address 1.1.1.2 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description R2-to-R1
 ipv4 address 10.0.12.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description R2-to-R4
 ipv4 address 10.0.24.1 255.255.255.252
 no shutdown
!
segment-routing
 global-block 16000 23999
!
router ospf 1
 router-id 1.1.1.2
 segment-routing mpls
 segment-routing forwarding mpls
 area 0
  interface Loopback0
   passive enable
   prefix-sid index 2
  !
  interface GigabitEthernet0/0/0/0
   network point-to-point
  !
  interface GigabitEthernet0/0/0/1
   network point-to-point
  !
 !
!
commit
end
```

---

### R3

```bash
ssh clab@172.20.20.13
```

```
conf t
interface Loopback0
 ipv4 address 1.1.1.3 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description R3-to-R1
 ipv4 address 10.0.13.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description R3-to-R4
 ipv4 address 10.0.34.1 255.255.255.252
 no shutdown
!
segment-routing
 global-block 16000 23999
!
router ospf 1
 router-id 1.1.1.3
 segment-routing mpls
 segment-routing forwarding mpls
 area 0
  interface Loopback0
   passive enable
   prefix-sid index 3
  !
  interface GigabitEthernet0/0/0/0
   network point-to-point
  !
  interface GigabitEthernet0/0/0/1
   network point-to-point
  !
 !
!
commit
end
```

---

### R4 - Tailend

```bash
ssh clab@172.20.20.14
```

```
conf t
interface Loopback0
 ipv4 address 1.1.1.4 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description R4-to-R2
 ipv4 address 10.0.24.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description R4-to-R3
 ipv4 address 10.0.34.2 255.255.255.252
 no shutdown
!
segment-routing
 global-block 16000 23999
!
router ospf 1
 router-id 1.1.1.4
 segment-routing mpls
 segment-routing forwarding mpls
 area 0
  interface Loopback0
   passive enable
   prefix-sid index 4
  !
  interface GigabitEthernet0/0/0/0
   network point-to-point
  !
  interface GigabitEthernet0/0/0/1
   network point-to-point
  !
 !
!
commit
end
```

---

## Validação

Execute os comandos abaixo em R1, na ordem. A validação está dividida em duas partes: primeiro confirma que a base SR-MPLS está saudável, depois verifica o comportamento específico do SR-TE.

### Base SR-MPLS

**Vizinhos OSPF**

```
show ospf neighbor
```

> Esperado: R2 e R3 em estado FULL. Se algum estiver em estado diferente, aguarde alguns segundos e repita.

**SIDs distribuídos pelo OSPF**

```
show ospf segment-routing sid-database
```

> Esperado: labels 16001, 16002, 16003 e 16004 presentes, um por node.

**LFIB populada**

```
show mpls forwarding
```

> Esperado: entradas para 16002, 16003 e 16004 com next-hop e interface de saída corretos.

---

### SR-TE

**SR Policy ativa**

```
show segment-routing traffic-eng policy color 100
```

> Esperado: `Admin: up, Oper: up` com Segment List `[16003, 16004]` ativo.

**Binding-SID na LFIB**

```
show mpls forwarding labels 15100
```

> Esperado: label 15100 mapeado para o Segment List da policy.

**Caminho IGP - referência**

```
traceroute 1.1.1.4 source 1.1.1.1
```

> Esperado: probes distribuídos entre R2 e R3. Este é o comportamento padrão do IGP sem SR-TE - guarda para comparar com o próximo resultado.

**Caminho SR-TE - forçado**

```
traceroute mpls sr-policy name srte_c_100_ep_1.1.1.4 verbose
```

> Esperado: caminho passa apenas por R3, nunca por R2. Se R3 aparece e R2 não, o SR-TE está funcionando corretamente.

---

## Derrubar o lab

```bash
cd ~/labs/sr-mpls/cisco/lab01_sr-te
containerlab destroy -t lab01_sr-te.clab.yml
```

---
## Conclusão

Este lab demonstra na prática a diferença entre o encaminhamento IGP e o encaminhamento
SR-TE. O OSPF faz o que foi projetado para fazer: distribui o tráfego pelos caminhos de
menor custo, usando ECMP quando os custos são iguais. O SR-TE não disputa com o IGP -
ele simplesmente substitui a decisão de encaminhamento para o tráfego que passa pela
policy, sem alterar nada no restante da rede.

O que ficou provado aqui é que um único ponto de configuração - o headend -, é suficiente
para controlar o caminho de ponta a ponta. R2 e R3 não sabem que existe uma SR Policy.
R4 não foi tocado. A rede convergiu normalmente pelo IGP e a policy operou em paralelo,
de forma completamente stateless.

Esse é o ponto central do SR-TE: expressar intenção de encaminhamento no pacote, e não
na rede.



## Referências

- Containerlab XRd Kind: https://containerlab.dev/manual/kinds/xrd/
- Cisco XRd Docs: https://xrdocs.io/virtual-routing/tutorials/2022-08-22-setting-up-host-environment-to-run-xrd
- WWT Multi-Domain SR-TE Lab: https://www.wwt.com/lab/multi-domain-sr-te-lab
- RFC 9256 - Segment Routing Policy Architecture: https://datatracker.ietf.org/doc/html/rfc9256
- Cisco IOS-XR SR-TE Configuration Guide: https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x/configure-sr-te-policies.html

---

> AVISO: A imagem `sbezverk/xrd-control-plane:7.10.2` utilizada neste lab não é oficial
> da Cisco. Trata-se de uma imagem de terceiro disponibilizada publicamente no Docker Hub
> para fins educacionais. Sua disponibilidade não é garantida e pode ser removida a qualquer
> momento. Esta imagem não deve ser utilizada fora de ambientes de teste isolados.