#!/usr/bin/env python3
"""
下载所有 HuggingFace Benchmark 数据并导出为单独文件

使用方法:
    python download_benchmarks.py

数据来源:
    - YuehHanChen/forecasting: 5,516 cases (二元预测)
    - Duruo/forecastbench-single_question: 902 cases (预测市场)
    - robinfaro/TSQA: 10,063 cases (时间敏感QA)
    - TimelyEventsBenchmark/TiEBe: 23,446+ cases (多时区事件)

注意: 需要安装 huggingface-hub
    pip install huggingface-hub
"""

from huggingface_hub import hf_hub_download, list_repo_files
import json
import os
import glob
from collections import OrderedDict


def download_and_export_forecasting():
    """下载并导出 forecasting_5516"""
    print("=== 1. 下载 YuehHanChen/forecasting ===")
    repo_id = "YuehHanChen/forecasting"
    output_dir = "forecasting_cases_5516"
    os.makedirs(output_dir, exist_ok=True)
    
    # 下载数据
    for filename in ['train.json', 'test.json', 'validation.json']:
        try:
            hf_hub_download(repo_id=repo_id, filename=filename, 
                          repo_type='dataset', local_dir='.cache')
            print(f"  ✅ {filename}")
        except Exception as e:
            print(f"  ❌ {filename}: {e}")
    
    # 导出
    print(f"  导出到 {output_dir}/ ...")
    counter = 0
    index_list = []
    
    for split in ['train', 'validation', 'test']:
        filepath = f'.cache/{split}.json'
        if not os.path.exists(filepath):
            continue
            
        with open(filepath) as f:
            data = json.load(f)
        
        for item in data:
            counter += 1
            file_id = f"FC_{counter:05d}"
            
            case = OrderedDict()
            case['file_id'] = file_id
            case['split'] = split
            case['question'] = item.get('question', '')
            case['background'] = item.get('background', '')
            case['resolution_criteria'] = item.get('resolution_criteria', '')
            case['ground_truth'] = item.get('resolution')  # 0.0 或 1.0
            case['is_resolved'] = item.get('is_resolved')
            case['data_source'] = item.get('data_source', '')
            case['question_type'] = item.get('question_type', '')
            case['date_begin'] = item.get('date_begin', '')
            case['date_close'] = item.get('date_close', '')
            case['date_resolve_at'] = item.get('date_resolve_at', '')
            case['url'] = item.get('url', '')
            case['gpt_3p5_category'] = item.get('gpt_3p5_category', '')
            
            with open(os.path.join(output_dir, f"{file_id}.json"), 'w') as f:
                json.dump(case, f, indent=2, ensure_ascii=False)
            
            index_list.append({
                'file_id': file_id,
                'split': split,
                'question': item.get('question', '')[:60],
                'ground_truth': item.get('resolution'),
                'data_source': item.get('data_source', '')
            })
    
    # 保存索引
    with open(os.path.join(output_dir, '_index.json'), 'w') as f:
        json.dump({
            'metadata': {
                'source': 'YuehHanChen/forecasting',
                'total_cases': counter,
                'splits': {'train': 3762, 'validation': 840, 'test': 914}
            },
            'cases': index_list
        }, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ 完成: {counter} cases")
    return counter


def download_and_export_forecastbench():
    """下载并导出 forecastbench_902"""
    print("\n=== 2. 下载 Duruo/forecastbench-single_question ===")
    repo_id = "Duruo/forecastbench-single_question"
    output_dir = "forecastbench_cases_902"
    os.makedirs(output_dir, exist_ok=True)
    
    # 下载
    for filename in ['forecastbench_single_questions_2024-12-08.jsonl',
                     'forecastbench_single_questions_human_2024-07-21.jsonl']:
        try:
            hf_hub_download(repo_id=repo_id, filename=filename,
                          repo_type='dataset', local_dir='.cache')
            print(f"  ✅ {filename}")
        except Exception as e:
            print(f"  ❌ {filename}: {e}")
    
    # 导出
    print(f"  导出到 {output_dir}/ ...")
    counter = 0
    index_list = []
    
    for filename in ['forecastbench_single_questions_2024-12-08.jsonl',
                     'forecastbench_single_questions_human_2024-07-21.jsonl']:
        filepath = f'.cache/{filename}'
        if not os.path.exists(filepath):
            continue
        
        with open(filepath) as f:
            for line in f:
                item = json.loads(line.strip())
                counter += 1
                file_id = f"FB_{counter:04d}"
                
                case = OrderedDict()
                case['file_id'] = file_id
                case['question'] = item.get('question', '')
                case['background'] = item.get('background', '')
                case['ground_truth'] = item.get('answer')  # 0 或 1
                case['source'] = item.get('source', '')
                
                if 'human_super_forecast' in item:
                    case['human_super_forecast'] = item.get('human_super_forecast')
                if 'human_public_forecast' in item:
                    case['human_public_forecast'] = item.get('human_public_forecast')
                
                with open(os.path.join(output_dir, f"{file_id}.json"), 'w') as f:
                    json.dump(case, f, indent=2, ensure_ascii=False)
                
                index_list.append({
                    'file_id': file_id,
                    'question': item.get('question', '')[:60],
                    'ground_truth': item.get('answer'),
                    'source': item.get('source', '')
                })
    
    # 保存索引
    with open(os.path.join(output_dir, '_index.json'), 'w') as f:
        json.dump({
            'metadata': {
                'source': 'Duruo/forecastbench-single_question',
                'total_cases': counter
            },
            'cases': index_list
        }, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ 完成: {counter} cases")
    return counter


def download_and_export_tsqa():
    """下载并导出 TSQA"""
    print("\n=== 3. 下载 robinfaro/TSQA ===")
    repo_id = "robinfaro/TSQA"
    output_dir = "tsqa_cases_10063"
    os.makedirs(output_dir, exist_ok=True)
    
    # 下载
    try:
        hf_hub_download(repo_id=repo_id, filename='dataset.json',
                       repo_type='dataset', local_dir='.cache')
        print(f"  ✅ dataset.json")
    except Exception as e:
        print(f"  ❌ dataset.json: {e}")
        return 0
    
    # 导出
    print(f"  导出到 {output_dir}/ ...")
    with open('.cache/dataset.json') as f:
        data = json.load(f)
    
    index_list = []
    
    for i, item in enumerate(data, 1):
        file_id = f"TSQA_{i:05d}"
        
        # 找出正确答案
        correct_answer = None
        for opt in item.get('options', []):
            if opt.get('tag') == 'correct':
                correct_answer = opt.get('answer')
                break
        
        case = OrderedDict()
        case['file_id'] = file_id
        case['question'] = item.get('question', '')
        case['year'] = item.get('year')
        case['ground_truth'] = correct_answer
        case['ground_truth_tag'] = 'correct'
        case['options'] = item.get('options', [])
        
        with open(os.path.join(output_dir, f"{file_id}.json"), 'w') as f:
            json.dump(case, f, indent=2, ensure_ascii=False)
        
        index_list.append({
            'file_id': file_id,
            'question': item.get('question', '')[:60],
            'year': item.get('year'),
            'ground_truth': correct_answer
        })
    
    # 保存索引
    with open(os.path.join(output_dir, '_index.json'), 'w') as f:
        json.dump({
            'metadata': {
                'source': 'robinfaro/TSQA',
                'total_cases': len(data),
                'years_covered': '2013-2024'
            },
            'cases': index_list
        }, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ 完成: {len(data)} cases")
    return len(data)


def download_and_export_tiebe():
    """下载并导出 TiEBe (World + English)"""
    print("\n=== 4. 下载 TimelyEventsBenchmark/TiEBe ===")
    repo_id = "TimelyEventsBenchmark/TiEBe"
    output_dir = "tiebe_cases"
    os.makedirs(output_dir, exist_ok=True)
    
    # 下载 (先列出可用文件)
    try:
        files = list_repo_files(repo_id, repo_type='dataset')
        target_files = [f for f in files if 'World' in f or 'english' in f][:10]
        
        for filename in target_files:
            try:
                hf_hub_download(repo_id=repo_id, filename=filename,
                              repo_type='dataset', local_dir='.cache')
                print(f"  ✅ {filename}")
            except Exception as e:
                print(f"  ❌ {filename}: {e}")
    except Exception as e:
        print(f"  ❌ 无法列出文件: {e}")
        return 0
    
    # 导出
    print(f"  导出到 {output_dir}/ ...")
    json_files = glob.glob('.cache/data/english/*.json')
    
    counter = 0
    index_list = []
    
    for filepath in json_files:
        country = os.path.basename(filepath).replace('.json', '')
        
        with open(filepath) as f:
            data = json.load(f)
        
        for item in data:
            counter += 1
            file_id = f"TIEBE_{counter:05d}"
            
            case = OrderedDict()
            case['file_id'] = file_id
            case['country'] = country
            case['year'] = item.get('year')
            case['month'] = item.get('month')
            case['question'] = item.get('question', '')
            case['ground_truth'] = item.get('answer', '')
            case['event_desc'] = item.get('event_desc', '')
            
            with open(os.path.join(output_dir, f"{file_id}.json"), 'w') as f:
                json.dump(case, f, indent=2, ensure_ascii=False)
            
            index_list.append({
                'file_id': file_id,
                'country': country,
                'year': item.get('year'),
                'month': item.get('month'),
                'question': item.get('question', '')[:60]
            })
    
    # 保存索引
    with open(os.path.join(output_dir, '_index.json'), 'w') as f:
        json.dump({
            'metadata': {
                'source': 'TimelyEventsBenchmark/TiEBe',
                'total_cases': counter,
                'countries': len(json_files)
            },
            'cases': index_list
        }, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ 完成: {counter} cases from {len(json_files)} countries")
    return counter


def main():
    """主函数"""
    print("=" * 60)
    print("下载 HuggingFace Benchmark 数据集")
    print("=" * 60)
    print()
    
    total = 0
    total += download_and_export_forecasting()
    total += download_and_export_forecastbench()
    total += download_and_export_tsqa()
    total += download_and_export_tiebe()
    
    print()
    print("=" * 60)
    print(f"总计: {total} cases 已导出")
    print("=" * 60)
    print()
    print("导出目录:")
    print("  - forecasting_cases_5516/")
    print("  - forecastbench_cases_902/")
    print("  - tsqa_cases_10063/")
    print("  - tiebe_cases/")


if __name__ == "__main__":
    main()
