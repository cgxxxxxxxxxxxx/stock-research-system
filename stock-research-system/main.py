#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票深度研究报告自动生成系统 - 主入口

用法:
    # 生成首发覆盖报告
    python main.py --report-type initiating_coverage --stock-code 600309
    
    # 生成季报更新报告
    python main.py --report-type earnings_update --stock-code 600309 --quarter 2025Q1
    
    # 使用配置文件
    python main.py --config configs/wanhua_initiating_coverage.yaml
    
    # 指定模块
    python main.py --report-type initiating_coverage --stock-code 600309 \
        --modules data_fetch,financial_analysis,valuation
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional
import yaml

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import Orchestrator
from utils.logger import setup_logger


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def parse_modules(modules_str: Optional[str]) -> List[str]:
    """解析模块参数"""
    if not modules_str:
        return []
    return [m.strip() for m in modules_str.split(',')]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='股票深度研究报告自动生成系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成万华化学首发覆盖报告（完整流程）
  python main.py --report-type initiating_coverage --stock-code 600309
  
  # 生成万华化学2025Q1季报更新
  python main.py --report-type earnings_update --stock-code 600309 --quarter 2025Q1
  
  # 使用配置文件
  python main.py --config configs/wanhua_initiating_coverage.yaml
  
  # 只运行财务分析和估值模块
  python main.py --report-type initiating_coverage --stock-code 600309 \
      --modules financial_analysis,valuation
  
  # 指定DCF参数
  python main.py --report-type initiating_coverage --stock-code 600309 \
      --growth-rate 0.06 --wacc 0.09
        """
    )
    
    # 基本参数
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--report-type', type=str, 
                       choices=['initiating_coverage', 'earnings_update'],
                       help='报告类型')
    parser.add_argument('--stock-code', type=str, help='股票代码')
    parser.add_argument('--company-name', type=str, help='公司名称（可选）')
    parser.add_argument('--market', type=str, default='A股',
                       choices=['A股', '港股', '美股'],
                       help='市场（默认A股）')
    
    # 季报参数
    parser.add_argument('--quarter', type=str, help='季度（如2025Q1）')
    
    # 模块参数
    parser.add_argument('--modules', type=str, 
                       help='要运行的模块，逗号分隔（如data_fetch,financial_analysis,valuation）')
    parser.add_argument('--list-modules', action='store_true', help='列出所有可用模块')
    
    # 估值参数
    parser.add_argument('--growth-rate', type=float, help='DCF永续增长率')
    parser.add_argument('--wacc', type=float, help='加权平均资本成本')
    parser.add_argument('--target-price', type=float, help='目标价')
    parser.add_argument('--rating', type=str, 
                       choices=['买入', '增持', '持有', '减持', '卖出'],
                       help='投资评级')
    
    # 输出参数
    parser.add_argument('--output-format', type=str, default='markdown',
                       choices=['markdown', 'word', 'ppt'],
                       help='输出格式（默认markdown）')
    parser.add_argument('--output-path', type=str, help='输出路径')
    
    # 其他参数
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别')
    parser.add_argument('--dry-run', action='store_true', 
                       help='试运行，不生成报告')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logger(level=args.log_level)
    
    # 列出可用模块
    if args.list_modules:
        print("\n可用模块列表:")
        print("-" * 60)
        config = load_config('config/system_config.yaml')
        for module in config['available_modules']:
            print(f"  {module['id']:20s} - {module['name']}")
            print(f"  {'':20s}   {module['description']}")
            print(f"  {'':20s}   类别: {module['category']}")
            print()
        return
    
    # 加载配置
    if args.config:
        logger.info(f"加载配置文件: {args.config}")
        config = load_config(args.config)
    else:
        config = load_config('config/system_config.yaml')
    
    # 验证必要参数
    if not args.config:
        if not args.report_type:
            parser.error("必须指定 --report-type 或 --config")
        if not args.stock_code:
            parser.error("必须指定 --stock-code")
    
    # 构建任务参数
    task_params = {
        'report_type': args.report_type,
        'stock_code': args.stock_code,
        'company_name': args.company_name,
        'market': args.market,
        'quarter': args.quarter,
        'modules': parse_modules(args.modules),
        'output_format': args.output_format,
        'output_path': args.output_path,
        'dry_run': args.dry_run,
    }
    
    # 添加估值参数
    if args.growth_rate:
        task_params['growth_rate'] = args.growth_rate
    if args.wacc:
        task_params['wacc'] = args.wacc
    if args.target_price:
        task_params['target_price'] = args.target_price
    if args.rating:
        task_params['rating'] = args.rating
    
    # 创建调度器并执行
    logger.info("=" * 60)
    logger.info("股票深度研究报告自动生成系统")
    logger.info("=" * 60)
    logger.info(f"报告类型: {task_params.get('report_type')}")
    logger.info(f"股票代码: {task_params.get('stock_code')}")
    logger.info(f"市场: {task_params.get('market')}")
    if task_params.get('modules'):
        logger.info(f"运行模块: {', '.join(task_params['modules'])}")
    logger.info("=" * 60)
    
    try:
        orchestrator = Orchestrator(config)
        result = orchestrator.run(task_params)
        
        logger.info("=" * 60)
        logger.info("任务执行完成")
        if result.get('report_path'):
            logger.info(f"报告已生成: {result['report_path']}")
        logger.info("=" * 60)
        
        # 打印摘要
        print("\n" + "=" * 60)
        print("执行摘要")
        print("=" * 60)
        print(f"股票代码: {task_params['stock_code']}")
        print(f"报告类型: {task_params['report_type']}")
        if result.get('report_path'):
            print(f"报告路径: {result['report_path']}")
        if result.get('word_count'):
            print(f"报告字数: {result['word_count']}")
        print("=" * 60 + "\n")
        
    except Exception as e:
        logger.error(f"任务执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
