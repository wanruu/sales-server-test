#!/bin/bash

FILE_PATTERN="testcase_*.py"

for file in ./$FILE_PATTERN; do
  if [ -f "$file" ]; then
    echo "Running '$file'..."
    python3.9 "$file"
    
    # 检查上一个命令的退出状态
    if [ $? -ne 0 ]; then
      echo "Error: '$file' encountered an error."
    fi
  else
    echo "No test files found matching pattern '$FILE_PATTERN'."
  fi
done

echo "All tests have been executed."