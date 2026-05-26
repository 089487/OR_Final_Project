# Heuristic Implementations

The two greedy methods are implemented in `src/heuristics.py`. Both methods use
the same input contract as the ADP-aware ILP:

- one owned snake-draft pick per roster slot;
- ADP availability rule `adp + delta >= current_pick`;
- position eligibility, including hitter-only `Util`;
- immediate assignment of every drafted player to one roster position.

Neither heuristic reoptimizes previous assignments. This is intentional: the
goal is to compare the exact ILP benchmark with methods that remain fast on
large synthetic instances.

## Shared Data Structures

The implementation builds one max-heap per roster position. Python heaps are
min-heaps, so projected points are stored as negative values:

```text
heap[position] = [(-projected_points, player_index), ...]
```

Each player appears in every heap for which the player is eligible. Removed
players are handled by lazy deletion: heaps are cleaned only when their top
entry is inspected.

The implementation also maintains:

- `selected[player]`: whether the player has already been drafted;
- `alive[player]`: whether the player is still available under the current ADP
  window;
- `active_count[position]`: number of currently available, not-yet-selected
  players eligible for the position;
- `remaining[position]`: number of roster slots still open at the position;
- an expiration order sorted by `adp + delta`.

At each pick, players with `adp + delta < current_pick` expire before the next
choice is made.

## Direct Greedy

Direct Greedy chooses the scarcest open position, then drafts the highest-point
currently available player for that position.

For every open position \(p\), the method computes:

```text
scarcity_ratio[p] = remaining[p] / active_count[p]
```

It chooses the position with the largest tuple:

```text
(scarcity_ratio[p], best_available_points[p])
```

Then it drafts the heap-top player for that position, marks the player selected,
decrements all active counts for that player's eligible positions, and reduces
`remaining[p]` by one.

If no open position has an available eligible player, the run is marked
`INFEASIBLE`.

## Opportunity Cost Greedy

Opportunity Cost Greedy compares the best current player at each open position
with the best player expected to remain available at the next owned pick.

It maintains two availability views:

- `current`: players available at the current pick;
- `future`: players expected to remain at the next owned pick.

For every open position \(p\), it computes:

```text
current_points[p] = best currently available points for p
future_points[p] = best points for p expected to remain at next pick
opportunity_cost[p] = current_points[p] - future_points[p]
```

The normal priority is:

```text
(0, opportunity_cost[p], current_points[p])
```

The method also includes a feasibility fallback for tight supply. A position is
treated as forced when either condition holds:

```text
current_count[p] <= remaining[p]
future_count[p] < remaining[p]
```

Forced positions receive higher priority:

```text
(1, remaining[p] / current_count[p], current_points[p])
```

If no positive opportunity-cost choice is necessary, the method still drafts a
fallback player using the same scarcity-style priority:

```text
(remaining[p] / current_count[p], current_points[p])
```

This fallback is what prevents the heuristic from waiting too long in tight
position-supply cases. After drafting, the selected player is removed from both
current and future availability views, and the assigned roster slot is filled.

## Complexity Intuition

Let:

- \(n\): number of players;
- \(p\): number of roster positions;
- \(r\): roster size;
- \(e\): average eligible positions per player.

Building heaps costs approximately \(O(ne)\). Lazy heap operations add
logarithmic factors. Each draft pick scans the roster positions, so the dominant
practical cost is approximately:

```text
O(ne log n + rp log n)
```

This is much smaller than building and solving the full ILP on the large stress
instances, whose approximate variable count is reported as:

```text
approx_variable_count = n * (1 + p + r)
```
