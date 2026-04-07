from pathlib import Path
import locale
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox


class ThesisGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("论文大纲提取与段落润色")
        self.base_dir = Path(__file__).resolve().parent

        self.api_key_var = tk.StringVar()
        self.pdf_path_var = tk.StringVar(value=str(self.base_dir / "test2.pdf"))
        self.outline_path_var = tk.StringVar(value=str(self.base_dir / "outline.txt"))
        self.output_path_var = tk.StringVar(value=str(self.base_dir / "polished.txt"))
        self.position_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        tk.Label(self.root, text="kimi_API密钥").grid(row=0, column=0, sticky="w", **pad)
        tk.Entry(self.root, textvariable=self.api_key_var, show="*", width=70).grid(row=0, column=1, columnspan=3, sticky="we", **pad)

        tk.Label(self.root, text="PDF路径").grid(row=1, column=0, sticky="w", **pad)
        tk.Entry(self.root, textvariable=self.pdf_path_var, width=70).grid(row=1, column=1, columnspan=2, sticky="we", **pad)
        tk.Button(self.root, text="选择PDF", command=self.pick_pdf).grid(row=1, column=3, sticky="we", **pad)

        tk.Button(self.root, text="提取论文大纲", command=self.run_outline).grid(row=2, column=0, columnspan=4, sticky="we", **pad)

        tk.Label(self.root, text="大纲文件").grid(row=3, column=0, sticky="w", **pad)
        tk.Entry(self.root, textvariable=self.outline_path_var, width=70).grid(row=3, column=1, columnspan=3, sticky="we", **pad)

        tk.Button(self.root, text="加载大纲", command=self.load_outline_to_editor).grid(row=4, column=0, columnspan=2, sticky="we", **pad)
        tk.Button(self.root, text="保存大纲", command=self.save_outline_from_editor).grid(row=4, column=2, columnspan=2, sticky="we", **pad)

        tk.Label(self.root, text="大纲可视化（可编辑）").grid(row=5, column=0, sticky="nw", **pad)
        self.outline_text = tk.Text(self.root, height=10, width=90)
        self.outline_text.grid(row=5, column=1, columnspan=3, sticky="we", **pad)

        tk.Label(self.root, text="润色位置").grid(row=6, column=0, sticky="w", **pad)
        tk.Entry(self.root, textvariable=self.position_var, width=70).grid(row=6, column=1, columnspan=3, sticky="we", **pad)

        tk.Label(self.root, text="待润色文字").grid(row=7, column=0, sticky="nw", **pad)
        self.input_text = tk.Text(self.root, height=10, width=90)
        self.input_text.grid(row=7, column=1, columnspan=3, sticky="we", **pad)

        tk.Button(self.root, text="开始润色", command=self.run_polish).grid(row=8, column=0, columnspan=4, sticky="we", **pad)

        tk.Label(self.root, text="润色后输出").grid(row=9, column=0, sticky="nw", **pad)
        self.output_text = tk.Text(self.root, height=10, width=90)
        self.output_text.grid(row=9, column=1, columnspan=3, sticky="we", **pad)

        tk.Label(self.root, text="状态").grid(row=10, column=0, sticky="nw", **pad)
        self.status_text = tk.Text(self.root, height=6, width=90)
        self.status_text.grid(row=10, column=1, columnspan=3, sticky="we", **pad)

        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=1)

    def pick_pdf(self):
        path = filedialog.askopenfilename(
            title="选择论文PDF",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if path:
            self.pdf_path_var.set(path)

    def append_status(self, text: str):
        self.status_text.insert("end", text + "\n")
        self.status_text.see("end")

    def load_outline_to_editor(self):
        path = Path(self.outline_path_var.get().strip())
        if not path.exists():
            messagebox.showwarning("文件不存在", f"未找到大纲文件: {path}")
            return
        content = path.read_text(encoding="utf-8")
        self.outline_text.delete("1.0", "end")
        self.outline_text.insert("1.0", content)
        self.append_status(f"已加载大纲: {path}")

    def save_outline_from_editor(self):
        path = Path(self.outline_path_var.get().strip())
        content = self.outline_text.get("1.0", "end").strip()
        path.write_text(content + ("\n" if content else ""), encoding="utf-8")
        self.append_status(f"已保存大纲: {path}")

    def _run_subprocess(self, cmd: list[str], on_success=None):
        env = os.environ.copy()
        env["MOONSHOT_API_KEY"] = self.api_key_var.get().strip()
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                encoding=locale.getpreferredencoding(False),
                errors="replace",
                env=env
            )
            stdout = (result.stdout or "").strip()
            stderr = (result.stderr or "").strip()
            if stdout:
                self.root.after(0, lambda: self.append_status(stdout))
            if stderr:
                self.root.after(0, lambda: self.append_status(stderr))
            if result.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror("执行失败", f"命令执行失败，退出码: {result.returncode}"))
                return
            if on_success:
                self.root.after(0, on_success)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("异常", str(e)))

    def run_outline(self):
        api_key = self.api_key_var.get().strip()
        pdf_path = self.pdf_path_var.get().strip()
        if not api_key:
            messagebox.showwarning("缺少参数", "请先输入API密钥")
            return
        if not pdf_path:
            messagebox.showwarning("缺少参数", "请先输入PDF路径")
            return

        script = self.base_dir / "generate_outline.py"
        if not script.exists():
            messagebox.showerror("文件缺失", f"未找到脚本: {script}")
            return

        self.append_status("开始提取大纲...")
        cmd = [sys.executable, str(script), pdf_path]

        def on_success():
            self.append_status("大纲提取完成")
            self.load_outline_to_editor()

        threading.Thread(target=self._run_subprocess, args=(cmd, on_success), daemon=True).start()

    def run_polish(self):
        api_key = self.api_key_var.get().strip()
        position = self.position_var.get().strip()
        text = self.input_text.get("1.0", "end").strip()
        if not api_key:
            messagebox.showwarning("缺少参数", "请先输入API密钥")
            return
        if not position:
            messagebox.showwarning("缺少参数", "请先输入润色位置")
            return
        if not text:
            messagebox.showwarning("缺少参数", "请先输入待润色文字")
            return

        script = self.base_dir / "polish.py"
        if not script.exists():
            messagebox.showerror("文件缺失", f"未找到脚本: {script}")
            return

        outline_path = self.outline_path_var.get().strip()
        output_path = self.output_path_var.get().strip()
        self.save_outline_from_editor()
        self.append_status("开始润色...")
        cmd = [
            sys.executable,
            str(script),
            "--outline",
            outline_path,
            "--position",
            position,
            "--text",
            text,
            "--output",
            output_path,
        ]

        def on_success():
            out_file = Path(output_path)
            if out_file.exists():
                content = out_file.read_text(encoding="utf-8")
                self.output_text.delete("1.0", "end")
                self.output_text.insert("1.0", content)
            self.append_status("润色完成")

        threading.Thread(target=self._run_subprocess, args=(cmd, on_success), daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ThesisGUI(root)
    root.mainloop()