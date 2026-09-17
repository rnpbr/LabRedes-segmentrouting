> Referencia externa, em ingles, mantida como material de origem.
> A versao canonica em portugues dos conceitos e convencoes deste projeto
> está preservado como referência histórica. Para os labs atuais, siga a
> [base SR-MPLS no IOS-XR](../../../../labs/cisco/sr-mpls/00-base/README.md).

# Cisco XRd 5-Node SR-MPLS Lab

This lab uses five Cisco XRd control-plane routers with `xrd-control-plane:7.10.2`.

```text
             p1
          /      \
       pe1        pe2
          \      /
             p2

          p1 -- p3 -- p2
```

The extra `p3` path lets you test ECMP, non-shortest SR policy paths, TI-LFA backup paths, and Flex-Algo constraints without making the lab too large.

## What This Lab Covers

- OSPFv2 SR-MPLS prefix-SIDs and node-SIDs
- SRGB and SRLB behavior
- OSPF adjacency SIDs
- ECMP and OSPF metric changes
- Explicit SR-TE policies using MPLS label segment lists
- Static-route traffic steering into an SR policy
- TI-LFA link and node protection
- OSPF Flexible Algorithm basics
- SR/MPLS verification and OAM commands

This XRd-only lab does not fully cover L3VPN, EVPN, SR-PCE/controller workflows, inter-domain SR, SRv6, or hardware convergence measurements. Those are natural follow-on labs.

## Start the Lab

```bash
cd cisco-sr-mpls-5node
sudo containerlab deploy -t lab.clab.yml
```

Connect to IOS XR:

```bash
docker exec -it clab-cisco-sr-mpls-5node-pe1 /pkg/bin/xr_cli.sh
docker exec -it clab-cisco-sr-mpls-5node-p1 /pkg/bin/xr_cli.sh
docker exec -it clab-cisco-sr-mpls-5node-p2 /pkg/bin/xr_cli.sh
docker exec -it clab-cisco-sr-mpls-5node-p3 /pkg/bin/xr_cli.sh
docker exec -it clab-cisco-sr-mpls-5node-pe2 /pkg/bin/xr_cli.sh
```

Default SSH access is also available with username `clab` and password `clab@123`.

## Interfaces and Addresses

Containerlab uses dash-separated XRd interface names such as `Gi0-0-0-0`. IOS XR sees the same port as `GigabitEthernet0/0/0/0`.

| Link | A-side | Address | B-side | Address |
| --- | --- | --- | --- | --- |
| pe1-p1 | pe1 Gi0/0/0/0 | 192.0.2.0/31 | p1 Gi0/0/0/0 | 192.0.2.1/31 |
| pe1-p2 | pe1 Gi0/0/0/1 | 192.0.2.2/31 | p2 Gi0/0/0/0 | 192.0.2.3/31 |
| p1-pe2 | p1 Gi0/0/0/1 | 192.0.2.4/31 | pe2 Gi0/0/0/0 | 192.0.2.5/31 |
| p2-pe2 | p2 Gi0/0/0/1 | 192.0.2.6/31 | pe2 Gi0/0/0/1 | 192.0.2.7/31 |
| p1-p3 | p1 Gi0/0/0/2 | 192.0.2.8/31 | p3 Gi0/0/0/0 | 192.0.2.9/31 |
| p3-p2 | p3 Gi0/0/0/1 | 192.0.2.10/31 | p2 Gi0/0/0/2 | 192.0.2.11/31 |

| Node | Loopback0 | Prefix-SID index | Label with SRGB 16000 |
| --- | --- | ---: | ---: |
| pe1 | 10.0.0.1/32 | 1 | 16001 |
| p1 | 10.0.0.2/32 | 2 | 16002 |
| p2 | 10.0.0.3/32 | 3 | 16003 |
| p3 | 10.0.0.4/32 | 4 | 16004 |
| pe2 | 10.0.0.5/32 | 5 | 16005 |

The lab uses the default SRLB, `15000-15999`, for manually allocated local segments such as adjacency SIDs and binding SIDs.

## Base OSPFv2 SR-MPLS Configuration

Paste the matching block on each router.

### pe1

```text
configure
hostname pe1
segment-routing global-block 16000 23999
segment-routing local-block 15000 15999
!
interface Loopback0
 ipv4 address 10.0.0.1 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description pe1 to p1
 ipv4 address 192.0.2.0 255.255.255.254
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description pe1 to p2
 ipv4 address 192.0.2.2 255.255.255.254
 no shutdown
!
router ospf 1
 router-id 10.0.0.1
 segment-routing mpls
 segment-routing sr-prefer
 area 0
  segment-routing mpls
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
commit
end
```

### p1

```text
configure
hostname p1
segment-routing global-block 16000 23999
segment-routing local-block 15000 15999
!
interface Loopback0
 ipv4 address 10.0.0.2 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description p1 to pe1
 ipv4 address 192.0.2.1 255.255.255.254
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description p1 to pe2
 ipv4 address 192.0.2.4 255.255.255.254
 no shutdown
!
interface GigabitEthernet0/0/0/2
 description p1 to p3
 ipv4 address 192.0.2.8 255.255.255.254
 no shutdown
!
router ospf 1
 router-id 10.0.0.2
 segment-routing mpls
 segment-routing sr-prefer
 area 0
  segment-routing mpls
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
  interface GigabitEthernet0/0/0/2
   network point-to-point
  !
 !
!
commit
end
```

### p2

```text
configure
hostname p2
segment-routing global-block 16000 23999
segment-routing local-block 15000 15999
!
interface Loopback0
 ipv4 address 10.0.0.3 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description p2 to pe1
 ipv4 address 192.0.2.3 255.255.255.254
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description p2 to pe2
 ipv4 address 192.0.2.6 255.255.255.254
 no shutdown
!
interface GigabitEthernet0/0/0/2
 description p2 to p3
 ipv4 address 192.0.2.11 255.255.255.254
 no shutdown
!
router ospf 1
 router-id 10.0.0.3
 segment-routing mpls
 segment-routing sr-prefer
 area 0
  segment-routing mpls
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
  interface GigabitEthernet0/0/0/2
   network point-to-point
  !
 !
!
commit
end
```

### p3

```text
configure
hostname p3
segment-routing global-block 16000 23999
segment-routing local-block 15000 15999
!
interface Loopback0
 ipv4 address 10.0.0.4 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description p3 to p1
 ipv4 address 192.0.2.9 255.255.255.254
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description p3 to p2
 ipv4 address 192.0.2.10 255.255.255.254
 no shutdown
!
router ospf 1
 router-id 10.0.0.4
 segment-routing mpls
 segment-routing sr-prefer
 area 0
  segment-routing mpls
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

### pe2

```text
configure
hostname pe2
segment-routing global-block 16000 23999
segment-routing local-block 15000 15999
!
interface Loopback0
 ipv4 address 10.0.0.5 255.255.255.255
!
interface GigabitEthernet0/0/0/0
 description pe2 to p1
 ipv4 address 192.0.2.5 255.255.255.254
 no shutdown
!
interface GigabitEthernet0/0/0/1
 description pe2 to p2
 ipv4 address 192.0.2.7 255.255.255.254
 no shutdown
!
router ospf 1
 router-id 10.0.0.5
 segment-routing mpls
 segment-routing sr-prefer
 area 0
  segment-routing mpls
  interface Loopback0
   passive enable
   prefix-sid index 5
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

## Baseline Verification

Run these on `pe1` first:

```text
show ospf neighbor
show ospf routes
show ospf segment-routing prefix-sid-map active-policy
show route 10.0.0.5/32 detail
show mpls forwarding
show mpls label table 0 label 16005 detail
ping 10.0.0.5 source 10.0.0.1
traceroute 10.0.0.5 source 10.0.0.1
```

Expected result: `pe1` should have two equal-cost paths to `pe2`, one through `p1` and one through `p2`. The prefix-SID for `pe2` is index `5`, so the SR label is `16005`.

## Lab 1: ECMP and OSPF Metrics

From `pe1`, both direct core paths should be equal:

```text
show route 10.0.0.5/32 detail
```

Make the path through `p2` less preferred:

```text
configure
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/1
   cost 50
  !
 !
!
commit
end
```

Verify that `pe1` now prefers `p1`:

```text
show ospf routes 10.0.0.5/32
show route 10.0.0.5/32 detail
show mpls forwarding labels 16005
```

Restore ECMP:

```text
configure
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/1
   no cost
  !
 !
!
commit
end
```

## Lab 2: Manual Adjacency SIDs

OSPF creates dynamic adjacency SIDs automatically. Manual adjacency SIDs are useful when you want stable local labels for explicit paths or controller workflows. The label is locally significant and allocated from the SRLB.

Configure protected manual adjacency SIDs on `pe1`:

```text
configure
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/0
   adjacency-sid index 11 protected
  !
  interface GigabitEthernet0/0/0/1
   adjacency-sid index 12 protected
  !
 !
!
commit
end
```

Verify:

```text
show mpls label table 0 detail
show ospf database opaque-area self-originate
show mpls forwarding
```

The exact labels are based on the SRLB base plus the configured index. With the default SRLB base `15000`, index `11` maps to label `15011`, and index `12` maps to label `15012`.

## Lab 3: Explicit SR Policy Through p3

The native shortest paths from `pe1` to `pe2` are:

```text
pe1-p1-pe2
pe1-p2-pe2
```

Create an SR policy on `pe1` that forces traffic through the longer path:

```text
pe1-p1-p3-p2-pe2
```

This segment list uses node-SID labels:

| Segment | Meaning |
| --- | --- |
| `16002` | reach `p1` |
| `16004` | then reach `p3` |
| `16003` | then reach `p2` |
| `16005` | then reach `pe2` |

Configure the policy on `pe1`:

```text
configure
segment-routing
 traffic-eng
  logging
   policy status
  !
  segment-list PE1_P1_P3_P2_PE2
   index 10 mpls label 16002
   index 20 mpls label 16004
   index 30 mpls label 16003
   index 40 mpls label 16005
  !
  policy PE1_TO_PE2_VIA_P3
   binding-sid mpls 15090
   color 100 end-point ipv4 10.0.0.5
   candidate-paths
    preference 100
     explicit segment-list PE1_P1_P3_P2_PE2
     !
    !
   !
  !
 !
!
commit
end
```

Verify the policy:

```text
show segment-routing traffic-eng policy color 100
show segment-routing traffic-eng policy name srte_c_100_ep_10.0.0.5
show mpls forwarding labels 15090
show mpls label table 0 label 15090 detail
```

The policy should be operationally up and should show the explicit segment list. Label `15090` is the binding SID for the policy. A binding SID is locally significant on the head-end router and represents the full policy.

## Lab 4: Static Route Steering Into the SR Policy

Add a test destination on `pe2`:

```text
configure
interface Loopback100
 description SR policy test endpoint
 ipv4 address 203.0.113.5 255.255.255.255
!
commit
end
```

On `pe1`, steer `203.0.113.5/32` into the SR policy. IOS XR uses the generated SR policy name in the RIB, so check the name first:

```text
show segment-routing traffic-eng policy color 100
```

Then configure the static route:

```text
configure
router static
 address-family ipv4 unicast
  203.0.113.5/32 sr-policy srte_c_100_ep_10.0.0.5
 !
!
commit
end
```

Verify:

```text
show route 203.0.113.5/32 detail
ping 203.0.113.5 source 10.0.0.1
traceroute 203.0.113.5 source 10.0.0.1
```

Expected result: the route should be known via `static` and should resolve through the SR-TE policy toward `10.0.0.5`.

## Lab 5: TI-LFA

TI-LFA computes preinstalled repair paths for link, node, or SRLG failures. Configure it on the core-facing OSPF interfaces.

On `pe1`:

```text
configure
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/0
   fast-reroute per-prefix
   fast-reroute per-prefix ti-lfa
   fast-reroute per-prefix tiebreaker node-protecting index 200
  !
  interface GigabitEthernet0/0/0/1
   fast-reroute per-prefix
   fast-reroute per-prefix ti-lfa
   fast-reroute per-prefix tiebreaker node-protecting index 200
  !
 !
!
commit
end
```

Use the same pattern on every non-loopback OSPF interface on `p1`, `p2`, `p3`, and `pe2`.

Verify from `pe1`:

```text
show route 10.0.0.5/32 detail
show cef ipv4 10.0.0.5/32 detail
show ospf routes 10.0.0.5/32
```

Then fail one path and watch the route stay installed through a repair path:

```text
configure
interface GigabitEthernet0/0/0/0
 shutdown
!
commit
end
```

Verify, then restore:

```text
show ospf neighbor
show route 10.0.0.5/32 detail
show mpls forwarding labels 16005
```

```text
configure
interface GigabitEthernet0/0/0/0
 no shutdown
!
commit
end
```

## Lab 6: Flexible Algorithm

Flex-Algo lets the IGP compute an alternate SPF using a different algorithm and different constraints. This example defines algorithm `128` to exclude links colored `red`.

The goal is to make algorithm `128` avoid these direct links:

```text
pe1-p2
p1-pe2
```

That leaves this path from `pe1` to `pe2`:

```text
pe1-p1-p3-p2-pe2
```

Configure the same Flex-Algo definition and affinity map on every router:

```text
configure
router ospf 1
 flex-algo 128
  advertise-definition
  priority 200
  affinity exclude-any
   red
  !
 !
 affinity-map
  color red bit-position 10
 !
!
commit
end
```

Add algorithm-specific prefix-SIDs. Use the matching index on each router:

| Node | Flex-Algo 128 SID index | Label with SRGB 16000 |
| --- | ---: | ---: |
| pe1 | 101 | 16101 |
| p1 | 102 | 16102 |
| p2 | 103 | 16103 |
| p3 | 104 | 16104 |
| pe2 | 105 | 16105 |

Example for `pe1`:

```text
configure
router ospf 1
 area 0
  interface Loopback0
   prefix-sid algorithm 128 index 101
  !
 !
!
commit
end
```

Use `102` on `p1`, `103` on `p2`, `104` on `p3`, and `105` on `pe2`.

Color both directions of the `pe1-p2` link red:

```text
! pe1
configure
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/1
   flex-algo affinity
    color red
   !
  !
 !
!
commit
end
```

```text
! p2
configure
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/0
   flex-algo affinity
    color red
   !
  !
 !
!
commit
end
```

Color both directions of the `p1-pe2` link red:

```text
! p1
configure
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/1
   flex-algo affinity
    color red
   !
  !
 !
!
commit
end
```

```text
! pe2
configure
router ospf 1
 area 0
  interface GigabitEthernet0/0/0/0
   flex-algo affinity
    color red
   !
  !
 !
!
commit
end
```

Verify:

```text
show ospf topology summary
show ospf routes flex-algo 128
show route 10.0.0.5/32 detail
show mpls label table 0 label 16105 detail
```

The regular algorithm still uses normal OSPF SPF. Algorithm `128` computes a constrained path that excludes red links. The Flex-Algo label for `pe2` is `16105`.

## Lab 7: SR/MPLS OAM

Basic IP reachability:

```text
ping 10.0.0.5 source 10.0.0.1
traceroute 10.0.0.5 source 10.0.0.1
```

MPLS forwarding and label checks:

```text
show mpls forwarding
show mpls forwarding labels 15090
show mpls label table 0 label 16005 detail
show mpls label table 0 label 16105 detail
```

Nil-FEC MPLS ping and traceroute can test a chosen label stack. From `pe1`, this tests the explicit label stack for `pe1-p1-p3-p2-pe2`:

```text
ping mpls nil-fec labels 16002,16004,16003,16005 output interface GigabitEthernet0/0/0/0 nexthop 192.0.2.1
traceroute mpls nil-fec labels 16002,16004,16003,16005 output interface GigabitEthernet0/0/0/0 nexthop 192.0.2.1
```

If the XRd control-plane image accepts the commands but does not return useful data-plane results, use the control-plane checks instead:

```text
show ospf database opaque-area
show ospf segment-routing prefix-sid-map active-policy
show segment-routing traffic-eng policy color 100
show route 203.0.113.5/32 detail
```

## Reset Useful Changes

Remove the static steering route:

```text
configure
router static
 address-family ipv4 unicast
  no 203.0.113.5/32 sr-policy srte_c_100_ep_10.0.0.5
 !
!
commit
end
```

Remove the SR policy:

```text
configure
segment-routing
 traffic-eng
  no policy PE1_TO_PE2_VIA_P3
  no segment-list PE1_P1_P3_P2_PE2
 !
!
commit
end
```

Destroy the lab:

```bash
sudo containerlab destroy -t lab.clab.yml --cleanup
```

## References

- Containerlab Cisco XRd kind: <https://containerlab.dev/manual/kinds/xrd/>
- Cisco IOS XR 7.10.x OSPF SR-MPLS: <https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x/configuring-segment-routing-for-ospf-protocol.html>
- Cisco IOS XR 7.10.x SRGB and SRLB: <https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x/configuring-sr-global-block-and-sr-local-block.html>
- Cisco IOS XR 7.10.x SR-TE policies: <https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x/configuring-sr-te-policy.html>
- Cisco IOS XR 7.10.x TI-LFA: <https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x/configuring-topology-independent-loop-free-alternate.html>
- Cisco IOS XR 7.10.x Flexible Algorithm: <https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x/enabling-segment-routing-flexible-algorithm.html>
- Cisco IOS XR 7.10.x SR OAM: <https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/710x/configuration/guide/b-segment-routing-cg-cisco8000-710x/using-segment-routing-oam.html>
