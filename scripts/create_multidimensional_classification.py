#!/usr/bin/env python3
"""
创建多维度分类系统
维度:
1. 领域 (Domain): finance, political, sports, tech, social, science
2. CAP 能力 (CAPability): full, partial, none, llm_only
3. 数据可用性 (DataAvailability): realtime, historical, unavailable
4. 时间范围 (TimeHorizon): short_term, medium_term, long_term
5. 复杂度 (Complexity): L1, L2, L3, L4
"""

import json
import sys
from typing import Dict, List, Tuple


def load_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data: dict, path: str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {path}")


class MultidimensionalClassifier:
    """多维度分类器"""
    
    def __init__(self):
        # 维度定义
        self.dimensions = {
            'domain': ['finance', 'political', 'sports', 'tech', 'social', 'science', 'entertainment'],
            'cap_ability': ['full', 'partial', 'none', 'llm_only'],
            'data_availability': ['realtime', 'historical', 'unavailable'],
            'time_horizon': ['short_term', 'medium_term', 'long_term'],
            'complexity': ['L1', 'L2', 'L3', 'L4']
        }
    
    def classify_domain(self, title: str, context: str = '') -> Tuple[str, float]:
        """分类领域，返回 (领域, 置信度)"""
        text = (title + ' ' + context).lower()
        
        # 关键词映射
        domain_keywords = {
            'finance': ['gold', 'oil', 'crude', 'lumber', 'commodity', 'rate', 'fed', 'ecb', 'boe', 
                       'interest', 'stock', 'price', 'market', 'trading', 'dollar', 'euro', 'pound',
                       'bitcoin', 'crypto', 'btc', 'eth', 'tesla', 'nvidia', 'tsla', 'nvda'],
            'political': ['election', 'vote', 'president', 'political', 'party', 'trump', 'biden',
                         'war', 'gaza', 'israel', 'iran', 'ukraine', 'russia', 'china', 'taiwan'],
            'sports': ['sport', 'olympic', 'tournament', 'superbowl', 'nba', 'nfl', 'soccer',
                      'football', 'rugby', 'tennis', 'golf', 'champion', 'winner', 'cup'],
            'tech': ['ai', 'gpt', 'llm', 'model', 'gemini', 'chatgpt', 'claude', 'chip',
                    'semiconductor', 'gpu', 'algorithm', 'tech', 'software', 'hardware'],
            'entertainment': ['movie', 'film', 'album', 'song', 'grammy', 'music', 'oscar',
                            'celebrity', 'actor', 'singer'],
            'science': ['math', 'usamo', 'amc', 'aime', 'science', 'research', 'physics',
                     'chemistry', 'biology'],
            'social': ['death', 'protest', 'conflict', 'population', 'disease', 'health']
        }
        
        # 计算每个领域的匹配分数
        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[domain] = score
        
        if not scores:
            return 'other', 0.0
        
        # 选择最高分
        best_domain = max(scores, key=scores.get)
        confidence = min(scores[best_domain] / 2, 1.0)  # 简单归一化
        
        return best_domain, confidence
    
    def classify_cap_ability(self, domain: str, title: str, available_nodes: List[str]) -> Tuple[str, str]:
        """
        分类 CAP 能力
        返回: (能力级别, 说明)
        """
        # Abel Graph Computer 已知的节点
        known_cap_nodes = [
            'NVDA_close', 'TSLA_close', 'AAPL_close', 'ETHUSD_close', 'BTCUSD_close',
            'GCUSD_close', 'CLUSD_close', 'SPY_close', 'PEAKUSD_close', 'DXY_close',
            'VIX_close', 'GLD_close', 'SLV_close'
        ]
        
        title_lower = title.lower()
        
        # 检查是否在已知节点中
        has_known_node = any(node.lower().replace('_close', '') in title_lower 
                            for node in known_cap_nodes)
        
        if domain == 'finance':
            if has_known_node:
                return 'full', 'Known ticker in causal graph'
            elif any(kw in title_lower for kw in ['oil', 'gold', 'rate', 'price']):
                return 'partial', 'Financial domain but node availability uncertain'
            else:
                return 'partial', 'Finance domain, need to verify node'
        
        elif domain == 'tech':
            if any(kw in title_lower for kw in ['nvidia', 'tesla', 'chip']):
                return 'partial', 'Tech stocks might be in graph'
            else:
                return 'llm_only', 'AI/tech metrics not in causal graph'
        
        elif domain in ['political', 'sports', 'entertainment', 'social']:
            return 'llm_only', f'{domain} not supported by causal graph'
        
        elif domain == 'science':
            return 'llm_only', 'Scientific/educational not in graph'
        
        else:
            return 'none', 'Unknown domain'
    
    def classify_data_availability(self, domain: str, cap_ability: str) -> str:
        """分类数据可用性"""
        if cap_ability == 'full':
            return 'realtime'
        elif cap_ability == 'partial':
            return 'historical'
        else:
            return 'unavailable'
    
    def classify_time_horizon(self, title: str, end_time: str = '') -> str:
        """分类时间范围"""
        title_lower = title.lower()
        
        # 短期 (几天到几周)
        short_indicators = ['next week', 'tomorrow', 'today', 'this week', 'hours']
        # 中期 (几周到几个月)
        medium_indicators = ['january', 'february', 'march', 'month', '2026']
        # 长期 (几个月到几年)
        long_indicators = ['2027', '2030', 'year', 'annual']
        
        if any(kw in title_lower for kw in short_indicators):
            return 'short_term'
        elif any(kw in title_lower for kw in long_indicators):
            return 'long_term'
        else:
            return 'medium_term'
    
    def classify_complexity(self, level: str) -> str:
        """分类复杂度"""
        level_map = {
            '1': 'L1',
            '2': 'L2',
            '3': 'L3',
            '4': 'L4'
        }
        return level_map.get(str(level), 'L?')
    
    def classify(self, case: dict) -> dict:
        """执行完整的多维度分类"""
        title = case.get('title', '')
        context = case.get('context', '')
        level = case.get('level', '')
        end_time = case.get('end_time', '')
        
        # 各维度分类
        domain, domain_conf = self.classify_domain(title, context)
        cap_ability, cap_reason = self.classify_cap_ability(domain, title, [])
        data_avail = self.classify_data_availability(domain, cap_ability)
        time_horizon = self.classify_time_horizon(title, end_time)
        complexity = self.classify_complexity(level)
        
        # 推荐测试方法
        if cap_ability == 'full':
            recommended_approach = 'CAP_only'
        elif cap_ability == 'partial':
            recommended_approach = 'CAP_first_then_LLM'
        elif cap_ability == 'llm_only':
            recommended_approach = 'LLM_only'
        else:
            recommended_approach = 'Hybrid'
        
        return {
            'dimensions': {
                'domain': {
                    'value': domain,
                    'confidence': domain_conf
                },
                'cap_ability': {
                    'value': cap_ability,
                    'reason': cap_reason
                },
                'data_availability': data_avail,
                'time_horizon': time_horizon,
                'complexity': complexity
            },
            'recommended_approach': recommended_approach,
            'test_priority': 'high' if cap_ability in ['full', 'partial'] else 'low'
        }


def apply_multidimensional_classification():
    """应用多维度分类"""
    print("=" * 70)
    print("Applying Multidimensional Classification")
    print("=" * 70)
    print()
    
    # 1. 加载 benchmark
    benchmark_path = 'src/abel_benchmark/references/benchmark_questions_v2_futurex_d25.json'
    print(f"📂 Loading: {benchmark_path}")
    benchmark = load_json(benchmark_path)
    questions = benchmark.get('questions', [])
    print(f"   Total questions: {len(questions)}")
    print()
    
    # 2. 创建分类器
    classifier = MultidimensionalClassifier()
    
    # 3. 对每个问题分类
    print("🔍 Classifying all questions...")
    for q in questions:
        # 构建 case 数据
        case = {
            'title': q.get('question', ''),
            'context': q.get('context', ''),
            'level': q.get('futurex_metadata', {}).get('level', '') if 'futurex_metadata' in q else '',
            'end_time': q.get('futurex_metadata', {}).get('end_time', '') if 'futurex_metadata' in q else ''
        }
        
        # 执行分类
        classification = classifier.classify(case)
        
        # 添加到问题
        q['multidimensional_classification'] = classification
    
    # 4. 统计各维度
    print("\n📊 Multidimensional Statistics:")
    
    # 按领域统计
    domains = {}
    for q in questions:
        domain = q['multidimensional_classification']['dimensions']['domain']['value']
        domains[domain] = domains.get(domain, 0) + 1
    
    print("\nBy Domain:")
    for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {domain:15}: {count:2} cases")
    
    # 按 CAP 能力统计
    cap_abilities = {}
    for q in questions:
        cap = q['multidimensional_classification']['dimensions']['cap_ability']['value']
        cap_abilities[cap] = cap_abilities.get(cap, 0) + 1
    
    print("\nBy CAP Ability:")
    for cap, count in sorted(cap_abilities.items(), key=lambda x: -x[1]):
        print(f"  {cap:15}: {count:2} cases")
    
    # 按推荐方法统计
    approaches = {}
    for q in questions:
        app = q['multidimensional_classification']['recommended_approach']
        approaches[app] = approaches.get(app, 0) + 1
    
    print("\nBy Recommended Approach:")
    for app, count in sorted(approaches.items(), key=lambda x: -x[1]):
        print(f"  {app:20}: {count:2} cases")
    
    # 5. 更新 benchmark
    benchmark['multidimensional_classification'] = {
        'dimensions': ['domain', 'cap_ability', 'data_availability', 'time_horizon', 'complexity'],
        'statistics': {
            'by_domain': domains,
            'by_cap_ability': cap_abilities,
            'by_approach': approaches
        }
    }
    
    benchmark['questions'] = questions
    
    # 6. 保存
    save_json(benchmark, benchmark_path)
    
    print()
    print("=" * 70)
    print("✅ Multidimensional Classification Applied!")
    print("=" * 70)
    
    # 7. 生成示例报告
    print("\n📋 Sample High-Priority Cases (CAP testable):")
    high_priority = [q for q in questions 
                     if q['multidimensional_classification']['test_priority'] == 'high'][:5]
    
    for i, q in enumerate(high_priority, 1):
        dims = q['multidimensional_classification']['dimensions']
        print(f"{i}. {q['id']}")
        print(f"   Q: {q['question'][:50]}...")
        print(f"   Domain: {dims['domain']['value']}")
        print(f"   CAP: {dims['cap_ability']['value']} ({dims['cap_ability']['reason']})")
        print(f"   Approach: {q['multidimensional_classification']['recommended_approach']}")
        print()


if __name__ == "__main__":
    try:
        apply_multidimensional_classification()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
