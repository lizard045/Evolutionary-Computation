import matplotlib
matplotlib.use('Agg')  # 使用非互動式後端

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# 簡化的任務圖
G = nx.DiGraph()

# 添加節點
nodes = [
    (0, 0),
    (1, 80),
    (2, 40), (3, 40), (4, 40), (5, 40), (6, 40), (7, 60),
    (8, 30), (9, 30), (10, 30), (11, 30), (12, 40),
    (13, 20), (14, 20), (15, 20), (16, 20),
    (17, 10), (18, 10),
    (19, 0)
]

for node_id, weight in nodes:
    G.add_node(node_id, weight=weight)

# 添加關鍵邊
edges = [
    (0, 1, 0),
    (1, 2, 120), (1, 3, 120), (1, 4, 120), (1, 5, 120), (1, 6, 120), (1, 7, 120),
    (2, 19, 0),
    (3, 7, 80), (3, 8, 80),
    (4, 9, 80),
    (5, 10, 80),
    (6, 11, 80),
    (7, 8, 120), (7, 9, 120), (7, 10, 120), (7, 11, 120), (7, 12, 120),
    (8, 19, 0),
    (9, 12, 80), (9, 13, 80),
    (10, 14, 80),
    (11, 15, 80),
    (12, 13, 120), (12, 14, 120), (12, 15, 120), (12, 16, 120),
    (13, 19, 0),
    (14, 16, 80), (14, 17, 80),
    (15, 18, 80),
    (16, 17, 120), (16, 18, 120),
    (17, 19, 0),
    (18, 19, 0)
]

for source, target, weight in edges:
    G.add_edge(source, target, weight=weight)  # 添加所有邊，包括權重為0的邊

# 計算分層
levels = {}
for i, layer in enumerate(nx.topological_generations(G)):
    for node in layer:
        levels[node] = i

# 確保節點19在最底層
max_level = max(levels.values())
levels[19] = max_level + 1  # 將節點19設置為最底層

# 計算位置（由上而下的佈局）
pos = {}
nodes_by_level = {}
for node, level in levels.items():
    if level not in nodes_by_level:
        nodes_by_level[level] = []
    nodes_by_level[level].append(node)

# 計算每層節點的位置
for level, nodes in nodes_by_level.items():
    nodes.sort()  # 對同層節點排序
    width = len(nodes)
    for i, node in enumerate(nodes):
        # Y座標為負的層級（由上而下），X座標平均分布
        pos[node] = (i - width/2, -level)

# 調整節點19的位置，使其在水平方向上居中
pos[19] = (0, -levels[19])

# 創建圖形
plt.figure(figsize=(14, 10))

# 繪製節點
node_size = 1800
nx.draw_networkx_nodes(G, pos, node_size=node_size, 
                      node_color='lightblue', alpha=0.9,
                      linewidths=1)

# 繪製節點標籤
labels = {}
for node, data in G.nodes(data=True):
    if 'weight' in data and data['weight'] > 0:
        labels[node] = f"t{node}\n{data['weight']}"
    else:
        labels[node] = f"t{node}\n0"

nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')

# 繪製一般邊
regular_edges = [(u, v) for u, v in G.edges() if (u, v) not in [(2, 19), (8, 19), (13, 19), (17, 19), (18, 19)]]
nx.draw_networkx_edges(G, pos, 
                      edgelist=regular_edges,
                      arrows=True, 
                      width=1.2, 
                      arrowsize=15, 
                      node_size=node_size,
                      arrowstyle='->', 
                      edge_color='black',
                      alpha=0.7)

# 創建彎曲的邊來連接特定節點到19
highlighted_edges = [(2, 19), (8, 19), (13, 19), (17, 19), (18, 19)]

# 為每個特定邊定義不同的彎曲控制點
edge_curves = {
    (2, 19): 0.6,    # 較大的彎曲
    (8, 19): 0.4,    # 中等彎曲
    (13, 19): 0.2,   # 較小的彎曲
    (17, 19): -0.2,  # 負值表示彎曲方向相反
    (18, 19): -0.4   # 較大的負彎曲
}

# 用彎曲的路徑繪製高亮邊
for edge in highlighted_edges:
    start = pos[edge[0]]
    end = pos[edge[1]]
    
    # 計算控制點以創建彎曲
    rad = edge_curves[edge]
    
    # 繪製彎曲的邊
    nx.draw_networkx_edges(G, pos, 
                          edgelist=[edge],
                          width=2.5, 
                          edge_color='orange',
                          arrows=True,
                          arrowsize=20,
                          node_size=node_size,
                          arrowstyle='->',
                          alpha=1.0,
                          connectionstyle=f'arc3,rad={rad}')

# 繪製邊標籤
edge_labels = {}
for u, v, data in G.edges(data=True):
    if 'weight' in data and data['weight'] > 0:
        edge_labels[(u, v)] = str(int(data['weight']))
    else:
        edge_labels[(u, v)] = "0"  # 顯示權重為0的邊標籤

# 為常規邊添加標籤
nx.draw_networkx_edge_labels(G, pos, 
                            edge_labels={k: v for k, v in edge_labels.items() if k not in highlighted_edges}, 
                            font_size=9, 
                            font_color='black',
                            bbox=dict(facecolor='white', alpha=0.7, pad=2))

# 為彎曲的高亮邊添加標籤
for edge in highlighted_edges:
    nx.draw_networkx_edge_labels(G, pos, 
                               edge_labels={edge: edge_labels[edge]}, 
                               font_size=9, 
                               font_color='black',
                               bbox=dict(facecolor='white', alpha=0.7, pad=2),
                               connectionstyle=f'arc3,rad={edge_curves[edge]}')

# 設置圖形屬性
plt.title('directed acyclic graph(DAG)', fontsize=16)
plt.axis('off')
plt.tight_layout()

# 保存圖片
plt.savefig('task_dag_simple.png', dpi=300, bbox_inches='tight')
print("已保存DAG圖為task_dag_simple.png") 