#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调度引擎 - 负责模块调度、数据传递和执行流程控制
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from modules.data_fetch.local_checker import LocalChecker
from modules.data_fetch.a_stock_fetcher import AStockFetcher
from modules.financial_analysis.financial_statement import FinancialStatementAnalyzer
from modules.financial_analysis.financial_indicator import FinancialIndicatorCalculator
from modules.financial_analysis.roic_analysis import ROICAnalyzer
from modules.valuation.dcf_model import DCFModel
from modules.valuation.comps_analysis import CompsAnalyzer
from modules.industry_analysis.industry_analysis import IndustryAnalyzer
from modules.competitive_analysis.competitive_landscape import CompetitiveAnalyzer
from modules.report_generation.initiating_coverage import InitiatingCoverageGenerator
from modules.report_generation.earnings_update import EarningsUpdateGenerator


logger = logging.getLogger(__name__)


class Orchestrator:
    """调度引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化调度器
        
        Args:
            config: 系统配置
        """
        self.config = config
        self.modules = {}
        self.context = {}  # 模块间共享的上下文数据
        
        # 初始化所有模块
        self._init_modules()
        
    def _init_modules(self):
        """初始化所有模块"""
        logger.info("初始化模块...")
        
        # 数据获取模块
        self.modules['data_fetch'] = {
            'local_checker': LocalChecker(self.config),
            'a_stock_fetcher': AStockFetcher(self.config),
        }
        
        # 财务分析模块
        self.modules['financial_analysis'] = {
            'financial_statement': FinancialStatementAnalyzer(self.config),
            'financial_indicator': FinancialIndicatorCalculator(self.config),
            'roic_analysis': ROICAnalyzer(self.config),
        }
        
        # 估值建模模块
        self.modules['valuation'] = {
            'dcf_model': DCFModel(self.config),
            'comps_analysis': CompsAnalyzer(self.config),
        }
        
        # 行业分析模块
        self.modules['industry_analysis'] = {
            'industry_analyzer': IndustryAnalyzer(self.config),
        }
        
        # 竞争分析模块
        self.modules['competitive_analysis'] = {
            'competitive_analyzer': CompetitiveAnalyzer(self.config),
        }
        
        # 报告生成模块
        self.modules['report_generation'] = {
            'initiating_coverage': InitiatingCoverageGenerator(self.config),
            'earnings_update': EarningsUpdateGenerator(self.config),
        }
        
        logger.info(f"已初始化 {len(self.modules)} 个模块组")
        
    def run(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task_params: 任务参数
            
        Returns:
            执行结果
        """
        logger.info("开始执行任务...")
        
        # 解析任务参数
        report_type = task_params.get('report_type')
        stock_code = task_params.get('stock_code')
        company_name = task_params.get('company_name')
        market = task_params.get('market', 'A股')
        modules_to_run = task_params.get('modules', [])
        
        # 初始化上下文
        self.context = {
            'stock_code': stock_code,
            'company_name': company_name,
            'market': market,
            'report_type': report_type,
            'start_time': datetime.now(),
            'task_params': task_params,
        }
        
        # 确定要运行的模块
        if not modules_to_run:
            modules_to_run = self._get_default_modules(report_type)
            logger.info(f"使用默认模块: {modules_to_run}")
        
        # 按依赖顺序执行模块
        execution_order = self._resolve_module_order(modules_to_run)
        logger.info(f"执行顺序: {' -> '.join(execution_order)}")
        
        for module_id in execution_order:
            logger.info(f"\n{'='*60}")
            logger.info(f"执行模块: {module_id}")
            logger.info(f"{'='*60}")
            
            try:
                result = self._execute_module(module_id, task_params)
                self.context[module_id] = result
                logger.info(f"模块 {module_id} 执行完成")
            except Exception as e:
                logger.error(f"模块 {module_id} 执行失败: {e}", exc_info=True)
                raise
        
        # 生成报告
        if not task_params.get('dry_run'):
            logger.info("\n" + "="*60)
            logger.info("生成报告...")
            logger.info("="*60)
            
            report_result = self._generate_report(task_params)
            self.context['report'] = report_result
            
            logger.info(f"报告已生成: {report_result.get('report_path')}")
        
        # 返回结果
        self.context['end_time'] = datetime.now()
        self.context['duration'] = (self.context['end_time'] - self.context['start_time']).total_seconds()
        
        logger.info(f"\n任务执行完成，耗时: {self.context['duration']:.2f}秒")
        
        return {
            'report_path': self.context.get('report', {}).get('report_path'),
            'word_count': self.context.get('report', {}).get('word_count'),
            'duration': self.context['duration'],
            'modules_executed': execution_order,
        }
    
    def _get_default_modules(self, report_type: str) -> List[str]:
        """获取默认模块列表"""
        if report_type == 'initiating_coverage':
            return [
                'data_fetch',
                'financial_analysis',
                'valuation',
                'industry_analysis',
                'competitive_analysis',
                'report_generation',
            ]
        elif report_type == 'earnings_update':
            return [
                'data_fetch',
                'financial_analysis',
                'valuation',
                'report_generation',
            ]
        else:
            return ['data_fetch', 'financial_analysis']
    
    def _resolve_module_order(self, modules: List[str]) -> List[str]:
        """
        解析模块执行顺序（基于依赖关系）
        
        Args:
            modules: 要执行的模块列表
            
        Returns:
            排序后的模块列表
        """
        dependencies = self.config.get('module_dependencies', {})
        
        # 简单的拓扑排序
        ordered = []
        visited = set()
        
        def visit(module):
            if module in visited:
                return
            visited.add(module)
            
            # 先访问依赖
            for dep in dependencies.get(module, []):
                if dep in modules:
                    visit(dep)
            
            ordered.append(module)
        
        for module in modules:
            visit(module)
        
        return ordered
    
    def _execute_module(self, module_id: str, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个模块
        
        Args:
            module_id: 模块ID
            task_params: 任务参数
            
        Returns:
            模块执行结果
        """
        module_group = self.modules.get(module_id)
        if not module_group:
            raise ValueError(f"未找到模块: {module_id}")
        
        # 根据模块类型执行
        if module_id == 'data_fetch':
            return self._execute_data_fetch(task_params)
        elif module_id == 'financial_analysis':
            return self._execute_financial_analysis(task_params)
        elif module_id == 'valuation':
            return self._execute_valuation(task_params)
        elif module_id == 'industry_analysis':
            return self._execute_industry_analysis(task_params)
        elif module_id == 'competitive_analysis':
            return self._execute_competitive_analysis(task_params)
        elif module_id == 'report_generation':
            return {}  # 报告生成单独处理
        else:
            raise ValueError(f"未知模块: {module_id}")
    
    def _execute_data_fetch(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据获取模块"""
        stock_code = task_params['stock_code']
        market = task_params.get('market', 'A股')
        
        result = {}
        
        # 1. 检查本地文档
        logger.info("检查本地文档...")
        local_checker = self.modules['data_fetch']['local_checker']
        local_result = local_checker.check(
            stock_code=stock_code,
            company_name=task_params.get('company_name'),
            market=market,
        )
        result['local_files'] = local_result
        
        # 2. 获取API数据
        logger.info("获取API数据...")
        if market == 'A股':
            fetcher = self.modules['data_fetch']['a_stock_fetcher']
            api_result = fetcher.fetch(
                stock_code=stock_code,
                data_types=['balance_sheet', 'income_statement', 'cash_flow', 
                           'financial_indicators', 'realtime_quote'],
            )
            result['api_data'] = api_result
        
        return result
    
    def _execute_financial_analysis(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """执行财务分析模块"""
        stock_code = task_params['stock_code']
        data = self.context.get('data_fetch', {})
        
        result = {}
        
        # 1. 三大报表分析
        logger.info("分析三大报表...")
        fs_analyzer = self.modules['financial_analysis']['financial_statement']
        fs_result = fs_analyzer.analyze(
            stock_code=stock_code,
            data=data.get('api_data', {}),
        )
        result['financial_statement'] = fs_result
        
        # 2. 财务指标计算
        logger.info("计算财务指标...")
        fi_calculator = self.modules['financial_analysis']['financial_indicator']
        fi_result = fi_calculator.calculate(
            stock_code=stock_code,
            data=data.get('api_data', {}),
        )
        result['financial_indicators'] = fi_result
        
        # 3. ROIC分析
        logger.info("ROIC分析...")
        roic_analyzer = self.modules['financial_analysis']['roic_analysis']
        roic_result = roic_analyzer.analyze(
            stock_code=stock_code,
            data=data.get('api_data', {}),
        )
        result['roic_analysis'] = roic_result
        
        return result
    
    def _execute_valuation(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """执行估值建模模块"""
        stock_code = task_params['stock_code']
        financial_data = self.context.get('financial_analysis', {})
        
        result = {}
        
        # 1. DCF估值
        logger.info("DCF估值...")
        dcf_model = self.modules['valuation']['dcf_model']
        dcf_result = dcf_model.valuate(
            stock_code=stock_code,
            financial_data=financial_data,
            growth_rate=task_params.get('growth_rate'),
            wacc=task_params.get('wacc'),
        )
        result['dcf'] = dcf_result
        
        # 2. 可比公司分析
        logger.info("可比公司分析...")
        comps_analyzer = self.modules['valuation']['comps_analysis']
        comps_result = comps_analyzer.analyze(
            stock_code=stock_code,
            financial_data=financial_data,
        )
        result['comps'] = comps_result
        
        return result
    
    def _execute_industry_analysis(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """执行行业分析模块"""
        stock_code = task_params['stock_code']
        
        logger.info("行业分析...")
        analyzer = self.modules['industry_analysis']['industry_analyzer']
        result = analyzer.analyze(
            stock_code=stock_code,
            company_name=task_params.get('company_name'),
        )
        
        return result
    
    def _execute_competitive_analysis(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """执行竞争分析模块"""
        stock_code = task_params['stock_code']
        industry_data = self.context.get('industry_analysis', {})
        
        logger.info("竞争分析...")
        analyzer = self.modules['competitive_analysis']['competitive_analyzer']
        result = analyzer.analyze(
            stock_code=stock_code,
            company_name=task_params.get('company_name'),
            industry_data=industry_data,
        )
        
        return result
    
    def _generate_report(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """生成报告"""
        report_type = task_params['report_type']
        
        if report_type == 'initiating_coverage':
            generator = self.modules['report_generation']['initiating_coverage']
        elif report_type == 'earnings_update':
            generator = self.modules['report_generation']['earnings_update']
        else:
            raise ValueError(f"未知报告类型: {report_type}")
        
        # 收集所有分析结果
        report_data = {
            'stock_code': task_params['stock_code'],
            'company_name': task_params.get('company_name'),
            'market': task_params.get('market', 'A股'),
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'rating': task_params.get('rating', '持有'),
            'target_price': task_params.get('target_price'),
            'data_fetch': self.context.get('data_fetch', {}),
            'financial_analysis': self.context.get('financial_analysis', {}),
            'valuation': self.context.get('valuation', {}),
            'industry_analysis': self.context.get('industry_analysis', {}),
            'competitive_analysis': self.context.get('competitive_analysis', {}),
        }
        
        # 生成报告
        result = generator.generate(report_data)
        
        return result
