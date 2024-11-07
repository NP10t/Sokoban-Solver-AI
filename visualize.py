# import os
# import re
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np

# # Hàm đọc dữ liệu từ các file và lưu vào DataFrame
# def read_data_from_files(file_list):
#     data = []
#     for i, file_name in enumerate(file_list):
#         with open(file_name, 'r') as file:
#             content = file.read()
            
#             # Trích xuất dữ liệu của mỗi thuật toán trong file
#             algorithms = re.findall(r'(A\*|UCS|BFS|DFS)\nSteps: (\d+), Weight: (\d+), Node: (\d+), Time \(ms\): ([\d.]+), Memory \(MB\): ([\d.]+)', content)
#             for algorithm, steps, weight, nodes, time, memory in algorithms:
#                 data.append({
#                     'Test Case': f'Test {i+1}',
#                     'Algorithm': algorithm,
#                     'Steps': int(steps),
#                     'Weight': int(weight),
#                     'Nodes': int(nodes),
#                     'Time (ms)': float(time),
#                     'Memory (MB)': float(memory)
#                 })
    
#     # Chuyển đổi dữ liệu thành DataFrame
#     return pd.DataFrame(data)

# # Lấy danh sách các file output
# file_list = [f"output-{i:02}.txt" for i in range(1, 11)]  # output-01.txt đến output-10.txt
# df = read_data_from_files(file_list)

# # Danh sách các tiêu chí cần vẽ biểu đồ và tiêu đề của chúng
# criteria = ['Time (ms)', 'Memory (MB)', 'Nodes', 'Steps', 'Weight']
# titles = ['Execution Time', 'Memory Usage', 'Generated Nodes', 'Movement Steps', 'Total Push Weight']

# # Màu cho từng thuật toán
# colors = {
#     'A*': (160/255, 35/255, 52/255),       # rgb(160, 35, 52)
#     'UCS': (255/255, 173/255, 96/255),     # rgb(255, 173, 96)
#     'BFS': (255/255, 238/255, 173/255),    # rgb(255, 238, 173)
#     'DFS': (150/255, 206/255, 180/255)     # rgb(150, 206, 180)
# }

# # Vẽ từng biểu đồ riêng biệt cho mỗi tiêu chí với các test case
# for i, criterion in enumerate(criteria):
#     plt.figure(figsize=(12, 8))
    
#     # Lấy dữ liệu cho tiêu chí hiện tại
#     data_pivot = df.pivot(index='Test Case', columns='Algorithm', values=criterion)
    
#     # Xác định vị trí các cột và chiều rộng cột
#     x = np.arange(len(data_pivot.index))  # vị trí của các test cases
#     width = 0.2  # chiều rộng của mỗi thanh
    
#     # Vẽ các cột cho từng thuật toán với màu sắc được chỉ định
#     plt.bar(x - 1.5 * width, data_pivot['A*'], width, label='A*', color=colors['A*'])
#     plt.bar(x - 0.5 * width, data_pivot['UCS'], width, label='UCS', color=colors['UCS'])
#     plt.bar(x + 0.5 * width, data_pivot['BFS'], width, label='BFS', color=colors['BFS'])
#     plt.bar(x + 1.5 * width, data_pivot['DFS'], width, label='DFS', color=colors['DFS'])
    
#     # Cài đặt nhãn và tiêu đề cho từng biểu đồ
#     plt.title(titles[i])
#     plt.xlabel('Test Case')
#     plt.ylabel(criterion)
#     plt.xticks(x, data_pivot.index, rotation=45)
#     plt.legend()
    
#     # Lưu biểu đồ thành file PDF
#     pdf_filename = f"{criterion.replace(' ', '_')}.pdf"
#     plt.tight_layout()
#     plt.savefig(pdf_filename, format='pdf')
    
#     # Đóng biểu đồ để giải phóng bộ nhớ
#     plt.close()

# print("Đã lưu các biểu đồ thành file PDF.")
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Hàm đọc dữ liệu từ các file và lưu vào DataFrame
def read_data_from_files(file_list):
    data = []
    for i, file_name in enumerate(file_list):
        with open(file_name, 'r') as file:
            content = file.read()
            
            # Trích xuất dữ liệu của mỗi thuật toán trong file
            algorithms = re.findall(r'(A\*|UCS|BFS|DFS)\nSteps: (\d+), Weight: (\d+), Node: (\d+), Time \(ms\): ([\d.]+), Memory \(MB\): ([\d.]+)', content)
            for algorithm, steps, weight, nodes, time, memory in algorithms:
                data.append({
                    'Test Case': f'Test {i+1}',
                    'Algorithm': algorithm,
                    'Steps': int(steps),
                    'Weight': int(weight),
                    'Nodes': int(nodes),
                    'Time (ms)': float(time),
                    'Memory (MB)': float(memory)
                })
    
    # Chuyển đổi dữ liệu thành DataFrame
    return pd.DataFrame(data)

# Lấy danh sách các file output
file_list = [f"output-{i:02}.txt" for i in range(1, 11)]  # output-01.txt đến output-10.txt
df = read_data_from_files(file_list)

# Danh sách các tiêu chí cần vẽ biểu đồ và tiêu đề của chúng
criteria = ['Time (ms)', 'Memory (MB)', 'Nodes', 'Steps', 'Weight']
titles = ['Execution Time', 'Memory Usage', 'Generated Nodes', 'Movement Steps', 'Total Push Weight']

# Định nghĩa màu sắc cho các thuật toán
colors = {
    'A*': (160/255, 35/255, 52/255),  # rgb(160, 35, 52)
    'UCS': (255/255, 173/255, 96/255),  # rgb(255, 173, 96)
    'BFS': (255/255, 238/255, 173/255),  # rgb(255, 238, 173)
    'DFS': (150/255, 206/255, 180/255)   # rgb(150, 206, 180)
}

# Vẽ biểu đồ cho mỗi test case và lưu vào các tấm PDF
for i in range(1,11):  # Lặp qua 10 test case
    plt.figure(figsize=(12, 8))
    
    # Lọc dữ liệu cho Test Case hiện tại
    data_test_case = df[df['Test Case'] == f'Test {i}']
    
    # Vẽ từng biểu đồ cho mỗi tiêu chí
    for j, criterion in enumerate(criteria):
        plt.subplot(2, 3, j+1)  # Tạo một lưới 2 hàng, 3 cột để chứa biểu đồ
        
        # Lấy dữ liệu cho tiêu chí hiện tại
        data_pivot = data_test_case.pivot(index='Algorithm', columns='Test Case', values=criterion).T
        
        # Vẽ các cột cho từng thuật toán với màu sắc đã định
        for algorithm in ['A*', 'UCS', 'BFS', 'DFS']:
            plt.bar(algorithm, data_pivot[algorithm].values[0], width=0.2, label=algorithm, color=colors[algorithm])
        
        # Cài đặt nhãn và tiêu đề cho biểu đồ
        plt.title(titles[j])
        plt.xlabel('Algorithm')
        plt.ylabel(criterion)
        plt.legend()
    
    # Lưu biểu đồ thành một tấm PDF cho mỗi test case
    pdf_filename = f"Test_{i}_comparison.pdf"
    plt.tight_layout()
    plt.savefig(pdf_filename, format='pdf')
    
    # Đóng biểu đồ để giải phóng bộ nhớ
    plt.close()

print("Đã lưu các tấm PDF cho từng test case.")
