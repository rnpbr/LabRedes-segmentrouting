# SR Microloop Avoidance

## Contexto

Todos os labs anteriores tratam do intervalo entre a falha e a ativação do backup - o TI-LFA garante que esse intervalo seja coberto em menos de 50ms por um caminho pré-calculado e livre de loops. Este lab trata do que acontece **depois** desse intervalo: a reconvergência "de verdade" do IGP, quando cada roteador do domínio recalcula SPF e atualiza sua FIB para refletir a topologia definitiva.

Esse processo não é instantâneo nem simultâneo entre roteadores - é aí que mora o **microloop**, um problema anterior e independente do Segment Routing, presente em qualquer rede IP com roteamento hop-by-hop. Ver [`concepts.md`](../concepts.md) para a explicação completa do mecanismo antes de seguir.

---

## Topologia
