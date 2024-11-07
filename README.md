# Sokoban Solver AI
## Giới thiệu
Đây là một trò chơi Sokoban với chức năng giải tự động sử dụng các thuật toán AI, bao gồm *BFS* (Breadth-First Search), DFS (Depth-First Search), *A\** (A-star) và *UCS* (Uniform Cost Search). Trò chơi Sokoban yêu cầu người chơi di chuyển các thùng vào các vị trí chỉ định trên bản đồ, và mục tiêu là giải quyết mọi bài toán Sokoban một cách tối ưu. AI trong dự án này sử dụng bốn thuật toán tìm kiếm khác nhau để tìm ra cách di chuyển các thùng tự động.
# Cài đặt
Để cài đặt và chạy dự án này, bạn có thể làm theo các bước dưới đây.

## Bước 1: Cài đặt môi trường
Trước tiên, bạn cần tạo một môi trường ảo với *Anaconda* và cài đặt các thư viện cần thiết.

1. Tạo môi trường ảo và cài đặt Python 3.10:
```bash
conda create -n myenv python=3.10
```
2. Kích hoạt môi trường ảo:
```bash
source ~/.bashrc
conda activate myenv
```
## Bước 2: Cài đặt các thư viện cần thiết
Cài đặt các thư viện cần thiết cho dự án, bao gồm:

- pygame: Thư viện để tạo giao diện người dùng đồ họa (GUI) cho trò chơi.
- pillow: Thư viện để xử lý hình ảnh, nếu có nhu cầu.
- psutil: Thư viện để theo dõi hiệu suất hệ thống, nếu cần.
- Chạy các lệnh sau đây để cài đặt:
```bash
pip install -r requirements.txt
```

### Demo
<img src="https://github.com/NP10t/Sokoban-Solver-AI/blob/40d99a28a4da8bf8cc25541b203ef3a621107835/demo_images/map_10.png" alt="image alt" width="700"/>