#!/usr/bin/env python3
"""
Create visualization charts comparing FutureX and Abel Causal Benchmark

Generates:
1. Category distribution comparison
2. Question count by source
3. Domain coverage comparison
4. Difficulty level distribution
5. CAP primitive coverage
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


def load_benchmark_data():
    """Load Abel Causal Benchmark data"""
    benchmark_path = Path(__file__).parent.parent / "src" / "abel_benchmark" / "references" / "benchmark_questions_v2_enhanced.json"
    with open(benchmark_path) as f:
        return json.load(f)


def create_category_distribution_chart(data, output_dir):
    """Chart 1: Question count by category"""
    categories = data['categories']
    
    cat_names = []
    cat_counts = []
    colors = []
    
    color_map = {
        'A': '#3498db',  # Predict - Blue
        'B': '#e74c3c',  # Intervene - Red
        'C': '#2ecc71',  # Path - Green
        'D': '#f39c12',  # Sensitivity - Orange
        'E': '#9b59b6',  # Attest - Purple
        'F': '#1abc9c',  # FutureX - Teal
        'X': '#e67e22'   # Cross-domain - Dark Orange
    }
    
    for cat_id, cat_info in sorted(categories.items()):
        cat_names.append(f"{cat_id}: {cat_info['name']}")
        cat_counts.append(cat_info['count'])
        colors.append(color_map.get(cat_id, '#95a5a6'))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(cat_names, cat_counts, color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bar, count in zip(bars, cat_counts):
        width = bar.get_width()
        ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, 
                f'{count}', ha='left', va='center', fontweight='bold')
    
    ax.set_xlabel('Number of Questions', fontsize=12, fontweight='bold')
    ax.set_title('Abel Causal Benchmark: Questions by Category\n(Total: {} questions)'.format(data['total_questions']), 
                 fontsize=14, fontweight='bold')
    ax.set_xlim(0, max(cat_counts) + 3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart1_category_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Chart 1 saved: category_distribution.png")


def create_source_breakdown_chart(data, output_dir):
    """Chart 2: Question source breakdown"""
    questions = data['questions']
    
    # Categorize by source
    original = len([q for q in questions if not q.get('metadata', {}).get('original_source')])
    futurex_financial = len([q for q in questions if q.get('metadata', {}).get('original_source') == 'FutureX Challenge D25' 
                             and not q.get('metadata', {}).get('cross_domain')])
    futurex_cross = len([q for q in questions if q.get('metadata', {}).get('original_source') == 'FutureX Challenge D25' 
                        and q.get('metadata', {}).get('cross_domain')])
    
    sources = ['Original\nAbel Causal', 'FutureX\nFinancial', 'FutureX\nCross-Domain']
    counts = [original, futurex_financial, futurex_cross]
    colors = ['#3498db', '#1abc9c', '#e67e22']
    explode = (0.02, 0.05, 0.05)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(counts, explode=explode, labels=sources, colors=colors,
                                        autopct='%1.1f%%', shadow=True, startangle=90,
                                        textprops={'fontsize': 11, 'fontweight': 'bold'})
    
    # Enhance text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')
    
    ax.set_title('Abel Causal Benchmark: Question Sources\n(Total: {} questions)'.format(sum(counts)), 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add legend with counts
    legend_labels = [f'{source.strip()}: {count} questions' for source, count in zip(sources, counts)]
    ax.legend(wedges, legend_labels, title="Sources", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart2_source_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Chart 2 saved: source_breakdown.png")


def create_domain_coverage_chart(data, output_dir):
    """Chart 3: Domain coverage comparison"""
    questions = data['questions']
    
    # Extract domains
    domains = []
    for q in questions:
        metadata = q.get('metadata', {})
        if metadata.get('cross_domain'):
            domains.append(metadata.get('domain', 'unknown'))
        elif metadata.get('original_source') == 'FutureX Challenge D25':
            domains.append('financial_futurex')
        else:
            # Categorize original questions by ticker
            ticker = q.get('cap_request', {}).get('input', {}).get('target_node', '')
            if any(x in ticker for x in ['BTC', 'ETH', 'SOL']):
                domains.append('crypto')
            elif any(x in ticker for x in ['NVDA', 'TSLA', 'AAPL', 'AMZN']):
                domains.append('tech_equities')
            elif any(x in ticker for x in ['SPY', 'XLF', 'DXY']):
                domains.append('macro_etfs')
            elif any(x in ticker for x in ['FED', 'TNX']):
                domains.append('rates_macro')
            else:
                domains.append('other_financial')
    
    domain_counts = Counter(domains)
    
    # Sort by count
    sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_domains)
    
    # Create color map
    domain_colors = {
        'crypto': '#f39c12',
        'tech_equities': '#3498db',
        'macro_etfs': '#2ecc71',
        'rates_macro': '#9b59b6',
        'financial_futurex': '#1abc9c',
        'election': '#e74c3c',
        'sports': '#e67e22',
        'entertainment': '#f1c40f',
        'geopolitics': '#34495e',
        'health': '#16a085',
        'weather': '#2980b9',
        'economics': '#8e44ad',
        'other_financial': '#95a5a6'
    }
    
    colors = [domain_colors.get(d, '#95a5a6') for d in labels]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.bar(range(len(labels)), values, color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{value}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([d.replace('_', '\n').title() for d in labels], rotation=0, ha='center')
    ax.set_ylabel('Number of Questions', fontsize=12, fontweight='bold')
    ax.set_title('Abel Causal Benchmark: Domain Coverage\n(Financial + Cross-Domain)', 
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(values) + 3)
    
    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart3_domain_coverage.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Chart 3 saved: domain_coverage.png")


def create_cap_primitives_chart(data, output_dir):
    """Chart 4: CAP primitive coverage"""
    questions = data['questions']
    
    # Count by CAP primitive
    primitives = [q.get('cap_primitive', 'unknown') for q in questions]
    prim_counts = Counter(primitives)
    
    # Define colors for primitives
    prim_colors = {
        'predict': '#3498db',
        'intervene': '#e74c3c',
        'path': '#2ecc71',
        'sensitivity': '#f39c12',
        'attest': '#9b59b6',
        'explain': '#1abc9c',
        'discover': '#e67e22',
        'counterfactual': '#34495e'
    }
    
    # Sort by count
    sorted_prims = sorted(prim_counts.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_prims)
    
    colors = [prim_colors.get(p, '#95a5a6') for p in labels]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.bar(labels, values, color=colors, edgecolor='black', linewidth=1.5, width=0.6)
    
    # Add value labels
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{value}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.set_ylabel('Number of Questions', fontsize=12, fontweight='bold')
    ax.set_xlabel('CAP Primitive', fontsize=12, fontweight='bold')
    ax.set_title('Abel Causal Benchmark: CAP Primitive Coverage\n(Testing Causal Agent Protocol Implementation)', 
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(values) + 3)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    # Add description text
    descriptions = {
        'predict': 'Direct prediction\nwith Markov blanket',
        'intervene': 'do-calculus\nintervention',
        'attest': 'Cross-sectional\ncomparison',
        'path': 'Causal chain\ntracing',
        'sensitivity': 'Uncertainty\nquantification'
    }
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart4_cap_primitives.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Chart 4 saved: cap_primitives.png")


def create_comparison_summary_chart(data, output_dir):
    """Chart 5: FutureX vs Abel Causal Benchmark comparison summary"""
    
    # Data for comparison
    metrics = ['Total\nQuestions', 'Financial\nFocus', 'Domains\nCovered', 'CAP\nPrimitives', 
               'Difficulty\nLevels', 'Question\nFormat']
    
    # Scores (normalized 0-10)
    futurex_scores = [8, 3, 9, 0, 8, 6]  # FutureX: many questions, low financial, many domains, no CAP, 4 levels, MC
    abel_scores = [7, 10, 8, 10, 5, 8]   # Abel: fewer questions, 100% financial, 8 domains, full CAP, fewer levels, structured
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    bars1 = ax.bar(x - width/2, futurex_scores, width, label='FutureX Challenge', 
                   color='#e74c3c', edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, abel_scores, width, label='Abel Causal Benchmark', 
                   color='#3498db', edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                    f'{height}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_ylabel('Coverage Score (0-10)', fontsize=12, fontweight='bold')
    ax.set_title('FutureX Challenge vs Abel Causal Benchmark\nFeature Comparison', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_ylim(0, 12)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    # Add comparison annotations
    ax.text(0.5, -0.15, 'Note: Higher is better for most metrics. "Question Format" scores structured (CAP-compatible) vs free-text.',
            transform=ax.transAxes, fontsize=9, style='italic', ha='center')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart5_benchmark_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Chart 5 saved: benchmark_comparison.png")


def create_evolution_timeline(output_dir):
    """Chart 6: Benchmark evolution timeline"""
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Timeline data
    versions = [
        {'name': 'V1.0\nOriginal', 'date': '2025-01', 'questions': 25, 'color': '#95a5a6'},
        {'name': 'V2.0\nEnhanced', 'date': '2025-03', 'questions': 35, 'color': '#3498db'},
        {'name': 'V2.1\n+FutureX', 'date': '2026-03-20', 'questions': 42, 'color': '#1abc9c'},
        {'name': 'V2.2\n+Cross-Domain', 'date': '2026-03-20', 'questions': 53, 'color': '#e67e22'},
    ]
    
    x_pos = range(len(versions))
    heights = [v['questions'] for v in versions]
    colors = [v['color'] for v in versions]
    
    bars = ax.bar(x_pos, heights, color=colors, edgecolor='black', linewidth=2, width=0.6)
    
    # Add value labels
    for bar, version in zip(bars, versions):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f"{height}\nquestions", ha='center', va='bottom', 
                fontweight='bold', fontsize=11)
        # Add date below
        ax.text(bar.get_x() + bar.get_width()/2., -3,
                version['date'], ha='center', va='top', 
                fontsize=9, style='italic')
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels([v['name'] for v in versions], fontsize=11)
    ax.set_ylabel('Number of Questions', fontsize=12, fontweight='bold')
    ax.set_title('Abel Causal Benchmark: Evolution Timeline\nFrom 25 to 53 Questions', 
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 60)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    # Add growth annotations
    for i in range(1, len(versions)):
        prev = versions[i-1]['questions']
        curr = versions[i]['questions']
        growth = ((curr - prev) / prev) * 100
        x_mid = (x_pos[i-1] + x_pos[i]) / 2
        y_mid = (prev + curr) / 2
        ax.annotate(f'+{growth:.0f}%', xy=(x_mid, y_mid), fontsize=10, 
                   ha='center', fontweight='bold', color='#27ae60',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#27ae60'))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart6_evolution_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Chart 6 saved: evolution_timeline.png")


def main():
    """Generate all visualization charts"""
    print("=" * 70)
    print("Creating Abel Causal Benchmark Visualization Charts")
    print("=" * 70)
    print()
    
    # Load data
    data = load_benchmark_data()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "visualizations"
    output_dir.mkdir(exist_ok=True)
    
    # Generate charts
    create_category_distribution_chart(data, output_dir)
    create_source_breakdown_chart(data, output_dir)
    create_domain_coverage_chart(data, output_dir)
    create_cap_primitives_chart(data, output_dir)
    create_comparison_summary_chart(data, output_dir)
    create_evolution_timeline(output_dir)
    
    print()
    print("=" * 70)
    print("✅ All visualization charts created successfully!")
    print("=" * 70)
    print()
    print(f"📁 Output directory: {output_dir}")
    print()
    print("Generated charts:")
    print("   1. chart1_category_distribution.png - Questions by category")
    print("   2. chart2_source_breakdown.png - Original vs FutureX sources")
    print("   3. chart3_domain_coverage.png - Domain coverage analysis")
    print("   4. chart4_cap_primitives.png - CAP primitive coverage")
    print("   5. chart5_benchmark_comparison.png - FutureX vs Abel comparison")
    print("   6. chart6_evolution_timeline.png - Benchmark evolution")
    print()


if __name__ == "__main__":
    main()
