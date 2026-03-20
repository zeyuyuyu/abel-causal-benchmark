#!/usr/bin/env python3
"""
将现有 test cases 转换为 FutureX 风格
- 添加 Level (L1-L4)
- 转换为多项选择题 (Options A, B, C...)
- 保持 CAP 兼容性
"""

import json
import sys
from pathlib import Path


def convert_to_futurex_style(case):
    """转换单个 case 为 FutureX 风格"""
    
    # 1. 确定 Level
    level = determine_level(case)
    
    # 2. 转换问题为多项选择题
    question_data = convert_to_multiple_choice(case)
    
    # 3. 构建 FutureX 风格结构
    futurex_case = {
        "case_id": case.get('case_id', 'unknown'),
        "level": level,
        "category": case.get('multidimensional_classification', {}).get('dimensions', {}).get('domain', {}).get('value', 'finance'),
        
        # FutureX 风格问题
        "question": question_data['question'],
        "options": question_data['options'],
        
        # 上下文
        "context": case.get('context', ''),
        "background": generate_background(case),
        
        # CAP 请求（内部使用）
        "cap_request": case.get('cap_request', {}),
        
        # 解析标准
        "resolution_criteria": {
            "type": question_data['resolution_type'],
            "metric": question_data['metric'],
            "measurement": {
                "start_time": "prediction_time",
                "end_time": f"prediction_time + {question_data.get('horizon', '24h')}"
            },
            "thresholds": {opt['id']: opt.get('threshold_desc', 'TBD') for opt in question_data['options']}
        },
        
        # 答案验证
        "ground_truth": {
            "source": case.get('ground_truth', {}).get('source', 'yahoo_finance'),
            "verification_method": case.get('ground_truth', {}).get('method', 'api_fetch'),
            "ticker": extract_ticker(case),
            "resolution_time": case.get('ground_truth', {}).get('delay_hours', 24),
            "metric": "exact_match"
        },
        
        # 评分
        "scoring": {
            "method": "exact_match",
            "points": case.get('cevs_weight', 1.0),
            "bonus_for_confidence": True,
            "partial_credit": False
        },
        
        # 元数据
        "metadata": {
            "original_category": case.get('category'),
            "cap_primitive": case.get('cap_primitive'),
            "complexity": level,
            "cap_ability": case.get('multidimensional_classification', {}).get('dimensions', {}).get('cap_ability', {}).get('value', 'unknown')
        }
    }
    
    return futurex_case


def determine_level(case):
    """确定 Level (L1-L4)"""
    # 基于多种因素判断
    cap_primitive = case.get('cap_primitive', '')
    complexity = case.get('multidimensional_classification', {}).get('dimensions', {}).get('complexity', 'L?')
    
    # 如果有明确的 complexity，使用它
    if complexity in ['L1', 'L2', 'L3', 'L4']:
        return complexity
    
    # 根据 cap_primitive 判断
    if cap_primitive == 'predict':
        return 'L1'  # 简单预测
    elif cap_primitive == 'intervene':
        return 'L2'  # 干预分析
    elif cap_primitive == 'path':
        return 'L3'  # 路径分析
    elif cap_primitive == 'attest':
        return 'L4'  # 复杂比较
    else:
        return 'L2'  # 默认中等


def convert_to_multiple_choice(case):
    """转换为多项选择题"""
    question = case.get('question', '')
    cap_primitive = case.get('cap_primitive', '')
    
    # 提取时间范围
    horizon = extract_horizon(case.get('context', ''))
    
    if cap_primitive == 'predict':
        # 预测类问题 - 转换为 Yes/No 或 Up/Down
        ticker = extract_ticker(case)
        
        # 判断是方向预测还是幅度预测
        if 'go up' in question.lower() or 'rise' in question.lower() or 'increase' in question.lower():
            return {
                'question': f"Will {ticker} close price increase in the next {horizon}?",
                'options': [
                    {'id': 'A', 'text': f'Yes (Increase)', 'threshold': 0.0, 'threshold_desc': '> 0%'},
                    {'id': 'B', 'text': f'No (Decrease or Unchanged)', 'threshold': 0.0, 'threshold_desc': '≤ 0%'}
                ],
                'resolution_type': 'threshold',
                'metric': 'price_direction',
                'horizon': horizon
            }
        else:
            # 幅度预测
            return {
                'question': f"What will be the price movement of {ticker} in the next {horizon}?",
                'options': [
                    {'id': 'A', 'text': 'Increase > 3%', 'threshold': 0.03, 'threshold_desc': '> 3%'},
                    {'id': 'B', 'text': 'Increase 0-3%', 'threshold': 0.0, 'threshold_desc': '0% to 3%'},
                    {'id': 'C', 'text': 'Decrease < 0%', 'threshold': 0.0, 'threshold_desc': '< 0%'}
                ],
                'resolution_type': 'threshold',
                'metric': 'percentage_change',
                'horizon': horizon
            }
    
    elif cap_primitive == 'intervene':
        # 干预类问题
        return {
            'question': f"If the specified intervention occurs, what will be the primary effect?",
            'options': [
                {'id': 'A', 'text': 'Strong positive effect (>5%)', 'threshold': 0.05},
                {'id': 'B', 'text': 'Moderate positive effect (0-5%)', 'threshold': 0.0},
                {'id': 'C', 'text': 'No significant effect', 'threshold': 0.0},
                {'id': 'D', 'text': 'Negative effect', 'threshold': 0.0}
            ],
            'resolution_type': 'simulation',
            'metric': 'causal_effect',
            'horizon': '24h'
        }
    
    elif cap_primitive == 'path':
        # 路径类问题
        return {
            'question': f"Is there a direct causal path between the specified nodes?",
            'options': [
                {'id': 'A', 'text': 'Yes, direct path exists (1-2 hops)'},
                {'id': 'B', 'text': 'Yes, indirect path (3+ hops)'},
                {'id': 'C', 'text': 'No path exists'}
            ],
            'resolution_type': 'existence',
            'metric': 'path_existence',
            'horizon': 'immediate'
        }
    
    else:
        # 默认转换
        return {
            'question': question,
            'options': [
                {'id': 'A', 'text': 'Outcome A'},
                {'id': 'B', 'text': 'Outcome B'}
            ],
            'resolution_type': 'manual',
            'metric': 'expert_evaluation',
            'horizon': '24h'
        }


def extract_ticker(case):
    """提取股票代码"""
    target = case.get('cap_request', {}).get('params', {}).get('target_node', '')
    if target:
        return target.replace('_close', '').replace('_rate', '')
    
    # 从问题中提取
    question = case.get('question', '')
    import re
    tickers = re.findall(r'\b([A-Z]{2,8}USD?)\b', question)
    if tickers:
        return tickers[0]
    
    return 'UNKNOWN'


def extract_horizon(context):
    """提取时间范围"""
    context_lower = context.lower()
    
    if '5 hours' in context_lower or '4-hour' in context_lower or '6 hours' in context_lower:
        return '6 hours'
    elif '12-hour' in context_lower or 'tomorrow' in context_lower:
        return '24 hours'
    elif '3-day' in context_lower or '48 hours' in context_lower:
        return '72 hours'
    elif 'week' in context_lower:
        return '1 week'
    else:
        return '24 hours'


def generate_background(case):
    """生成背景信息"""
    context = case.get('context', '')
    domain = case.get('multidimensional_classification', {}).get('dimensions', {}).get('domain', {}).get('value', '')
    
    backgrounds = {
        'finance': 'Financial market analysis using causal graph relationships between assets.',
        'political': 'Political event prediction based on historical patterns and current indicators.',
        'sports': 'Sports outcome prediction using performance metrics and historical data.',
        'tech': 'Technology trend analysis based on market indicators and innovation cycles.',
        'entertainment': 'Entertainment industry prediction based on market trends and consumer behavior.',
        'science': 'Scientific outcome prediction based on empirical data and statistical models.'
    }
    
    return backgrounds.get(domain, context)


def main():
    print("=" * 70)
    print("Converting Test Cases to FutureX Style")
    print("=" * 70)
    print()
    
    # 加载现有 cases
    input_dir = Path('test_cases')
    output_dir = Path('test_cases_futurex_style')
    output_dir.mkdir(exist_ok=True)
    
    # 找到所有 JSON 文件
    case_files = [f for f in input_dir.glob('*.json') if not f.name.startswith('_')]
    
    print(f"📂 Found {len(case_files)} test cases")
    print()
    
    # 转换每个 case
    converted = []
    level_stats = {'L1': 0, 'L2': 0, 'L3': 0, 'L4': 0}
    
    for case_file in case_files:
        case = json.load(open(case_file))
        
        # 转换
        futurex_case = convert_to_futurex_style(case)
        converted.append(futurex_case)
        
        # 统计 level
        level = futurex_case['level']
        level_stats[level] = level_stats.get(level, 0) + 1
        
        # 保存
        output_path = output_dir / case_file.name
        with open(output_path, 'w') as f:
            json.dump(futurex_case, f, indent=2, ensure_ascii=False)
    
    print("✅ Conversion complete!")
    print()
    print("📊 Level Distribution:")
    for level, count in sorted(level_stats.items()):
        print(f"  {level}: {count}")
    print()
    
    # 创建索引
    index = {
        'total_cases': len(converted),
        'export_date': '2026-03-20',
        'style': 'FutureX',
        'format_version': '1.0',
        'cases': [
            {
                'id': c['case_id'],
                'level': c['level'],
                'category': c['category'],
                'question_preview': c['question'][:50] + '...',
                'options_count': len(c['options'])
            }
            for c in converted[:20]  # 前20个
        ]
    }
    
    with open(output_dir / '_index.json', 'w') as f:
        json.dump(index, f, indent=2)
    
    # 创建示例文件
    example = converted[0] if converted else None
    if example:
        with open(output_dir / '_EXAMPLE.json', 'w') as f:
            json.dump(example, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to: {output_dir}/")
    print(f"  - {len(converted)} individual case files")
    print(f"  - _index.json (index)")
    print(f"  - _EXAMPLE.json (example)")


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
