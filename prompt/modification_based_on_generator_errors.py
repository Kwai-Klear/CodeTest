import json

prompt = """**You are an ACM competition problem test data construction expert. Your task is to debug a pipeline that generates test cases for competition-level code, analyze the problem, and return the corrected result.**

### Test Case Generation Pipeline
1.  **Request** an LLM to obtain a `generator' specifically designed to generate test case inputs. **Execute** this `generator' to obtain several inputs.
2.  **Execute** multiple human-expert-written `solutions' (which have already passed official tests) using the input generated by the `generator'. If they **produce consistent output**, then consider that input **valid**.
3.  If the input is **valid**, pair it with the output to form a **unit test**.

### Task Description
Your task is to analyze error types within the pipeline and provide a corrected `generator` based on the error information.

### Error Types
1.  **Formatting Error:** The `generator' output **must** be in the format: `list[str]', where each string represents an independent test case.
2.  **Generator Code Execution Error:** The `generator' code has issues and cannot run successfully.
3.  **Other Error Types**

### Competition Problem, Generator Code \& Error Information
-   **[Competition Problem]:** {problem}
-   **[Generator]:** {generator}
-   **[Error Information]:** {error_info}

### Analyze Errors \& Provide Corrections
1.  Based on the above information, **analyze the error type** in the generator. **What caused it?**
2.  Based on the error information, **modify the generator code**. The output of the modified generator code **must** be a list (`list'), where the elements are test cases (strings).
3.  Below are two **examples** of generators:
-     {example1}
-     {example2}

Please modify the generator code according to the above requirements and provide the corrected generator code.
"""


example1 = """
```python
def generate_test_inputs(num_cases=100):
    # 参数生成器定义（示例）
    random.seed(42)  # 固定随机种子确保结果可复现
    param_generators = {{
        'n': [1, 1000] + [random.randint(2, 999) for _ in range(20)],
        'matrix': [gen_matrix(size) for size in (2, 5, 10)]
    }}
    
    # 正交组合引擎
    cases = []
    while len(cases) < num_cases:
        # 动态选择生成策略
        strategy = weighted_choice([
            ('boundary', 0.1), 
            ('random', 0.7),
            ('invalid', 0.2)
        ])
        
        # 执行策略对应的生成逻辑
        if strategy == 'boundary':
            case = (choice(param_generators['n']), 
                generate_boundary_array())
        elif ...:
            ...

        # 约束校验
        if is_valid_case(case):
            cases.append(case)
    return cases[:num_cases]
def main():
    # Generate test cases
    test_cases = generate_test_inputs()
    test_case_list = []
    # Print or process the test cases as needed
    for case in test_cases:
        test_case_list.append(case)
    print(test_case_list)

if __name__ == "__main__":
    main()
```
"""

example2 = """
```python
import random
def generate_single_testcase():
    strategies = ['all_ones', 'all_zeros', 'half', 'no_valid', 'random_yes', 'random_no']
    strategy = random.choice(strategies)
    
    # 生成L的值
    if random.random() < 0.05:   #接近边界的概率需要设置较低的值
        L = random.randint(90000, 100000)
    else:
        L = random.choice([1, 2, 3, 4, 5, 10, 100, 1000, 5000, 10000])

    # 生成S的逻辑
    if strategy == 'all_ones':
        S = '1' * L
    elif strategy == 'all_zeros':
        S = '0' * L
    elif strategy == 'half':
        m = (L + 1) // 2
        S = '1' * m + '0' * (L - m)
    elif strategy == 'no_valid':
        s = []
        current_ones = 0
        for i in range(1, L + 1):
            max_allowed = (i - 1) // 2
            if current_ones + 1 <= max_allowed:
                s.append('1')
                current_ones += 1
            else:
                s.append('0')
        S = ''.join(s)
    elif strategy == 'random_yes':
        k = random.randint(1, L)
        required = (k + 1) // 2
        prefix = ['1'] * required + ['0'] * (k - required)
        random.shuffle(prefix)
        suffix = [random.choice(['0', '1']) for _ in range(L - k)]
        S = ''.join(prefix + suffix)
    elif strategy == 'random_no':
        s = []
        current_ones = 0
        for i in range(1, L + 1):
            max_allowed = (i - 1) // 2
            if current_ones + 1 <= max_allowed:
                s.append('1')
                current_ones += 1
            else:
                s.append('0')
        S = ''.join(s)
    else:
        S = ''.join(random.choices(['0', '1'], k=L))
    return (L, S)
def generate_test_inputs(num_cases=100):
    random.seed(42)
    test_case_list = []
    
    for _ in range(num_cases):
        # 生成完整的测试输入字符串
        T = random.randint(1, 10)  # 每个测试输入包含1~10个测试用例
        sum_L = 0
        test_input = []
        for _ in range(T):
            remaining = 10**6 - sum_L
            if remaining <= 0:
                break
            # 动态调整L的生成范围
            max_possible_L = min(100000, remaining)
            L = random.randint(1, max_possible_L) if remaining > 100000 else remaining
            
            # 生成单个测试用例
            _, S = generate_single_testcase()
            L = min(L, 100000)  # 确保L不超过题目限制
            test_input.append(f"{{L}}\n{{S}}")
            sum_L += L
        # 构造完整的输入字符串
        T_actual = len(test_input)
        full_input = f"{{T_actual}}\n" + "\n".join(test_input)
        test_case_list.append(full_input)
    return test_case_list[:num_cases]
def main():
    test_cases = generate_test_inputs()
    print(test_cases)
if __name__ == "__main__":
    main()
```
"""


path = ''
path_save = ''

with open(path, 'r') as file, open(path_save, 'w') as save_file:
    for i, line in enumerate(file):
        print(i)
        data = json.loads(line.strip())
        problem = data['question']
        generator = data['input_generator']
        try:
            error_info = data['error_info'][:5000]
        except:
            continue
        # error_info = ""
        ques = prompt.format_map({
            "problem": problem,
            "generator": generator,
            "error_info": error_info,
            "example1": example1,
            "example2": example2
        })

        for j in range(4):
            new_dic = {"custom_id": f"{data['custom_id']}-{j}", "body": {"messages": [{"role": "user", "content": ques}], "max_tokens": 8192, "temperature": 0.7}}
            save_file.write(json.dumps(new_dic, ensure_ascii=False)+'\n')

        
        # new_dic = {"custom_id": f"{data['custom_id']}", "body": {"messages": [{"role": "user", "content": ques}], "max_tokens": 8192, "temperature": 0.7}}