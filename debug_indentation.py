import re

def debug_indentation(file_path, problem_line_number, context=5):
    """检查文件中的缩进问题并打印出相关上下文"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # 确定要显示的行范围
        start_line = max(0, problem_line_number - context - 1)
        end_line = min(len(lines), problem_line_number + context)
        
        print(f"检查文件 {file_path} 中第 {problem_line_number} 行附近的缩进问题\n")
        
        # 打印有行号和缩进级别的上下文
        for i in range(start_line, end_line):
            line = lines[i].rstrip('\n')
            leading_spaces = len(line) - len(line.lstrip())
            indent_level = leading_spaces // 4
            
            # 高亮显示问题行
            line_marker = " >" if i + 1 == problem_line_number else "  "
            
            print(f"{i+1:4d}{line_marker} {'|' * indent_level} {line}")
            
            # 检查特定问题
            if i + 1 == problem_line_number:
                if "else:" in line:
                    prev_line_indent = len(lines[i-1].rstrip('\n')) - len(lines[i-1].lstrip())
                    if leading_spaces != prev_line_indent:
                        print(f"    ! 潜在问题: 'else:' 缩进与上方代码块不匹配")
                        print(f"      当前缩进: {leading_spaces} 空格")
                        print(f"      预期缩进: {prev_line_indent} 空格")
                
        return True
    except Exception as e:
        print(f"调试过程中出错: {e}")
        return False

if __name__ == "__main__":
    file_path = "spotify_playlist_importer/utils/enhanced_matcher.py"
    problem_line = 224  # 根据错误信息调整
    debug_indentation(file_path, problem_line) 