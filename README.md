# Openwheel
Open-source some readily usable tools. At present, I don't know what to write about.

# Project1 : ThesisPolish  
## The tool can significantly enhance the polishing of master’s thesis.



## 代码提交说明  
- 代码提交到Openwheel仓库的thesispolish目录下
(The code has been submitted to the "ThesisPolish" branch of the Openwheel repository.)  
- 代码提交时,请在提交信息git commit message中按照例子进行编写
(When submitting the code, please follow the example to write the git commit message in the submission information.)
- Here is an example:ThesisPolish:Added what modules;your_name;date

# runcode  
```
# create a virtual environment
conda create -n thesispolish python=3.10
conda activate thesispolish
pip install --upgrade 'openai>=1.0'

# set model to kimi-k2-0905-preview  
set MOONSHOT_API_KEY=your_api_key
# Generate the overall outline of the thesis.  
python generate_outline.py your_pdf_path

# Based on the outline of the paper, generate localized revision text.    
# 润色完毕的文本在polish.txt文件中(The revised text is stored in the "polish.txt" file.)  
python polish.py --position 需要润色文字所在位置 --test 需要润色文本
```


## 工作日志  
### 2026-03-30  
- 完成了kimi api的调用  
- 完成了对pdf信息的提取  
- pdf输出信息在outline.txt文件中  
- 完成了对pdf输出信息的规范化,符合硕士论文要求  
- 增加论文:大纲+局部润色功能,输出在polish.txt文件中    
### further work  
- 整体架构实现了，如何增加交互模块，避免使用命令行  

