#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三大报表分析器 - 分析资产负债表、利润表、现金流量表
参考Claude Financial Services的财务分析最佳实践
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class FinancialStatementAnalyzer:
    """三大报表分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化
        
        Args:
            config: 系统配置
        """
        self.config = config
        self.default_period = config['modules']['financial_analysis'].get('default_period', '5y')
        
    def analyze(
        self,
        stock_code: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        分析三大报表
        
        Args:
            stock_code: 股票代码
            data: 财务数据
            
        Returns:
            分析结果
        """
        logger.info(f"分析三大报表: {stock_code}")
        
        result = {
            'stock_code': stock_code,
            'analysis_time': datetime.now().isoformat(),
            'balance_sheet_analysis': {},
            'income_statement_analysis': {},
            'cash_flow_analysis': {},
            'summary': {},
        }
        
        # 提取数据
        balance_sheet_data = data.get('balance_sheet', {}).get('data', [])
        income_statement_data = data.get('income_statement', {}).get('data', [])
        cash_flow_data = data.get('cash_flow', {}).get('data', [])
        
        # 分析资产负债表
        if balance_sheet_data:
            result['balance_sheet_analysis'] = self._analyze_balance_sheet(balance_sheet_data)
            
        # 分析利润表
        if income_statement_data:
            result['income_statement_analysis'] = self._analyze_income_statement(income_statement_data)
            
        # 分析现金流量表
        if cash_flow_data:
            result['cash_flow_analysis'] = self._analyze_cash_flow(cash_flow_data)
            
        # 生成综合摘要
        result['summary'] = self._generate_summary(result)
        
        return result
        
    def _analyze_balance_sheet(self, data: List[Dict]) -> Dict[str, Any]:
        """
        分析资产负债表
        
        Args:
            data: 资产负债表数据
            
        Returns:
            分析结果
        """
        logger.info("分析资产负债表...")
        
        if not data:
            return {'error': '无数据'}
            
        try:
            df = pd.DataFrame(data)
            
            # 提取最近5年的数据
            recent_data = df.head(20)  # 最近20个报告期
            
            analysis = {
                'total_assets_trend': [],
                'asset_structure': {},
                'liability_structure': {},
                'key_ratios': {},
                'assessment': {},
            }
            
            # 总资产趋势
            if '资产总计' in df.columns:
                assets = recent_data[['报告期', '资产总计']].head(10)
                analysis['total_assets_trend'] = assets.to_dict('records')
                
            # 资产结构分析
            if all(col in df.columns for col in ['流动资产合计', '非流动资产合计', '资产总计']):
                latest = df.iloc[0]
                total_assets = latest.get('资产总计', 0)
                if total_assets > 0:
                    analysis['asset_structure'] = {
                        'current_assets': latest.get('流动资产合计', 0),
                        'current_assets_ratio': latest.get('流动资产合计', 0) / total_assets,
                        'non_current_assets': latest.get('非流动资产合计', 0),
                        'non_current_assets_ratio': latest.get('非流动资产合计', 0) / total_assets,
                    }
                    
            # 负债结构分析
            if all(col in df.columns for col in ['流动负债合计', '非流动负债合计', '负债合计']):
                latest = df.iloc[0]
                total_liabilities = latest.get('负债合计', 0)
                if total_liabilities > 0:
                    analysis['liability_structure'] = {
                        'current_liabilities': latest.get('流动负债合计', 0),
                        'current_liabilities_ratio': latest.get('流动负债合计', 0) / total_liabilities,
                        'non_current_liabilities': latest.get('非流动负债合计', 0),
                        'non_current_liabilities_ratio': latest.get('非流动负债合计', 0) / total_liabilities,
                    }
                    
            # 关键比率
            analysis['key_ratios'] = self._calculate_balance_sheet_ratios(df)
            
            # 评估
            analysis['assessment'] = self._assess_balance_sheet(analysis['key_ratios'])
            
            logger.info("资产负债表分析完成")
            return analysis
            
        except Exception as e:
            logger.error(f"资产负债表分析失败: {e}")
            return {'error': str(e)}
            
    def _analyze_income_statement(self, data: List[Dict]) -> Dict[str, Any]:
        """
        分析利润表
        
        Args:
            data: 利润表数据
            
        Returns:
            分析结果
        """
        logger.info("分析利润表...")
        
        if not data:
            return {'error': '无数据'}
            
        try:
            df = pd.DataFrame(data)
            recent_data = df.head(20)
            
            analysis = {
                'revenue_trend': [],
                'profit_trend': [],
                'margin_analysis': {},
                'key_ratios': {},
                'growth_analysis': {},
                'assessment': {},
            }
            
            # 营收趋势
            if '营业总收入' in df.columns:
                revenue = recent_data[['报告期', '营业总收入']].head(10)
                analysis['revenue_trend'] = revenue.to_dict('records')
                
            # 利润趋势
            if '净利润' in df.columns:
                profit = recent_data[['报告期', '净利润']].head(10)
                analysis['profit_trend'] = profit.to_dict('records')
                
            # 利润率分析
            analysis['margin_analysis'] = self._calculate_margins(df)
            
            # 关键比率
            analysis['key_ratios'] = self._calculate_profitability_ratios(df)
            
            # 增长分析
            analysis['growth_analysis'] = self._analyze_growth(df)
            
            # 评估
            analysis['assessment'] = self._assess_profitability(analysis['key_ratios'], analysis['growth_analysis'])
            
            logger.info("利润表分析完成")
            return analysis
            
        except Exception as e:
            logger.error(f"利润表分析失败: {e}")
            return {'error': str(e)}
            
    def _analyze_cash_flow(self, data: List[Dict]) -> Dict[str, Any]:
        """
        分析现金流量表
        
        Args:
            data: 现金流量表数据
            
        Returns:
            分析结果
        """
        logger.info("分析现金流量表...")
        
        if not data:
            return {'error': '无数据'}
            
        try:
            df = pd.DataFrame(data)
            recent_data = df.head(20)
            
            analysis = {
                'operating_cf_trend': [],
                'investing_cf_trend': [],
                'financing_cf_trend': [],
                'quality_analysis': {},
                'key_ratios': {},
                'assessment': {},
            }
            
            # 经营现金流趋势
            if '经营活动产生的现金流量净额' in df.columns:
                ocf = recent_data[['报告期', '经营活动产生的现金流量净额']].head(10)
                analysis['operating_cf_trend'] = ocf.to_dict('records')
                
            # 投资现金流趋势
            if '投资活动产生的现金流量净额' in df.columns:
                icf = recent_data[['报告期', '投资活动产生的现金流量净额']].head(10)
                analysis['investing_cf_trend'] = icf.to_dict('records')
                
            # 筹资现金流趋势
            if '筹资活动产生的现金流量净额' in df.columns:
                fcf = recent_data[['报告期', '筹资活动产生的现金流量净额']].head(10)
                analysis['financing_cf_trend'] = fcf.to_dict('records')
                
            # 现金流质量分析
            analysis['quality_analysis'] = self._analyze_cash_flow_quality(df)
            
            # 关键比率
            analysis['key_ratios'] = self._calculate_cash_flow_ratios(df)
            
            # 评估
            analysis['assessment'] = self._assess_cash_flow(analysis['quality_analysis'])
            
            logger.info("现金流量表分析完成")
            return analysis
            
        except Exception as e:
            logger.error(f"现金流量表分析失败: {e}")
            return {'error': str(e)}
            
    def _calculate_balance_sheet_ratios(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算资产负债表关键比率"""
        ratios = {}
        
        try:
            latest = df.iloc[0]
            
            # 资产负债率
            if '负债合计' in df.columns and '资产总计' in df.columns:
                total_assets = latest.get('资产总计', 0)
                total_liabilities = latest.get('负债合计', 0)
                if total_assets > 0:
                    ratios['debt_to_asset'] = total_liabilities / total_assets
                    
            # 流动比率
            if '流动资产合计' in df.columns and '流动负债合计' in df.columns:
                current_assets = latest.get('流动资产合计', 0)
                current_liabilities = latest.get('流动负债合计', 0)
                if current_liabilities > 0:
                    ratios['current_ratio'] = current_assets / current_liabilities
                    
            # 速动比率（简化计算，未扣除存货）
            if '流动资产合计' in df.columns and '流动负债合计' in df.columns:
                current_assets = latest.get('流动资产合计', 0)
                current_liabilities = latest.get('流动负债合计', 0)
                inventory = latest.get('存货', 0)
                if current_liabilities > 0:
                    quick_assets = current_assets - inventory
                    ratios['quick_ratio'] = quick_assets / current_liabilities
                    
        except Exception as e:
            logger.warning(f"计算资产负债表比率失败: {e}")
            
        return ratios
        
    def _calculate_margins(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算利润率"""
        margins = {}
        
        try:
            latest = df.iloc[0]
            
            revenue = latest.get('营业总收入', 0)
            operating_profit = latest.get('营业利润', 0)
            net_profit = latest.get('净利润', 0)
            cost = latest.get('营业成本', 0)
            
            if revenue > 0:
                # 毛利率
                if cost > 0:
                    gross_profit = revenue - cost
                    margins['gross_margin'] = gross_profit / revenue
                    
                # 营业利润率
                margins['operating_margin'] = operating_profit / revenue
                
                # 净利率
                margins['net_margin'] = net_profit / revenue
                
        except Exception as e:
            logger.warning(f"计算利润率失败: {e}")
            
        return margins
        
    def _calculate_profitability_ratios(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算盈利能力比率"""
        ratios = {}
        
        try:
            latest = df.iloc[0]
            
            # ROE (简化计算)
            if '净利润' in df.columns:
                net_profit = latest.get('净利润', 0)
                # 需要股东权益数据，这里简化处理
                ratios['roe_hint'] = '需要股东权益数据计算'
                
        except Exception as e:
            logger.warning(f"计算盈利能力比率失败: {e}")
            
        return ratios
        
    def _analyze_growth(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析增长情况"""
        growth = {}
        
        try:
            if len(df) >= 5:  # 至少5个报告期
                # 营收增长率
                if '营业总收入' in df.columns:
                    revenues = df['营业总收入'].head(5).values
                    if revenues[0] > 0 and revenues[4] > 0:
                        growth['revenue_growth_yoy'] = (revenues[0] - revenues[4]) / abs(revenues[4])
                        
                # 净利润增长率
                if '净利润' in df.columns:
                    profits = df['净利润'].head(5).values
                    if profits[0] > 0 and profits[4] > 0:
                        growth['profit_growth_yoy'] = (profits[0] - profits[4]) / abs(profits[4])
                        
        except Exception as e:
            logger.warning(f"增长分析失败: {e}")
            
        return growth
        
    def _analyze_cash_flow_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析现金流质量"""
        quality = {}
        
        try:
            latest = df.iloc[0]
            
            # 经营现金流与净利润的比值
            if '经营活动产生的现金流量净额' in df.columns and '净利润' in df.columns:
                ocf = latest.get('经营活动产生的现金流量净额', 0)
                net_profit = latest.get('净利润', 0)
                if net_profit > 0:
                    quality['ocf_to_net_profit'] = ocf / net_profit
                    quality['quality_score'] = 1 if ocf > net_profit else 0
                    
            # 自由现金流（简化计算）
            if '经营活动产生的现金流量净额' in df.columns and '购建固定资产、无形资产和其他长期资产支付的现金' in df.columns:
                ocf = latest.get('经营活动产生的现金流量净额', 0)
                capex = latest.get('购建固定资产、无形资产和其他长期资产支付的现金', 0)
                quality['free_cash_flow'] = ocf - capex
                
        except Exception as e:
            logger.warning(f"现金流质量分析失败: {e}")
            
        return quality
        
    def _calculate_cash_flow_ratios(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算现金流比率"""
        ratios = {}
        
        try:
            latest = df.iloc[0]
            
            # 现金流覆盖率
            if '经营活动产生的现金流量净额' in df.columns and '流动负债合计' in df.columns:
                ocf = latest.get('经营活动产生的现金流量净额', 0)
                current_liabilities = latest.get('流动负债合计', 0)
                if current_liabilities > 0:
                    ratios['ocf_to_current_liabilities'] = ocf / current_liabilities
                    
        except Exception as e:
            logger.warning(f"计算现金流比率失败: {e}")
            
        return ratios
        
    def _assess_balance_sheet(self, ratios: Dict[str, Any]) -> Dict[str, str]:
        """评估资产负债表"""
        assessment = {}
        
        # 资产负债率评估
        debt_ratio = ratios.get('debt_to_asset', 0)
        if debt_ratio < 0.4:
            assessment['debt_level'] = '低杠杆，财务稳健'
        elif debt_ratio < 0.6:
            assessment['debt_level'] = '中等杠杆，财务状况良好'
        else:
            assessment['debt_level'] = '高杠杆，需关注偿债风险'
            
        # 流动比率评估
        current_ratio = ratios.get('current_ratio', 0)
        if current_ratio >= 2:
            assessment['liquidity'] = '流动性充裕'
        elif current_ratio >= 1:
            assessment['liquidity'] = '流动性良好'
        else:
            assessment['liquidity'] = '流动性紧张，需关注短期偿债能力'
            
        return assessment
        
    def _assess_profitability(self, ratios: Dict[str, Any], growth: Dict[str, Any]) -> Dict[str, str]:
        """评估盈利能力"""
        assessment = {}
        
        # 增长评估
        revenue_growth = growth.get('revenue_growth_yoy', 0)
        if revenue_growth > 0.2:
            assessment['growth'] = '高速增长'
        elif revenue_growth > 0.1:
            assessment['growth'] = '稳健增长'
        elif revenue_growth > 0:
            assessment['growth'] = '低速增长'
        else:
            assessment['growth'] = '负增长，需关注'
            
        return assessment
        
    def _assess_cash_flow(self, quality: Dict[str, Any]) -> Dict[str, str]:
        """评估现金流"""
        assessment = {}
        
        # 现金流质量评估
        ocf_to_np = quality.get('ocf_to_net_profit', 0)
        if ocf_to_np > 1.2:
            assessment['cash_quality'] = '现金流质量优秀，盈利含金量高'
        elif ocf_to_np > 0.8:
            assessment['cash_quality'] = '现金流质量良好'
        else:
            assessment['cash_quality'] = '现金流质量需关注，可能存在应收账款问题'
            
        return assessment
        
    def _generate_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合摘要"""
        summary = {
            'strengths': [],
            'weaknesses': [],
            'key_metrics': {},
        }
        
        # 提取关键指标
        bs_ratios = result.get('balance_sheet_analysis', {}).get('key_ratios', {})
        is_margins = result.get('income_statement_analysis', {}).get('margin_analysis', {})
        cf_quality = result.get('cash_flow_analysis', {}).get('quality_analysis', {})
        
        summary['key_metrics'] = {
            'debt_to_asset': bs_ratios.get('debt_to_asset', 'N/A'),
            'current_ratio': bs_ratios.get('current_ratio', 'N/A'),
            'gross_margin': is_margins.get('gross_margin', 'N/A'),
            'net_margin': is_margins.get('net_margin', 'N/A'),
            'ocf_to_net_profit': cf_quality.get('ocf_to_net_profit', 'N/A'),
        }
        
        # 识别优势和劣势
        bs_assessment = result.get('balance_sheet_analysis', {}).get('assessment', {})
        is_assessment = result.get('income_statement_analysis', {}).get('assessment', {})
        cf_assessment = result.get('cash_flow_analysis', {}).get('assessment', {})
        
        for key, value in {**bs_assessment, **is_assessment, **cf_assessment}.items():
            if '优秀' in value or '充裕' in value or '稳健' in value:
                summary['strengths'].append(value)
            elif '关注' in value or '紧张' in value or '风险' in value:
                summary['weaknesses'].append(value)
                
        return summary
