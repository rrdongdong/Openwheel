# Openwheel
Open-source some readily usable tools. At present, I don't know what to write about.

# Project1 : ThesisPolish  
## The tool can significantly enhance the polishing of master’s thesis.



## 代码提交说明  
- 代码提交到Openwheel仓库的thesispolish目录下  
- 代码提交时,请在提交信息commit message中举例(ThesisPolish:增加了什么功能;your_name;date)  

# runcode  
```
# create a virtual environment
conda create -n thesispolish python=3.10
conda activate thesispolish
pip install --upgrade 'openai>=1.0'

# set model to kimi-k2-0905-preview  
set MOONSHOT_API_KEY=your_api_key
python generate_outline.py your_pdf_path
```


## 工作日志  
### 2026-03-30  
- 完成了kimi api的调用  
- 完成了对pdf信息的提取  
- pdf输出信息在outline.txt文件中    
### further work  
- 需要对pdf输出信息的规范化,符合硕士论文要求  
- 需要增加论文:大纲+局部润色功能  