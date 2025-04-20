import matplotlib
matplotlib.use('Agg')  # 使用非互動式後端，確保在無GUI環境下也能運行

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from matplotlib.patches import Patch
import matplotlib.patheffects as PathEffects
import os
import traceback
import time

# 獲取目前腳本所在的目錄路徑
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 定義模擬數據
PROCESSOR_COUNT = 4
TASK_COUNT = 20
EDGE_COUNT = 35

# 默認任務計算時間
comp_costs = [
    0.0, 80.0, 40.0, 40.0, 40.0, 40.0, 40.0, 60.0, 30.0, 30.0,
    30.0, 30.0, 40.0, 20.0, 20.0, 20.0, 20.0, 10.0, 10.0, 0.0
]

# 默認任務依賴和通信量
dependencies = [
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

# 解析HW01-1.txt獲取任務計算時間和依賴數據
def parse_problem_file(filename):
    """解析問題定義文件，獲取計算時間和依賴關係"""
    global PROCESSOR_COUNT, TASK_COUNT, EDGE_COUNT, comp_costs, dependencies
    
    # 使用絕對路徑
    file_path = os.path.join(SCRIPT_DIR, filename)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            # 尋找處理器個數、工作個數、有向邊個數
            for i, line in enumerate(lines):
                if "處理器個數" in line:
                    PROCESSOR_COUNT = int(lines[i+1].strip())
                    TASK_COUNT = int(lines[i+2].strip())
                    EDGE_COUNT = int(lines[i+3].strip())
                    print(f"讀取基本參數: 處理器個數={PROCESSOR_COUNT}, 工作個數={TASK_COUNT}, 有向邊個數={EDGE_COUNT}")
                    break
            
            # 尋找計算成本矩陣
            comp_costs = []
            comp_cost_section = False
            for i, line in enumerate(lines):
                if "theCompCost" in line:
                    comp_cost_section = True
                    continue
                if comp_cost_section and len(line.strip()) > 0 and "段" not in line and "ID" not in line:
                    try:
                        # 處理每一行，只取第一個處理器的值（因為題目中每個任務在不同處理器上時間相同）
                        values = line.strip().replace("00", "0.0").replace(".0.", ".0 .").split()
                        if values:
                            try:
                                comp_costs.append(float(values[0]))
                            except:
                                pass
                    except Exception as e:
                        print(f"解析計算成本行出錯: {line}, 錯誤: {e}")
                
                # 如果已獲取足夠任務數，則停止
                if len(comp_costs) == TASK_COUNT:
                    break
            
            # 尋找任務依賴和數據傳輸量
            dependencies = []
            transfer_data_section = False
            for i, line in enumerate(lines):
                if "TransData" in line:
                    transfer_data_section = True
                    continue
                if transfer_data_section and len(line.strip()) > 0 and "段" not in line and "ID" not in line:
                    values = line.strip().split()
                    if len(values) >= 3:
                        try:
                            from_task = int(values[0])
                            to_task = int(values[1])
                            data_vol = float(values[2])
                            dependencies.append((from_task, to_task, data_vol))
                        except:
                            pass
                
                # 如果已獲取足夠依賴數，則停止
                if len(dependencies) == EDGE_COUNT:
                    break
            
            print(f"讀取完成: {len(comp_costs)}個任務計算時間和{len(dependencies)}個依賴關係")
            
    except Exception as e:
        print(f"解析問題文件時出錯: {e}")
        traceback.print_exc()

# 解析HW01-2.txt獲取解決方案
def parse_solutions_file(filename):
    """解析解決方案文件，獲取所有解決方案"""
    solutions = []
    
    # 使用絕對路徑
    file_path = os.path.join(SCRIPT_DIR, filename)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("ss ="):
                    ss_text = line.replace("ss =", "").strip()
                    ss_text = ss_text.replace("{", "").replace("}", "").replace(" ", "")
                    ss = [int(x) for x in ss_text.split(",")]
                    
                    # 尋找對應的ms
                    if i + 1 < len(lines) and lines[i+1].strip().startswith("ms ="):
                        ms_text = lines[i+1].replace("ms =", "").strip()
                        ms_text = ms_text.replace("{", "").replace("}", "").replace(" ", "")
                        ms = [int(x) for x in ms_text.split(",")]
                        
                        if len(ss) == len(ms):
                            solution = {'ss': ss, 'ms': ms}
                            solutions.append(solution)
                            print(f"已解析解決方案 {len(solutions)}: {len(ss)}個任務分配")
                    
                i += 1
                
            print(f"總共解析了{len(solutions)}個解決方案")
            
    except Exception as e:
        print(f"解析解決方案文件時出錯: {e}")
        traceback.print_exc()
        
    return solutions

# 評估解決方案
def evaluate_solution(solution):
    """評估解決方案，計算任務的開始時間、結束時間和總耗時"""
    ss = solution['ss']
    ms = solution['ms']
    
    # 初始化處理器的完成時間
    processor_finish_time = [0] * PROCESSOR_COUNT
    
    # 初始化任務開始和結束時間
    task_start_times = [0] * TASK_COUNT
    task_end_times = [0] * TASK_COUNT
    
    # 建立任務的前置依賴
    predecessors = {}
    for from_task, to_task, data_vol in dependencies:
        if to_task not in predecessors:
            predecessors[to_task] = []
        predecessors[to_task].append((from_task, data_vol))
    
    # 根據排程順序處理任務
    for task_idx in ss:
        processor = ms[task_idx]
        
        # 計算任務的最早開始時間（考慮前置依賴）
        earliest_start = 0
        if task_idx in predecessors:
            for from_task, data_vol in predecessors[task_idx]:
                # 前置任務必須完成
                pred_end = task_end_times[from_task]
                
                # 如果前置任務和當前任務在不同處理器，需要考慮通信時間
                if ms[from_task] != processor and data_vol > 0:
                    comm_time = data_vol  # 假設通信率為1
                    pred_end += comm_time
                
                earliest_start = max(earliest_start, pred_end)
        
        # 任務開始時間
        start_time = max(earliest_start, processor_finish_time[processor])
        
        # 計算執行時間
        execution_time = comp_costs[task_idx]
        
        # 任務結束時間
        end_time = start_time + execution_time
        
        # 更新數據
        task_start_times[task_idx] = start_time
        task_end_times[task_idx] = end_time
        processor_finish_time[processor] = end_time
    
    # 計算總耗時
    makespan = max(task_end_times)
    
    # 更新解決方案
    solution['start_times'] = task_start_times
    solution['end_times'] = task_end_times
    solution['makespan'] = makespan
    
    return solution

def draw_gantt_chart(solution_index, solution):
    """繪製指定解決方案的甘特圖"""
    try:
        ss = solution['ss']
        ms = solution['ms']
        task_start_times = solution['start_times']
        task_end_times = solution['end_times']
        makespan = solution['makespan']
        
        # 設置顏色映射
        colors = plt.cm.get_cmap('tab20', TASK_COUNT)
        
        fig, ax = plt.subplots(figsize=(16, 8))
        y_ticks = []
        y_labels = []
        
        # 為每個處理器繪製任務條
        for processor in range(PROCESSOR_COUNT):
            y_pos = processor
            y_ticks.append(y_pos)
            y_labels.append(f'P{processor}')
            
            # 查找分配給此處理器的任務
            # 保存每個位置的標籤，用於檢測重疊
            label_positions = {}
            
            # 先按結束時間排序，這樣可以優先處理較早結束的任務
            tasks_on_processor = []
            for task_idx, proc in enumerate(ms):
                if proc == processor:
                    start_time = task_start_times[task_idx]
                    end_time = task_end_times[task_idx]
                    duration = end_time - start_time
                    if duration > 0:
                        tasks_on_processor.append((task_idx, start_time, end_time, duration))
            
            # 按結束時間排序
            tasks_on_processor.sort(key=lambda x: x[2])
            
            for task_idx, start_time, end_time, duration in tasks_on_processor:
                # 繪製任務條
                ax.barh(y_pos, duration, left=start_time, height=0.8, 
                        color=colors(task_idx % 20), alpha=0.8, 
                        edgecolor='black', linewidth=1)
                
                # 添加任務ID標籤在中間位置
                task_middle = start_time + duration/2
                ax.text(task_middle, y_pos, f't{task_idx}', 
                        ha='center', va='center', fontsize=11, fontweight='bold',
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))
                
                # 檢查標籤是否會重疊
                offset = -0.3  # 初始垂直偏移
                
                # 檢查此結束時間附近是否已有標籤
                too_close = False
                for pos, time_range in label_positions.items():
                    # 如果兩個標籤之間的時間間隔小於標籤寬度的估計值，則認為可能重疊
                    if abs(task_middle - pos) < duration/4:
                        too_close = True
                        # 找到一個新的垂直偏移
                        if offset > -0.4:
                            offset = -0.4
                        else:
                            offset = -0.2
                
                # 記錄此標籤位置
                label_positions[task_middle] = (start_time, end_time)
                
                # 在任務下方添加結束時間標記
                ax.text(task_middle, y_pos + offset, f'{end_time:.1f}', 
                        ha='center', va='center', fontsize=9, color='black', fontweight='bold',
                        bbox=dict(facecolor='lightyellow', alpha=0.9, edgecolor='gray', boxstyle='round,pad=0.1'))
        
        # 設置軸標籤和標題
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.set_xlabel('time', fontsize=12)
        ax.set_ylabel('processor', fontsize=12)
        ax.set_title(f'task scheduling gantt chart (solution {solution_index+1})\ntotal time: {makespan:.2f}', fontsize=16)
        
        # 設置網格線以輔助對齊時間
        ax.grid(axis='x', linestyle='--', alpha=0.6)
        
        # 設置合適的時間範圍，略大於總時長
        ax.set_xlim(-0.5, makespan * 1.1)
        
        # 根據任務結束時間設置x軸刻度
        time_ticks = []
        # 收集所有任務的結束時間
        all_end_times = sorted(list(set([end_time for end_time in task_end_times if end_time > 0])))
        
        # 如果結束時間太多，選擇一部分有代表性的時間點
        if len(all_end_times) > 15:
            # 均勻選擇時間點
            step = max(1, len(all_end_times) // 15)
            time_ticks = [0] + [all_end_times[i] for i in range(0, len(all_end_times), step)]
            # 確保包含最大時間
            if all_end_times[-1] not in time_ticks:
                time_ticks.append(all_end_times[-1])
        else:
            time_ticks = [0] + all_end_times
        
        ax.set_xticks(time_ticks)
        
        # 添加圖例顯示任務對應顏色
        legend_elements = []
        for task in range(min(20, TASK_COUNT)):  # 限制圖例數量，避免過多
            legend_elements.append(Patch(facecolor=colors(task % 20), edgecolor='black',
                                    label=f'task {task}'))
        
        # 將圖例放在右側
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5), 
                title="task legend", fontsize=9)
        
        # 調整布局並保存
        plt.tight_layout()
        plt.savefig(f'gantt_chart_solution_{solution_index+1}.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"已保存解決方案 {solution_index+1} 的甘特圖")
        
    except Exception as e:
        print(f"繪製甘特圖時出錯: {e}")
        traceback.print_exc()

def draw_makespan_comparison(solutions):
    """繪製所有解決方案的總耗時比較圖"""
    try:
        makespans = [solution['makespan'] for solution in solutions]
        
        plt.figure(figsize=(10, 6))
        
        # 準備數據
        solution_indices = [f"solution {i+1}" for i in range(len(makespans))]
        
        # 繪製柱狀圖
        bars = plt.bar(solution_indices, makespans, color='skyblue', edgecolor='black', linewidth=1.2)
        
        # 在柱子上方顯示具體數值
        for bar, makespan in zip(bars, makespans):
            plt.text(bar.get_x() + bar.get_width()/2, makespan + 5, f"{makespan:.2f}",
                   ha='center', va='bottom', fontweight='bold')
        
        # 添加標題和標籤
        plt.title('all solutions total time comparison', fontsize=14)
        plt.xlabel('plane', fontsize=12)
        plt.ylabel('total time', fontsize=12)
        
        # 突出顯示最佳解決方案
        best_solution_idx = makespans.index(min(makespans))
        bars[best_solution_idx].set_color('green')
        plt.text(bars[best_solution_idx].get_x() + bars[best_solution_idx].get_width()/2, 
                min(makespans) / 2, 'best solution', ha='center', va='center', 
                fontweight='bold', color='white',
                bbox=dict(facecolor='green', alpha=0.6, boxstyle='round,pad=0.5'))
        
        # 顯示網格線
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig('makespan_comparison.png', dpi=300)
        plt.close()
        print("已保存總耗時比較圖為 'makespan_comparison.png'")
        
    except Exception as e:
        print(f"繪製總耗時比較圖時出錯: {e}")

def export_solutions_and_execution_time_to_text(solutions, execution_time):
    """將所有解決方案的工作時間和程式執行時間輸出到同一個文字檔"""
    try:
        with open('hw01_2_solutions_and_execution_time.txt', 'w', encoding='utf-8') as f:
            for i, solution in enumerate(solutions):
                f.write(f"解決方案 {i+1}:\n")
                f.write(f"總耗時: {solution['makespan']:.2f}\n")
                f.write("任務ID\t開始時間\t結束時間\n")
                
                # 按任務ID順序輸出
                for task_idx in range(TASK_COUNT):
                    start_time = solution['start_times'][task_idx]
                    end_time = solution['end_times'][task_idx]
                    f.write(f"{task_idx}\t{start_time:.2f}\t{end_time:.2f}\n")
                
                f.write("\n")
            
            f.write(f"程式執行總耗時: {execution_time:.2f} 秒\n")
            
        print("已將所有解決方案的工作時間和程式執行時間輸出到 'hw01_2_solutions_and_execution_time.txt'")
        
    except Exception as e:
        print(f"輸出解決方案和程式執行時間到文字檔時出錯: {e}")

if __name__ == "__main__":
    start_time = time.time()
    
    # 解析問題案例文件
    parse_problem_file("HW01-1.txt")
    
    # 解析解決方案文件
    all_solutions = parse_solutions_file("HW01-2.txt")
    
    # 評估所有解決方案
    evaluated_solutions = []
    for i, solution in enumerate(all_solutions):
        print(f"\n評估解決方案 {i+1}:")
        evaluated_solution = evaluate_solution(solution)
        evaluated_solutions.append(evaluated_solution)
        print(f"總耗時: {evaluated_solution['makespan']:.2f}")
    
    # 繪製所有解決方案的甘特圖
    for i, solution in enumerate(evaluated_solutions):
        draw_gantt_chart(i, solution)
    
    # 繪製總耗時比較圖
    draw_makespan_comparison(evaluated_solutions)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # 輸出所有解決方案的工作時間和程式執行時間到同一個文字檔
    export_solutions_and_execution_time_to_text(evaluated_solutions, execution_time)
    
    print(f"\n所有圖表已成功生成！程式執行耗時: {execution_time:.2f} 秒") 