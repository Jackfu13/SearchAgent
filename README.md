# PA1-5: AI Grid Coloring Agent

An AI agent that uses first-choice hill climbing with random restarts to solve a grid coloring puzzle. The agent fills an n×n grid by placing colored shapes such that no two adjacent cells share the same color, while minimizing shapes and colors used.

## How It Works

The agent interacts with a PyGame grid environment through an `execute()` interface. It places colored shapes (brushes) onto the grid, choosing from 9 shape types and 4 colors.

### Algorithm

1. **First-Choice Hill Climbing**: Each step, the agent picks a random empty cell and tries to place the largest valid shape that covers it. If the move improves the objective score, it is accepted. Otherwise, it is undone.
2. **Random Restarts**: If the agent gets stuck (300+ consecutive failed attempts), it undoes all placements and starts over.
3. **Shape Priority**: Larger shapes are tried first (4-cell, then 3-cell, then 2-cell, then 1-cell) to minimize total shape count.
4. **Color Minimization**: The agent prefers reusing colors 0 and 1 to keep the number of distinct colors low.

### Objective Function

The scoring function balances four factors:
- Empty cells (high penalty)
- Adjacency violations (highest penalty)
- Number of shapes used (low penalty)
- Number of distinct colors used (low penalty)

## Files

- `hw1.py` - The AI agent implementation
- `gridgame.py` - The PyGame grid environment

## Running

```bash
python hw1.py
```

Set `GUI=True` in `hw1.py` to visualize the agent, or `GUI=False` for faster execution.
