#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCF估值模型 - 现金流折现估值
参考Claude Financial Services的估值建模最佳实践
"""

import logging
from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class DCFModel:
    """DCF估值模型"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化
        
        Args:
            config: 系统配置
        """
        self.config = config
        self.default_forecast_years = config['modules']['valuation']['dcf'].get('default_forecast_years', 5)
        self.default_growth_rate = config['modules']['valuation']['dcf'].get('default_growth_rate', 0.05)
        self.default_wacc = config['modules']['valuation']['dcf'].get('default_wacc', 0.10)
        
    def valuate(
        self,
        stock_code: str,
        financial_data: Dict[str, Any],
        growth_rate: Optional[float] = None,
        wacc: Optional[float] = None,
        forecast_years: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        DCF估值
        
        Args:
            stock_code: 股票代码
            financial_data: 财务数据
            growth_rate: 永续增长率
            wacc: 加权平均资本成本
            forecast_years: 预测期年数
            
        Returns:
            估值结果
        """
        logger.info(f"DCF估值: {stock_code}")
        
        # 使用配置默认值
        if growth_rate is None:
            growth_rate = self.default_growth_rate
        if wacc is None:
            wacc = self.default_wacc
        if forecast_years is None:
            forecast_years = self.default_forecast_years
            
        result = {
            'stock_code': stock_code,
            'valuation_time': datetime.now().isoformat(),
            'assumptions': {
                'growth_rate': growth_rate,
                'wacc': wacc,
                'forecast_years': forecast_years,
            },
            'enterprise_value': 0,
            'equity_value': 0,
            'per_share_value': 0,
            'sensitivity_analysis': {},
            'assessment': '',
        }
        
        try:
            # 提取财务数据
            income_data = financial_data.get('financial_analysis', {}).get('income_statement_analysis', {})
            balance_data = financial_data.get('financial_analysis', {}).get('balance_sheet_analysis', {})
            cash_flow_data = financial_data.get('financial_analysis', {}).get('cash_flow_analysis', {})
            
            # 获取基准数据
            base_fcf = self._estimate_base_fcf(income_data, cash_flow_data)
            
            if base_fcf <= 0:
                logger.warning("基准自由现金流为负，DCF估值可能不准确")
                result['assessment'] = '基准自由现金流为负，DCF估值参考价值有限'
                return result
                
            # 预测未来现金流
            forecasted_fcf = self._forecast_fcf(base_fcf, growth_rate, forecast_years)
            
            # 计算企业价值
            enterprise_value = self._calculate_enterprise_value(forecasted_fcf, wacc, growth_rate)
            
            # 计算股权价值
            net_debt = self._estimate_net_debt(balance_data)
            equity_value = enterprise_value - net_debt
            
            # 计算每股价值
            shares_outstanding = self._estimate_shares_outstanding(financial_data)
            per_share_value = equity_value / shares_outstanding if shares_outstanding > 0 else 0
            
            result.update({
                'base_fcf': base_fcf,
                'forecasted_fcf': forecasted_fcf,
                'net_debt': net_debt,
                'shares_outstanding': shares_outstanding,
                'enterprise_value': enterprise_value,
                'equity_value': equity_value,
                'per_share_value': per_share_value,
            })
            
            # 敏感性分析
            if self.config['modules']['valuation']['dcf'].get('sensitivity_enabled', True):
                result['sensitivity_analysis'] = self._perform_sensitivity_analysis(
                    base_fcf, growth_rate, wacc, forecast_years, net_debt, shares_outstanding
                )
                
            # 评估
            result['assessment'] = self._assess_valuation(result)
            
            logger.info(f"DCF估值完成: 每股价值 {per_share_value:.2f} 元")
            
        except Exception as e:
            logger.error(f"DCF估值失败: {e}")
            result['error'] = str(e)
            
        return result
        
    def _estimate_base_fcf(self, income_data: Dict, cash_flow_data: Dict) -> float:
        """
        估算基准自由现金流
        
        Args:
            income_data: 利润表数据
            cash_flow_data: 现金流数据
            
        Returns:
            基准自由现金流
        """
        # 优先使用实际自由现金流
        quality_analysis = cash_flow_data.get('quality_analysis', {})
        if 'free_cash_flow' in quality_analysis:
            return quality_analysis['free_cash_flow']
            
        # 否则使用经营现金流作为近似
        ocf_trend = cash_flow_data.get('operating_cf_trend', [])
        if ocf_trend and len(ocf_trend) > 0:
            # 取最近一年的经营现金流
            latest_ocf = ocf_trend[0].get('经营活动产生的现金流量净额', 0)
            return latest_ocf
            
        return 0
        
    def _forecast_fcf(
        self,
        base_fcf: float,
        growth_rate: float,
        years: int
    ) -> List[float]:
        """
        预测未来自由现金流
        
        Args:
            base_fcf: 基准自由现金流
            growth_rate: 增长率
            years: 预测年数
            
        Returns:
            预测的自由现金流列表
        """
        forecasted = []
        current_fcf = base_fcf
        
        for i in range(years):
            # 假设增长率逐年递减
            year_growth = growth_rate * (1 - i * 0.1)  # 每年递减10%
            current_fcf = current_fcf * (1 + year_growth)
            forecasted.append(current_fcf)
            
        return forecasted
        
    def _calculate_enterprise_value(
        self,
        forecasted_fcf: List[float],
        wacc: float,
        terminal_growth: float
    ) -> float:
        """
        计算企业价值
        
        Args:
            forecasted_fcf: 预测的自由现金流
            wacc: 加权平均资本成本
            terminal_growth: 永续增长率
            
        Returns:
            企业价值
        """
        # 计算预测期现金流的现值
        pv_forecast = 0
        for i, fcf in enumerate(forecasted_fcf):
            pv_forecast += fcf / ((1 + wacc) ** (i + 1))
            
        # 计算终值
        last_fcf = forecasted_fcf[-1] if forecasted_fcf else 0
        terminal_value = last_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
        
        # 终值的现值
        pv_terminal = terminal_value / ((1 + wacc) ** len(forecasted_fcf))
        
        # 企业价值
        enterprise_value = pv_forecast + pv_terminal
        
        return enterprise_value
        
    def _estimate_net_debt(self, balance_data: Dict) -> float:
        """
        估算净债务
        
        Args:
            balance_data: 资产负债表数据
            
        Returns:
            净债务
        """
        # 简化处理：使用负债合计作为净债务的近似
        # 实际应该计算：有息负债 - 现金及等价物
        key_ratios = balance_data.get('key_ratios', {})
        
        # 这里简化处理，返回0
        # 实际应该从资产负债表提取详细数据
        return 0
        
    def _estimate_shares_outstanding(self, financial_data: Dict) -> float:
        """
        估算流通股数
        
        Args:
            financial_data: 财务数据
            
        Returns:
            流通股数（亿股）
        """
        # 从公司信息获取
        company_info = financial_data.get('data_fetch', {}).get('api_data', {}).get('company_info', {})
        
        # 简化处理：假设10亿股
        # 实际应该从数据中提取
        return 10.0
        
    def _perform_sensitivity_analysis(
        self,
        base_fcf: float,
        base_growth: float,
        base_wacc: float,
        forecast_years: int,
        net_debt: float,
        shares: float
    ) -> Dict[str, Any]:
        """
        执行敏感性分析
        
        Args:
            base_fcf: 基准自由现金流
            base_growth: 基准增长率
            base_wacc: 基准WACC
            forecast_years: 预测年数
            net_debt: 净债务
            shares: 流通股数
            
        Returns:
            敏感性分析结果
        """
        logger.info("执行敏感性分析...")
        
        # 定义变化范围
        growth_range = [base_growth - 0.02, base_growth - 0.01, base_growth, 
                       base_growth + 0.01, base_growth + 0.02]
        wacc_range = [base_wacc - 0.02, base_wacc - 0.01, base_wacc, 
                     base_wacc + 0.01, base_wacc + 0.02]
                     
        sensitivity_matrix = []
        
        for growth in growth_range:
            row = []
            for wacc in wacc_range:
                # 计算该组合下的估值
                forecasted_fcf = self._forecast_fcf(base_fcf, growth, forecast_years)
                ev = self._calculate_enterprise_value(forecasted_fcf, wacc, growth)
                equity = ev - net_debt
                per_share = equity / shares if shares > 0 else 0
                row.append(per_share)
            sensitivity_matrix.append(row)
            
        return {
            'growth_range': growth_range,
            'wacc_range': wacc_range,
            'matrix': sensitivity_matrix,
        }
        
    def _assess_valuation(self, result: Dict) -> str:
        """
        评估估值结果
        
        Args:
            result: 估值结果
            
        Returns:
            评估说明
        """
        per_share_value = result.get('per_share_value', 0)
        
        if per_share_value <= 0:
            return '估值结果为负，公司可能处于困境或模型假设需要调整'
        elif per_share_value < 10:
            return '估值较低，需结合行业和公司具体情况判断'
        elif per_share_value < 50:
            return '估值处于合理区间'
        else:
            return '估值较高，需谨慎评估假设合理性'
            
    def calculate_wacc(
        self,
        risk_free_rate: float = 0.03,
        market_risk_premium: float = 0.07,
        beta: float = 1.0,
        cost_of_debt: float = 0.05,
        tax_rate: float = 0.25,
        debt_ratio: float = 0.3
    ) -> float:
        """
        计算加权平均资本成本（WACC）
        
        Args:
            risk_free_rate: 无风险利率
            market_risk_premium: 市场风险溢价
            beta: 贝塔系数
            cost_of_debt: 债务成本
            tax_rate: 税率
            debt_ratio: 债务比率
            
        Returns:
            WACC
        """
        # 股权成本（CAPM）
        cost_of_equity = risk_free_rate + beta * market_risk_premium
        
        # 税后债务成本
        after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
        
        # WACC
        equity_ratio = 1 - debt_ratio
        wacc = equity_ratio * cost_of_equity + debt_ratio * after_tax_cost_of_debt
        
        logger.info(f"计算WACC: {wacc:.4f}")
        return wacc
