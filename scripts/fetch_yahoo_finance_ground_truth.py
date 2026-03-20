#!/usr/bin/env python3
"""
使用 Yahoo Finance 历史数据生成真实的 Ground Truth
- 下载历史价格数据
- 计算统计特征
- 生成基于历史模式的 ground truth
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 尝试导入 yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️  yfinance not installed. Install with: pip install yfinance")


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_historical_data(ticker, period='1y'):
    """从 Yahoo Finance 获取历史数据"""
    if not YFINANCE_AVAILABLE:
        return None
    
    try:
        # 下载数据
        data = yf.download(ticker, period=period, progress=False)
        
        if data.empty:
            return None
        
        # 计算统计特征
        data['change'] = data['Close'].pct_change()
        data['direction'] = data['change'].apply(lambda x: 'up' if x > 0 else 'down' if x < 0 else 'flat')
        
        stats = {
            'total_days': len(data),
            'up_days': (data['direction'] == 'up').sum(),
            'down_days': (data['direction'] == 'down').sum(),
            'flat_days': (data['direction'] == 'flat').sum(),
            'up_ratio': (data['direction'] == 'up').mean(),
            'avg_change': data['change'].mean(),
            'volatility': data['change'].std(),
            'recent_trend': data['direction'].iloc[-5:].mode()[0] if len(data) >= 5 else 'unknown'
        }
        
        return stats
        
    except Exception as e:
        print(f"  ❌ Error fetching {ticker}: {e}")
        return None


def determine_ground_truth_from_history(stats, case):
    """基于历史统计确定 ground truth"""
    if not stats:
        return None
    
    options = case.get('options', [])
    if len(options) == 2:
        # 二元选择
        # 如果上涨天数 > 50%，选 A (Yes/Up)
        if stats['up_ratio'] > 0.5:
            return {
                'expected_answer': 'A',
                'confidence': stats['up_ratio'],
                'reasoning': f"Historical data shows {stats['up_ratio']:.1%} up days over {stats['total_days']} days",
                'historical_basis': {
                    'up_days': int(stats['up_days']),
                    'down_days': int(stats['down_days']),
                    'up_ratio': float(stats['up_ratio']),
                    'volatility': float(stats['volatility'])
                }
            }
        else:
            return {
                'expected_answer': 'B',
                'confidence': 1 - stats['up_ratio'],
                'reasoning': f"Historical data shows {1-stats['up_ratio']:.1%} down/flat days over {stats['total_days']} days",
                'historical_basis': {
                    'up_days': int(stats['up_days']),
                    'down_days': int(stats['down_days']),
                    'up_ratio': float(stats['up_ratio']),
                    'volatility': float(stats['volatility'])
                }
            }
    else:
        # 多选项，基于 recent trend
        recent = stats.get('recent_trend', 'unknown')
        if recent == 'up':
            return {'expected_answer': 'A', 'confidence': 0.6}
        elif recent == 'down':
            return {'expected_answer': 'C', 'confidence': 0.6}
        else:
            return {'expected_answer': 'B', 'confidence': 0.5}


def main():
    print("=" * 70)
    print("Fetching Ground Truth from Yahoo Finance Historical Data")
    print("=" * 70)
    print()
    
    if not YFINANCE_AVAILABLE:
        print("❌ yfinance not available. Please install:")
        print("   pip install yfinance")
        return 1
    
    # 加载 cases
    input_dir = Path('test_cases_futurex_style')
    case_files = [f for f in input_dir.glob('*.json') if not f.name.startswith('_')]
    
    print(f"📂 Found {len(case_files)} cases")
    print()
    
    # 统计
    updated = 0
    failed = 0
    skipped = 0
    
    for i, case_file in enumerate(case_files, 1):
        case = load_json(case_file)
        
        ticker = case.get('ground_truth', {}).get('ticker', '')
        
        if not ticker:
            print(f"{i}. {case['case_id']}: No ticker, skipped")
            skipped += 1
            continue
        
        print(f"{i}. {case['case_id']}: Fetching {ticker}...", end=' ')
        
        # 获取历史数据
        stats = fetch_historical_data(ticker)
        
        if stats:
            # 基于历史数据更新 ground truth
            gt_update = determine_ground_truth_from_history(stats, case)
            
            if gt_update:
                case['ground_truth'].update(gt_update)
                case['ground_truth']['status'] = 'historical_data_backed'
                case['ground_truth']['data_source'] = 'yahoo_finance_api'
                case['ground_truth']['fetch_date'] = datetime.now().isoformat()
                
                # 保存
                save_json(case, case_file)
                
                print(f"✅ {gt_update['expected_answer']} (confidence: {gt_update['confidence']:.2f})")
                updated += 1
            else:
                print("❌ Failed to determine")
                failed += 1
        else:
            print("❌ No data available")
            failed += 1
    
    print()
    print("=" * 70)
    print("Summary:")
    print(f"  Updated: {updated}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print()
    
    if updated > 0:
        print(f"✅ {updated} cases now have historical-data-backed ground truth!")
        print()
        print("The expected answers are based on:")
        print("- Historical up/down ratios from Yahoo Finance")
        print("- Real market data (1 year period)")
        print("- Statistical patterns (not random)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
