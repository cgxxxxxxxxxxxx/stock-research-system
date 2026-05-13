#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROIC与杜邦分析模块 - 投入资本回报率分析与杜邦分解
包括：ROIC计算、ROIC分解、杜邦分析、ROIC趋势分析、ROIC与WACC对比
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class ROICAnalyzerV2:
    """ROIC与杜邦分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化ROIC分析器
        
        Args:
            config: 系统配置
        """
        self.config = config
        
    def analyze(
        self,
        stock_code: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        ROIC与杜邦分析主入口
        
        Args:
            stock_code: 股票代码
            data: 财务数据（包含资产负债表、利润表、现金流量表）
            
        Returns:
            分析结果
        """
        logger.info(f"开始ROIC与杜邦分析: {stock_code}")
        
        result = {
            'stock_code': stock_code,
            'roic_analysis': {},
            'dupont_analysis': {},
        }
        
        try:
            # 1. 计算ROIC
            logger.info("计算ROIC...")
            roic_calculation = self._calculate_roic(data)
            result['roic_analysis']['calculation'] = roic_calculation
            
            # 2. ROIC分解分析
            logger.info("分解ROIC...")
            roic_decomposition = self._decompose_roic(data, roic_calculation)
            result['roic_analysis']['decomposition'] = roic_decomposition
            
            # 3. 杜邦分析（新增）
            logger.info("执行杜邦分析...")
            dupont_analysis = self._perform_dupont_analysis(data)
            result['dupont_analysis'] = dupont_analysis
            
            # 4. ROIC趋势分析
            logger.info("分析ROIC趋势...")
            roic_trend = self._analyze_roic_trend(roic_calculation)
            result['roic_analysis']['trend'] = roic_trend
            
            # 5. ROIC与WACC对比
            logger.info("对比ROIC与WACC...")
            roic_wacc_comparison = self._compare_roic_wacc(roic_calculation, data)
            result['roic_analysis']['wacc_comparison'] = roic_wacc_comparison
            
            # 6. ROIC行业对比
            logger.info("行业ROIC对比...")
            industry_comparison = self._compare_with_industry(roic_calculation, stock_code)
            result['roic_analysis']['industry_comparison'] = industry_comparison
            
            # 7. ROIC质量评估
            logger.info("评估ROIC质量...")
            quality_assessment = self._assess_roic_quality(
                roic_calculation, roic_trend, roic_wacc_comparison
            )
            result['roic_analysis']['quality'] = quality_assessment
            
            # 8. 生成综合总结
            summary = self._generate_summary(result)
            result['summary'] = summary
            
            logger.info("ROIC与杜邦分析完成")
            
        except Exception as e:
            logger.error(f"ROIC与杜邦分析失败: {e}")
            result['error'] = str(e)
            
        return result
    
    def _perform_dupont_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        杜邦分析
        
        ROE = 净利润率 × 资产周转率 × 权益乘数
        ROE = (净利润/销售收入) × (销售收入/总资产) × (总资产/股东权益)
        
        Args:
            data: 财务数据
            
        Returns:
            杜邦分析结果
        """
        dupont = {
            'years': [],
            'roe': [],
            'net_profit_margin': [],      # 净利润率
            'asset_turnover': [],         # 资产周转率
            'equity_multiplier': [],      # 权益乘数
            'analysis': '',
        }
        
        try:
            balance_sheet = data.get('balance_sheet', {})
            income_statement = data.get('income_statement', {})
            
            if not balance_sheet or not income_statement:
                logger.warning("缺少必要的财务数据")
                return dupont
            
            # 获取年份数据
            years = balance_sheet.get('years', [])
            if not years:
                years = income_statement.get('years', [])
            
            dupont['years'] = years
            
            # 计算每年的杜邦分解
            for i, year in enumerate(years):
                try:
                    # 净利润率 = 净利润 / 营业收入
                    net_incomes = income_statement.get('net_income', [])
                    revenues = income_statement.get('revenue', [])
                    
                    net_income = net_incomes[i] if i < len(net_incomes) else 0
                    revenue = revenues[i] if i < len(revenues) else 0
                    
                    net_profit_margin = (net_income / revenue * 100) if revenue > 0 else 0
                    dupont['net_profit_margin'].append(net_profit_margin)
                    
                    # 资产周转率 = 营业收入 / 总资产
                    total_assets = balance_sheet.get('total_assets', [])
                    total_asset = total_assets[i] if i < len(total_assets) else 0
                    
                    asset_turnover = (revenue / total_asset) if total_asset > 0 else 0
                    dupont['asset_turnover'].append(asset_turnover)
                    
                    # 权益乘数 = 总资产 / 股东权益
                    total_equities = balance_sheet.get('total_equity', [])
                    total_equity = total_equities[i] if i < len(total_equities) else 0
                    
                    equity_multiplier = (total_asset / total_equity) if total_equity > 0 else 0
                    dupont['equity_multiplier'].append(equity_multiplier)
                    
                    # ROE = 净利润率 × 资产周转率 × 权益乘数
                    roe = net_profit_margin * asset_turnover * equity_multiplier / 100
                    dupont['roe'].append(roe)
                    
                except Exception as e:
                    logger.warning(f"计算{year}年杜邦分解失败: {e}")
                    dupont['net_profit_margin'].append(0)
                    dupont['asset_turnover'].append(0)
                    dupont['equity_multiplier'].append(0)
                    dupont['roe'].append(0)
            
            # 生成分析文本
            dupont['analysis'] = self._generate_dupont_analysis(dupont)
            
        except Exception as e:
            logger.error(f"杜邦分析失败: {e}")
        
        return dupont
    
    def _generate_dupont_analysis(self, dupont: Dict[str, Any]) -> str:
        """生成杜邦分析文本"""
        if not dupont['roe']:
            return "数据不足，无法进行杜邦分析"
        
        # 计算平均值
        avg_roe = np.mean(dupont['roe'])
        avg_margin = np.mean(dupont['net_profit_margin'])
        avg_turnover = np.mean(dupont['asset_turnover'])
        avg_multiplier = np.mean(dupont['equity_multiplier'])
        
        # 分析ROE驱动因素
        analysis_parts = []
        
        analysis_parts.append(
            f"**杜邦分析**：平均ROE为{avg_roe:.2f}%，"
            f"由净利润率{avg_margin:.2f}%、资产周转率{avg_turnover:.2f}倍、"
            f"权益乘数{avg_multiplier:.2f}倍共同驱动。"
        )
        
        # 判断主要驱动因素
        if avg_margin > 15:
            analysis_parts.append("ROE主要由较高的盈利能力驱动。")
        elif avg_turnover > 1:
            analysis_parts.append("ROE主要由较高的资产使用效率驱动。")
        elif avg_multiplier > 3:
            analysis_parts.append("ROE主要由较高的财务杠杆驱动，需关注财务风险。")
        else:
            analysis_parts.append("ROE驱动因素较为均衡。")
        
        # 趋势分析
        if len(dupont['roe']) >= 2:
            if dupont['roe'][-1] > dupont['roe'][0]:
                trend = "上升"
            elif dupont['roe'][-1] < dupont['roe'][0]:
                trend = "下降"
            else:
                trend = "稳定"
            
            analysis_parts.append(f"ROE呈{trend}趋势。")
        
        return ''.join(analysis_parts)
    
    def _calculate_roic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算ROIC
        
        ROIC = NOPAT / Invested Capital
        
        NOPAT (Net Operating Profit After Tax) = EBIT × (1 - Tax Rate)
        Invested Capital = Total Equity + Total Debt - Cash & Equivalents
        
        Args:
            data: 财务数据
            
        Returns:
            ROIC计算结果
        """
        calculation = {
            'years': [],
            'nopat': [],
            'invested_capital': [],
            'roic': [],
            'details': {},
        }
        
        try:
            balance_sheet = data.get('balance_sheet', {})
            income_statement = data.get('income_statement', {})
            
            if not balance_sheet or not income_statement:
                logger.warning("缺少必要的财务数据")
                return calculation
            
            # 获取年份数据
            years = balance_sheet.get('years', [])
            if not years:
                years = income_statement.get('years', [])
            
            calculation['years'] = years
            
            # 计算每年的ROIC
            for i, year in enumerate(years):
                try:
                    # NOPAT计算
                    operating_income = income_statement.get('operating_income', [])
                    if not operating_income:
                        net_income = income_statement.get('net_income', [])
                        interest_expense = income_statement.get('interest_expense', [0] * len(years))
                        income_tax = income_statement.get('income_tax', [0] * len(years))
                        
                        if i < len(net_income):
                            ebit = net_income[i] + (interest_expense[i] if i < len(interest_expense) else 0) + (income_tax[i] if i < len(income_tax) else 0)
                        else:
                            ebit = 0
                    else:
                        ebit = operating_income[i] if i < len(operating_income) else 0
                    
                    # 所得税率
                    income_tax = income_statement.get('income_tax', [0] * len(years))
                    pre_tax_income = income_statement.get('pre_tax_income', [])
                    
                    if pre_tax_income and i < len(pre_tax_income) and pre_tax_income[i] != 0:
                        tax_rate = (income_tax[i] if i < len(income_tax) else 0) / pre_tax_income[i]
                    else:
                        tax_rate = 0.25
                    
                    # NOPAT = EBIT × (1 - Tax Rate)
                    nopat = ebit * (1 - tax_rate)
                    calculation['nopat'].append(nopat)
                    
                    # Invested Capital计算
                    total_equity = balance_sheet.get('total_equity', [])
                    equity = total_equity[i] if i < len(total_equity) else 0
                    
                    short_term_debt = balance_sheet.get('short_term_debt', [])
                    long_term_debt = balance_sheet.get('long_term_debt', [])
                    
                    total_debt = (short_term_debt[i] if i < len(short_term_debt) else 0) + \
                                (long_term_debt[i] if i < len(long_term_debt) else 0)
                    
                    cash = balance_sheet.get('cash', [])
                    cash_equivalents = cash[i] if i < len(cash) else 0
                    
                    invested_capital = equity + total_debt - cash_equivalents
                    calculation['invested_capital'].append(invested_capital)
                    
                    # ROIC = NOPAT / Invested Capital
                    if invested_capital > 0:
                        roic = (nopat / invested_capital) * 100
                    else:
                        roic = 0
                    
                    calculation['roic'].append(roic)
                    
                except Exception as e:
                    logger.warning(f"计算{year}年ROIC失败: {e}")
                    calculation['nopat'].append(0)
                    calculation['invested_capital'].append(0)
                    calculation['roic'].append(0)
            
            # 保存计算细节
            calculation['details'] = {
                'formula': 'ROIC = NOPAT / Invested Capital',
                'nopat_formula': 'NOPAT = EBIT × (1 - Tax Rate)',
                'invested_capital_formula': 'Invested Capital = Equity + Debt - Cash',
                'average_roic': np.mean(calculation['roic']) if calculation['roic'] else 0,
                'latest_roic': calculation['roic'][-1] if calculation['roic'] else 0,
            }
            
        except Exception as e:
            logger.error(f"ROIC计算失败: {e}")
        
        return calculation
    
    def _decompose_roic(
        self,
        data: Dict[str, Any],
        roic_calculation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        ROIC分解分析
        
        ROIC = NOPAT Margin × Capital Turnover
        NOPAT Margin = NOPAT / Revenue
        Capital Turnover = Revenue / Invested Capital
        
        Args:
            data: 财务数据
            roic_calculation: ROIC计算结果
            
        Returns:
            ROIC分解结果
        """
        decomposition = {
            'years': [],
            'nopat_margin': [],
            'capital_turnover': [],
            'analysis': '',
        }
        
        try:
            income_statement = data.get('income_statement', {})
            years = roic_calculation.get('years', [])
            
            decomposition['years'] = years
            
            for i, year in enumerate(years):
                try:
                    # NOPAT Margin = NOPAT / Revenue
                    nopat = roic_calculation['nopat'][i] if i < len(roic_calculation['nopat']) else 0
                    revenue = income_statement.get('revenue', [])
                    rev = revenue[i] if i < len(revenue) else 0
                    
                    if rev > 0:
                        nopat_margin = (nopat / rev) * 100
                    else:
                        nopat_margin = 0
                    
                    decomposition['nopat_margin'].append(nopat_margin)
                    
                    # Capital Turnover = Revenue / Invested Capital
                    invested_capital = roic_calculation['invested_capital'][i] if i < len(roic_calculation['invested_capital']) else 0
                    
                    if invested_capital > 0:
                        capital_turnover = rev / invested_capital
                    else:
                        capital_turnover = 0
                    
                    decomposition['capital_turnover'].append(capital_turnover)
                    
                except Exception as e:
                    logger.warning(f"分解{year}年ROIC失败: {e}")
                    decomposition['nopat_margin'].append(0)
                    decomposition['capital_turnover'].append(0)
            
            # 生成分析文本
            if decomposition['nopat_margin'] and decomposition['capital_turnover']:
                avg_margin = np.mean(decomposition['nopat_margin'])
                avg_turnover = np.mean(decomposition['capital_turnover'])
                
                decomposition['analysis'] = (
                    f"ROIC可分解为NOPAT利润率和资本周转率的乘积。"
                    f"平均NOPAT利润率为{avg_margin:.2f}%，"
                    f"平均资本周转率为{avg_turnover:.2f}倍。"
                )
                
                if avg_margin > 15 and avg_turnover > 1:
                    decomposition['analysis'] += "公司兼具较高的盈利能力和资本使用效率。"
                elif avg_margin > 15:
                    decomposition['analysis'] += "ROIC主要由较高的盈利能力驱动。"
                elif avg_turnover > 1:
                    decomposition['analysis'] += "ROIC主要由较高的资本周转率驱动。"
                else:
                    decomposition['analysis'] += "盈利能力和资本使用效率均有提升空间。"
            
        except Exception as e:
            logger.error(f"ROIC分解失败: {e}")
        
        return decomposition
    
    def _analyze_roic_trend(self, roic_calculation: Dict[str, Any]) -> Dict[str, Any]:
        """ROIC趋势分析"""
        trend = {
            'direction': '',
            'volatility': '',
            'cagr': None,
            'analysis': '',
        }
        
        try:
            roic_values = roic_calculation.get('roic', [])
            
            if not roic_values or len(roic_values) < 2:
                trend['analysis'] = "数据不足，无法进行趋势分析"
                return trend
            
            if roic_values[-1] > roic_values[0]:
                trend['direction'] = '上升'
            elif roic_values[-1] < roic_values[0]:
                trend['direction'] = '下降'
            else:
                trend['direction'] = '稳定'
            
            std_dev = np.std(roic_values)
            mean_roic = np.mean(roic_values)
            
            if mean_roic > 0:
                cv = std_dev / mean_roic
                if cv < 0.1:
                    trend['volatility'] = '低'
                elif cv < 0.3:
                    trend['volatility'] = '中等'
                else:
                    trend['volatility'] = '高'
            else:
                trend['volatility'] = '无法评估'
            
            if len(roic_values) >= 2 and roic_values[0] > 0:
                years = len(roic_values) - 1
                cagr = ((roic_values[-1] / roic_values[0]) ** (1/years) - 1) * 100
                trend['cagr'] = cagr
            
            trend['analysis'] = (
                f"ROIC呈{trend['direction']}趋势，波动性{trend['volatility']}。"
            )
            
            if trend['cagr'] is not None:
                trend['analysis'] += f"年均复合增长率为{trend['cagr']:.2f}%。"
            
        except Exception as e:
            logger.error(f"ROIC趋势分析失败: {e}")
        
        return trend
    
    def _compare_roic_wacc(
        self,
        roic_calculation: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """ROIC与WACC对比"""
        comparison = {
            'latest_roic': None,
            'wacc': None,
            'spread': None,
            'value_creation': '',
            'analysis': '',
        }
        
        try:
            roic_values = roic_calculation.get('roic', [])
            if roic_values:
                comparison['latest_roic'] = roic_values[-1]
            
            # 估算WACC
            balance_sheet = data.get('balance_sheet', {})
            
            total_equity = balance_sheet.get('total_equity', [])
            short_term_debt = balance_sheet.get('short_term_debt', [])
            long_term_debt = balance_sheet.get('long_term_debt', [])
            
            if total_equity and (short_term_debt or long_term_debt):
                equity = total_equity[-1] if total_equity else 0
                debt = (short_term_debt[-1] if short_term_debt else 0) + \
                      (long_term_debt[-1] if long_term_debt else 0)
                
                total_capital = equity + debt
                
                if total_capital > 0:
                    equity_weight = equity / total_capital
                    debt_weight = debt / total_capital
                    
                    risk_free_rate = 0.04
                    market_risk_premium = 0.06
                    beta = 1.0
                    cost_of_equity = risk_free_rate + beta * market_risk_premium
                    
                    cost_of_debt = 0.06
                    tax_rate = 0.25
                    
                    wacc = (equity_weight * cost_of_equity + 
                           debt_weight * cost_of_debt * (1 - tax_rate)) * 100
                    
                    comparison['wacc'] = wacc
                    
                    if comparison['latest_roic'] is not None:
                        comparison['spread'] = comparison['latest_roic'] - wacc
                        
                        if comparison['spread'] > 2:
                            comparison['value_creation'] = '强价值创造'
                        elif comparison['spread'] > 0:
                            comparison['value_creation'] = '价值创造'
                        elif comparison['spread'] > -2:
                            comparison['value_creation'] = '价值损毁'
                        else:
                            comparison['value_creation'] = '严重价值损毁'
                        
                        comparison['analysis'] = (
                            f"最新ROIC为{comparison['latest_roic']:.2f}%，"
                            f"估算WACC为{wacc:.2f}%，"
                            f"ROIC-WACC利差为{comparison['spread']:.2f}个百分点，"
                            f"公司处于{comparison['value_creation']}状态。"
                        )
            
        except Exception as e:
            logger.error(f"ROIC与WACC对比失败: {e}")
        
        return comparison
    
    def _compare_with_industry(
        self,
        roic_calculation: Dict[str, Any],
        stock_code: str,
    ) -> Dict[str, Any]:
        """ROIC行业对比"""
        comparison = {
            'company_roic': None,
            'industry_avg_roic': None,
            'percentile': None,
            'analysis': '',
        }
        
        try:
            roic_values = roic_calculation.get('roic', [])
            if roic_values:
                comparison['company_roic'] = roic_values[-1]
            
            # 简化处理，假设行业平均ROIC为12%
            comparison['industry_avg_roic'] = 12.0
            comparison['analysis'] = (
                f"公司ROIC为{comparison['company_roic']:.2f}%，"
                f"行业平均ROIC约为{comparison['industry_avg_roic']:.2f}%。"
            )
            
            if comparison['company_roic'] > comparison['industry_avg_roic'] * 1.2:
                comparison['analysis'] += "公司ROIC显著高于行业平均，竞争优势明显。"
            elif comparison['company_roic'] > comparison['industry_avg_roic']:
                comparison['analysis'] += "公司ROIC高于行业平均，具备一定竞争优势。"
            elif comparison['company_roic'] > comparison['industry_avg_roic'] * 0.8:
                comparison['analysis'] += "公司ROIC接近行业平均水平。"
            else:
                comparison['analysis'] += "公司ROIC低于行业平均，需提升资本使用效率。"
            
        except Exception as e:
            logger.error(f"ROIC行业对比失败: {e}")
        
        return comparison
    
    def _assess_roic_quality(
        self,
        roic_calculation: Dict[str, Any],
        roic_trend: Dict[str, Any],
        roic_wacc_comparison: Dict[str, Any],
    ) -> Dict[str, Any]:
        """ROIC质量评估"""
        quality = {
            'score': 0,
            'grade': '',
            'factors': [],
            'recommendations': [],
            'analysis': '',
        }
        
        try:
            score = 0
            factors = []
            
            # ROIC水平（40分）
            latest_roic = roic_calculation.get('details', {}).get('latest_roic', 0)
            
            if latest_roic > 20:
                score += 40
                factors.append(('ROIC水平', '优秀（>20%）', 40))
            elif latest_roic > 15:
                score += 32
                factors.append(('ROIC水平', '良好（15-20%）', 32))
            elif latest_roic > 10:
                score += 24
                factors.append(('ROIC水平', '中等（10-15%）', 24))
            elif latest_roic > 5:
                score += 16
                factors.append(('ROIC水平', '一般（5-10%）', 16))
            else:
                score += 8
                factors.append(('ROIC水平', '较差（<5%）', 8))
            
            # ROIC趋势（30分）
            trend_direction = roic_trend.get('direction', '')
            
            if trend_direction == '上升':
                score += 30
                factors.append(('ROIC趋势', '上升', 30))
            elif trend_direction == '稳定':
                score += 20
                factors.append(('ROIC趋势', '稳定', 20))
            else:
                score += 10
                factors.append(('ROIC趋势', '下降', 10))
            
            # ROIC vs WACC（30分）
            spread = roic_wacc_comparison.get('spread')
            
            if spread is not None:
                if spread > 5:
                    score += 30
                    factors.append(('ROIC-WACC利差', '显著为正（>5%）', 30))
                elif spread > 0:
                    score += 20
                    factors.append(('ROIC-WACC利差', '为正', 20))
                elif spread > -5:
                    score += 10
                    factors.append(('ROIC-WACC利差', '略为负', 10))
                else:
                    score += 0
                    factors.append(('ROIC-WACC利差', '显著为负', 0))
            
            quality['score'] = score
            quality['factors'] = factors
            
            if score >= 80:
                quality['grade'] = 'A（优秀）'
            elif score >= 60:
                quality['grade'] = 'B（良好）'
            elif score >= 40:
                quality['grade'] = 'C（中等）'
            else:
                quality['grade'] = 'D（较差）'
            
            recommendations = []
            
            if latest_roic < 10:
                recommendations.append("提升盈利能力，优化成本结构")
            
            if trend_direction == '下降':
                recommendations.append("分析ROIC下降原因，采取改善措施")
            
            if spread is not None and spread < 0:
                recommendations.append("优化资本结构，降低资本成本")
            
            if not recommendations:
                recommendations.append("保持当前良好状态，持续优化资本配置")
            
            quality['recommendations'] = recommendations
            
            quality['analysis'] = (
                f"ROIC质量评分：{score}分，评级：{quality['grade']}。"
            )
            
        except Exception as e:
            logger.error(f"ROIC质量评估失败: {e}")
        
        return quality
    
    def _generate_summary(self, result: Dict[str, Any]) -> str:
        """生成综合总结"""
        summary_parts = []
        
        # ROIC分析
        roic_analysis = result.get('roic_analysis', {})
        calculation = roic_analysis.get('calculation', {})
        details = calculation.get('details', {})
        
        if details.get('latest_roic') is not None:
            summary_parts.append(
                f"**ROIC分析**：最新ROIC为{details['latest_roic']:.2f}%，"
                f"平均ROIC为{details.get('average_roic', 0):.2f}%。"
            )
        
        # 杜邦分析
        dupont_analysis = result.get('dupont_analysis', {})
        if dupont_analysis.get('analysis'):
            summary_parts.append(f"**杜邦分析**：{dupont_analysis['analysis']}")
        
        # 价值创造
        wacc_comparison = roic_analysis.get('wacc_comparison', {})
        if wacc_comparison.get('analysis'):
            summary_parts.append(f"**价值创造**：{wacc_comparison['analysis']}")
        
        # 质量评估
        quality = roic_analysis.get('quality', {})
        if quality.get('analysis'):
            summary_parts.append(f"**质量评估**：{quality['analysis']}")
        
        return '\n\n'.join(summary_parts)
