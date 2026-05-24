import tkinter as tk
from tkinter import messagebox
import itertools

# ==================== 24点求解核心（与之前一致） ====================
class ExprNode:
    def __init__(self, op=None, value=None, children=None):
        self.op = op
        self.value = value
        self.children = children if children else []

    def is_leaf(self):
        return self.op is None

    def get_numbers(self):
        if self.is_leaf():
            return [int(self.value)]
        nums = []
        for ch in self.children:
            nums.extend(ch.get_numbers())
        return sorted(nums)

def full_normalize(node):
    if node.is_leaf():
        return node
    children = [full_normalize(ch) for ch in node.children]
    op = node.op

    if op in ('+', '*'):
        flat = []
        for ch in children:
            if ch.op == op:
                flat.extend(ch.children)
            else:
                flat.append(ch)
        flat.sort(key=lambda n: n.get_numbers())
        if op == '+':
            val = sum(ch.value for ch in flat)
        else:
            val = 1.0
            for ch in flat:
                val *= ch.value
        return ExprNode(op, val, flat)

    elif op == '-':
        left, right = children[0], children[1]
        if left.op == '-':
            a, b = left.children[0], left.children[1]
            c = right
            sum_bc = full_normalize(ExprNode('+', b.value + c.value, [b, c]))
            return full_normalize(ExprNode('-', a.value - sum_bc.value, [a, sum_bc]))
        if right.op == '-':
            a, b, c = left, right.children[0], right.children[1]
            sum_ac = full_normalize(ExprNode('+', a.value + c.value, [a, c]))
            return full_normalize(ExprNode('-', sum_ac.value - b.value, [sum_ac, b]))
        return ExprNode('-', left.value - right.value, [left, right])

    elif op == '/':
        left, right = children[0], children[1]
        if left.op == '/':
            a, b = left.children[0], left.children[1]
            c = right
            prod_bc = full_normalize(ExprNode('*', b.value * c.value, [b, c]))
            if abs(prod_bc.value) > 1e-10:
                return full_normalize(ExprNode('/', a.value / prod_bc.value, [a, prod_bc]))
        if right.op == '/':
            a, b, c = left, right.children[0], right.children[1]
            prod_ac = full_normalize(ExprNode('*', a.value * c.value, [a, c]))
            if abs(b.value) > 1e-10:
                return full_normalize(ExprNode('/', prod_ac.value / b.value, [prod_ac, b]))
        if abs(right.value) > 1e-10:
            return ExprNode('/', left.value / right.value, [left, right])
        else:
            return node

def node_to_string(node):
    if node.is_leaf():
        return str(int(node.value))
    if node.op in ('+', '*') and len(node.children) > 2:
        s = node_to_string(node.children[0])
        for ch in node.children[1:]:
            s = f"({s}{node.op}{node_to_string(ch)})"
        return s
    else:
        left_str = node_to_string(node.children[0])
        right_str = node_to_string(node.children[1])
        return f"({left_str}{node.op}{right_str})"

def find_all_solutions(nums):
    solutions = set()

    def search(items):
        if len(items) == 1:
            node = items[0]
            if abs(node.value - 24) < 1e-6:
                solutions.add(node_to_string(node))
            return

        n = len(items)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                rest = [items[k] for k in range(n) if k != i and k != j]
                a, b = items[i], items[j]

                new_node = full_normalize(ExprNode('+', a.value + b.value, [a, b]))
                search(rest + [new_node])
                new_node = full_normalize(ExprNode('*', a.value * b.value, [a, b]))
                search(rest + [new_node])
                new_node = full_normalize(ExprNode('-', a.value - b.value, [a, b]))
                search(rest + [new_node])
                new_node = full_normalize(ExprNode('-', b.value - a.value, [b, a]))
                search(rest + [new_node])
                if abs(b.value) > 1e-10:
                    new_node = full_normalize(ExprNode('/', a.value / b.value, [a, b]))
                    search(rest + [new_node])
                if abs(a.value) > 1e-10:
                    new_node = full_normalize(ExprNode('/', b.value / a.value, [b, a]))
                    search(rest + [new_node])

    for perm in itertools.permutations(nums):
        items = [ExprNode(value=float(x)) for x in perm]
        search(items)

    return sorted(solutions)

# ==================== GUI 部分（修正后） ====================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("24点求解器")
        self.root.resizable(False, False)

        # 输入区域
        input_frame = tk.Frame(root)
        input_frame.pack(padx=10, pady=10)

        tk.Label(input_frame, text="输入四个1~9的数字：").grid(row=0, column=0, columnspan=4, pady=(0,5))

        self.entries = []
        for i in range(4):
            entry = tk.Entry(input_frame, width=5, font=('Arial', 14), justify='center')
            entry.grid(row=1, column=i, padx=5)
            self.entries.append(entry)

        # 按钮区域
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="求解", command=self.solve, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="清空", command=self.clear, width=10).pack(side=tk.LEFT, padx=5)

        # 结果显示区域
        result_frame = tk.Frame(root)
        result_frame.pack(padx=10, pady=(0,10))  # 正确使用在 pack 中

        tk.Label(result_frame, text="求解结果：").pack(anchor='w')
        self.result_text = tk.Text(result_frame, width=50, height=15, font=('Consolas', 10), state='disabled')
        self.result_text.pack()

        # 状态栏
        self.status = tk.Label(root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def solve(self):
        nums = []
        for i, entry in enumerate(self.entries):
            val = entry.get().strip()
            if not val:
                messagebox.showwarning("输入错误", f"第{i+1}个数字不能为空")
                return
            try:
                num = int(val)
            except ValueError:
                messagebox.showwarning("输入错误", f"“{val}”不是有效整数")
                return
            if num < 1 or num > 9:
                messagebox.showwarning("输入错误", f"数字{num}不在1~9范围内")
                return
            nums.append(num)

        self.status.config(text="正在计算...")
        self.root.update_idletasks()
        solutions = find_all_solutions(nums)
        self.show_results(solutions, nums)

    def show_results(self, solutions, nums):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        if not solutions:
            self.result_text.insert(tk.END, f"数字 {nums} 无法计算出24。")
        else:
            self.result_text.insert(tk.END, f"数字 {nums} 共有 {len(solutions)} 个解：\n\n")
            for s in solutions:
                self.result_text.insert(tk.END, f"{s} = 24\n")
        self.result_text.config(state='disabled')
        self.status.config(text=f"完成，共 {len(solutions)} 个解")

    def clear(self):
        for entry in self.entries:
            entry.delete(0, tk.END)
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state='disabled')
        self.status.config(text="就绪")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()