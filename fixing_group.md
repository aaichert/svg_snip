# Fixing Group Rendering and Definition Propagation

## Background

`svg_snip` is designed as a stateless, functional SVG layout engine. The core idea is that all rendering state is created on the fly during execution and never stored permanently in mutable object state.

Key concepts:
- `Group` behaves like a callable function via `__call__`.
- `Composer` is the root renderer that assembles SVG from children.
- Advanced shape helpers return plain SVG snippets and can declare reusable definitions via `Composer.declare(func, definitions)`.
- `Group` instances may be nested and may themselves be returned from utility functions.

## Problem

When a nested `Group` is used, global SVG definitions registered by functions inside that group are not collected into the final `<defs>` block.

Root cause:
- `Composer.render()` and `Group.__call__()` assume children are only flat executable shape functions.
- Nested `Group` children are not properly executed in rendering mode and their recorded functions are not bubbled up.
- As a result, the final render misses definitions such as marker declarations used by advanced elements like `arrow`.

## Desired Engine Behavior

The rendering pass must propagate tracking data up the call stack without introducing mutable rendering state.

### `Group.__call__`

Signature:
```python
def __call__(self, *, composer=None, **call_kwargs):
```

Behavior:
- If `composer` is present, the call is part of a rendering pass.
- During rendering, the group should build a local set of recorded functions used by its children.
- For grouped children:
  - If a child is another `Group`, invoke it with `composer=composer` and collect its returned `recorded_functions` set.
  - If a child is a leaf function, invoke it with the same composer context.
- If `composer` is not provided, the call should behave as a plain string-producing function.

Return value:
- In rendering mode (`composer is not None`): return `(svg_code, local_recorded_functions)`.
- In normal mode: return just `svg_code`.

### `Composer.render`

Behavior:
- Iterate over top-level children.
- Always pass `composer=self` down into child execution during render.
- Accept both plain string results and `(svg_string, recorded_functions)` tuples.
- Merge all recorded function sets from nested groups into the master set.
- Use the master set to collect definitions from `Group.declared_shapes` and build `<defs>`.

### Native comment support

Add a lightweight, stateless `comment(text, **kwargs)` helper.
- It should return a safe string like `<!-- text -->`.
- It should not require global shape registration.
- Group rendering loops must handle such plain strings gracefully.

## Implementation Plan

1. Add or ensure a native `comment()` helper exists in `Composer.py`.
2. Update `Group.__call__()` to:
   - accept `composer=None` and `**call_kwargs`.
   - build `local_recorded_functions = set()` in rendering mode.
   - call nested `Group` children with `composer=composer`.
   - add non-group child functions into `local_recorded_functions`.
   - return `(svg_code, local_recorded_functions)` only when `composer is not None`.
3. Update `Composer.render()` to:
   - pass `composer=self` into every child call.
   - detect tuple return values from child execution.
   - append the SVG text and merge recorded function sets.
   - still support plain leaf-string returns.
4. Ensure `Group.declared_shapes` remains the shared registry for declared SVG definitions.
5. Add or update tests to cover:
   - nested groups produced by utility functions.
   - declared definitions from nested groups appearing in final `<defs>`.
   - plain comment children in groups.

## Example Use Case

A stateless utility should return a `Group` directly:

```python
from svg_snip.Composer import Group
from svg_snip.Elements import comment
import e3d


def svg_world_geometry(P, **kwargs):
    group = Group()
    group.add(comment, text="Start of World Space Coordinate Axes")
    group.add(e3d.arrow, P=P, X1=[0,0,0,1], X2=[100,0,0,1], stroke='red', **kwargs)
    group.add(e3d.arrow, P=P, X1=[0,0,0,1], X2=[0,100,0,1], stroke='green', **kwargs)
    group.add(e3d.arrow, P=P, X1=[0,0,0,1], X2=[0,0,100,1], stroke='blue', **kwargs)
    return group
```

The engine should then render this nested `Group` and include any `e3d.arrow` declared definitions automatically.

## Summary

This fix preserves the stateless, functional philosophy of `svg_snip` while enabling nested group utilities to participate fully in render-time definition collection. The main change is to treat `composer` as the rendering-pass marker and to carry `(svg_code, recorded_functions)` tuples upward through nested groups.
