
# ECS 架构

> Entity-Component-System——数据驱动设计的游戏架构, SoA 内存布局, Archetype, 稀疏集。

## 概念

ECS (Entity-Component-System) 是现代游戏引擎的核心数据架构，与传统的 OOP 继承树完全相反。在 ECS 中: Entity 只是一个 ID, Component 是纯数据 (无行为), System 是纯逻辑 (无状态)。这种分离带来三个根本优势: 缓存友好的数据布局 (SoA), 自然的并行化, 极高的模块复用性。

## 核心概念对比

| 概念 | OOP 继承 | ECS |
|------|---------|-----|
| 对象定义 | class Player : Entity { ... } | Entity ID = 42 |
| 数据 | 成员变量散布在继承树的各层 | Component: Position{x,y,z}, Velocity{vx,vy,vz} |
| 行为 | 成员方法 + 虚函数 | System: MoveSystem(Position, Velocity) |
| 内存布局 | AoS (Array of Structs) | SoA (Struct of Arrays) |
| 扩展方式 | 继承新类 | 添加新 Component 或新 System |

## ECS 基础模型

```
Entity: [ID=1001] // 无数据, 仅标识符
Entity: [ID=1002]
Entity: [ID=1003]

Components (按类型存储, SoA):
 Position: [(1001: 0,1,0), (1002: 5,2,1), (1003: -1,3,0)]
 Velocity: [(1001: 1,0,0), (1003: 0,0,1)]
 Health: [(1001: 100), (1002: 50), (1003: 200)]
 PlayerTag: [(1001)]
 EnemyTag: [(1002), (1003)]

Systems:
 MoveSystem: FOR (Position, Velocity) ← 查询拥有这两个组件的实体
 position += velocity * dt
 // 只遍历: (1001), (1003) — 因为有 Position + Velocity
 DamageSystem: FOR (Health, EnemyTag)
 ...
 RenderSystem: FOR (Position, Model)
 ...
```

## 内存布局: AoS vs SoA

```
AoS (Array of Structs) — OOP 方式:
 struct Entity {
 Position pos;
 Velocity vel;
 Health hp;
 };
 内存: [pos|vel|hp] [pos|vel|hp] [pos|vel|hp] ...
 问题: MoveSystem 只需要 pos 和 vel, 但 hp 也被加载到缓存 (浪费)

SoA (Struct of Arrays) — ECS 方式:
 Position[] pos_array = {(0,1,0), (5,2,1), ...};
 Velocity[] vel_array = {(1,0,0), (0,0,1), ...};
 内存: [pos|pos|pos|...] [vel|vel|vel|...]
 优势: MoveSystem 遍历时, 所有 pos 连续存放, 缓存命中率最大化
```

## Archetype (原型)

```
Archetype = 一组特定 Component 类型的集合

例如:
 Archetype<Position, Velocity, Health, PlayerTag> → 实体 1001
 Archetype<Position, Health, EnemyTag> → 实体 1002, 1003
 Archetype<Position, Velocity> → 无实体

原型存储 (Unity DOTS / Bevy 方式):
 每个 Archetype 内存块连续存储其实体的所有 Component:

 Chunk (Archetype<Position, Velocity, Health, PlayerTag>, 容量=64):
 [Pos][Pos]...[Pos] [Vel][Vel]...[Vel] [HP][HP]...[HP] [EntityID...]
 <-- 64 个实体, 每列连续排列 -->

迭代效率:
 MoveSystem 需要: Position + Velocity
 匹配的 Archetype: Archetype<Position, Velocity, Health, PlayerTag>
 Archetype<Position, Velocity>
 遍历这些 Archetype 的 Chunk, 逐列读取 → 极佳缓存友好
```

## Sparse Set (稀疏集)

```
另一种 ECS 存储方案 (EnTT, flecs):

Sparse Set 实现:
 // 每个 Component 类型有一个 Sparse Set
 SparseSet<Position>:
 sparse[]: // Entity → 索引 (大小 = max_entity_count)
 dense[]: // 索引 → Entity 实际数据
 packed[]: // [Position{0,1,0}, Position{5,2,1}, Position{-1,3,0}]

 查询 Position + Velocity:
 选择 dense 更小的 SparseSet, 遍历其 dense
 检查每个 Entity 是否也存在于另一个 SparseSet 中
 // O(min(|A|, |B|)) 迭代, O(1) 检查

 添加/删除 Component = SparseSet 的插入/删除 = O(1)
 比 Archetype 更灵活 (不需要移动 Archetype)
 但缓存局部性不如 Archetype 方案
```

---

