#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竞争格局分析模块 - 基于Claude Financial Services框架
包括：Porter五力分析、护城河评估（Claude框架）、竞争地位分析、SWOT分析
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class CompetitiveAnalyzer:
    """竞争格局分析器 - Claude框架"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化竞争格局分析器
        
        Args:
            config: 系统配置
        """
        self.config = config
        
        # 加载行业关键指标配置
        self.industry_metrics = self._load_industry_metrics()
        
    def _load_industry_metrics(self) -> Dict[str, Any]:
        """加载行业关键指标配置"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'industry_metrics.yaml'
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"加载行业指标配置失败: {e}")
        
        return {}
        
    def analyze(
        self,
        stock_code: str,
        company_name: str = None,
        industry_data: Dict[str, Any] = None,
        financial_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        竞争格局分析主入口 - Claude框架
        
        Args:
            stock_code: 股票代码
            company_name: 公司名称
            industry_data: 行业数据
            financial_data: 财务数据
            
        Returns:
            竞争格局分析结果
        """
        logger.info(f"开始竞争格局分析（Claude框架）: {stock_code}")
        
        result = {
            'stock_code': stock_code,
            'company_name': company_name,
            'competitive_analysis': {},
        }
        
        try:
            # Step 1: 目标公司概况（Claude Step 3）
            logger.info("分析目标公司概况...")
            company_profile = self._analyze_company_profile(
                stock_code, company_name, financial_data
            )
            result['competitive_analysis']['company_profile'] = company_profile
            
            # Step 2: 竞争对手映射（Claude Step 4）
            logger.info("映射竞争对手...")
            competitor_mapping = self._map_competitors(
                stock_code, industry_data, financial_data
            )
            result['competitive_analysis']['competitor_mapping'] = competitor_mapping
            
            # Step 3: Porter五力分析
            logger.info("执行Porter五力分析...")
            porter_five_forces = self._analyze_porter_five_forces(
                stock_code, company_name, industry_data, financial_data
            )
            result['competitive_analysis']['porter_five_forces'] = porter_five_forces
            
            # Step 4: 护城河评估（Claude核心框架）
            logger.info("评估护城河（Claude框架）...")
            moat_assessment = self._assess_moat_claude(
                stock_code, company_name, financial_data
            )
            result['competitive_analysis']['moat_assessment'] = moat_assessment
            
            # Step 5: 竞争定位可视化（Claude Step 5）
            logger.info("分析竞争定位...")
            positioning = self._analyze_positioning(
                stock_code, company_name, industry_data, financial_data
            )
            result['competitive_analysis']['positioning'] = positioning
            
            # Step 6: 比较分析（Claude Step 7）
            logger.info("执行比较分析...")
            comparative_analysis = self._analyze_comparative(
                stock_code, company_name, industry_data, financial_data
            )
            result['competitive_analysis']['comparative'] = comparative_analysis
            
            # Step 7: SWOT分析
            logger.info("执行SWOT分析...")
            swot = self._analyze_swot(
                stock_code, company_name, financial_data,
                porter_five_forces, moat_assessment
            )
            result['competitive_analysis']['swot'] = swot
            
            # Step 8: 战略综合（Claude Step 9）
            logger.info("生成战略综合...")
            synthesis = self._generate_synthesis(
                result['competitive_analysis']
            )
            result['competitive_analysis']['synthesis'] = synthesis
            
            logger.info("竞争格局分析完成")
            
        except Exception as e:
            logger.error(f"竞争格局分析失败: {e}")
            result['error'] = str(e)
            
        return result
    
    def _analyze_company_profile(
        self,
        stock_code: str,
        company_name: str,
        financial_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        目标公司概况（Claude Step 3）
        
        包括：关键指标表、多业务分部（如有）
        """
        profile = {
            'key_metrics': {},
            'segments': None,
        }
        
        if not financial_data:
            return profile
        
        # 提取关键指标
        income_statement = financial_data.get('income_statement', {})
        balance_sheet = financial_data.get('balance_sheet', {})
        
        if income_statement:
            revenues = income_statement.get('revenue', [])
            if revenues:
                profile['key_metrics']['Revenue'] = f"${revenues[-1]/1e8:.2f}B" if revenues[-1] else 'N/A'
            
            growth_rates = income_statement.get('revenue_growth', [])
            if growth_rates:
                profile['key_metrics']['Growth'] = f"+{growth_rates[-1]:.1f}% YoY" if growth_rates[-1] else 'N/A'
            
            gross_margins = income_statement.get('gross_margin', [])
            if gross_margins:
                profile['key_metrics']['Gross Margin'] = f"{gross_margins[-1]:.1f}%"
            
            net_margins = income_statement.get('net_margin', [])
            if net_margins:
                profile['key_metrics']['Profitability'] = f"${net_margins[-1]*revenues[-1]/100/1e6:.0f}M Net Income" if revenues and net_margins else 'N/A'
        
        # TODO: 添加业务分部分析
        
        return profile
    
    def _map_competitors(
        self,
        stock_code: str,
        industry_data: Dict[str, Any],
        financial_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        竞争对手映射（Claude Step 4）
        
        分组方式：商业模式/细分市场/竞争姿态/起源
        """
        mapping = {
            'grouping_method': None,
            'competitor_groups': [],
        }
        
        if not industry_data:
            return mapping
        
        competitive_landscape = industry_data.get('competitive_landscape', {})
        key_players = competitive_landscape.get('key_players', [])
        
        if key_players:
            # 按规模分组（Tier）
            tier1 = [p for p in key_players if float(p.get('market_share', '0%').replace('%', '')) > 10]
            tier2 = [p for p in key_players if 5 < float(p.get('market_share', '0%').replace('%', '')) <= 10]
            tier3 = [p for p in key_players if float(p.get('market_share', '0%').replace('%', '')) <= 5]
            
            mapping['grouping_method'] = 'by_scale'
            mapping['competitor_groups'] = [
                {'tier': 'Tier 1 (Leaders)', 'companies': [p['name'] for p in tier1]},
                {'tier': 'Tier 2 (Challengers)', 'companies': [p['name'] for p in tier2]},
                {'tier': 'Tier 3 (Niche Players)', 'companies': [p['name'] for p in tier3]},
            ]
        
        return mapping
    
    def _analyze_porter_five_forces(
        self,
        stock_code: str,
        company_name: str,
        industry_data: Dict[str, Any],
        financial_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Porter五力分析
        """
        porter = {
            'supplier_power': {},
            'buyer_power': {},
            'competitive_rivalry': {},
            'threat_of_substitution': {},
            'threat_of_new_entry': {},
            'overall_assessment': '',
        }
        
        # 供应商议价能力
        porter['supplier_power'] = {
            'level': '中等',
            'factors': ['供应商集中度', '原材料价格波动性', '替代供应商可获得性'],
            'analysis': '供应商议价能力中等，主要受原材料价格波动影响。',
        }
        
        # 买方议价能力
        porter['buyer_power'] = {
            'level': '中等',
            'factors': ['客户集中度', '产品差异化程度', '客户转换成本'],
            'analysis': '买方议价能力中等，产品差异化和服务质量是关键。',
        }
        
        # 行业内竞争
        if industry_data:
            competitive_landscape = industry_data.get('competitive_landscape', {})
            concentration = competitive_landscape.get('market_concentration', {})
            
            porter['competitive_rivalry'] = {
                'level': concentration.get('competition_intensity', '中等'),
                'factors': ['竞争对手数量', '行业增长率', '产品差异化程度'],
                'analysis': f"行业内竞争{concentration.get('competition_intensity', '中等')}，市场集中度{concentration.get('type', '适中')}。",
            }
        
        # 替代品威胁
        porter['threat_of_substitution'] = {
            'level': '低',
            'factors': ['替代品性价比', '客户转换成本', '替代品技术发展'],
            'analysis': '替代品威胁相对较低，产品具有较强的不可替代性。',
        }
        
        # 新进入者威胁
        porter['threat_of_new_entry'] = {
            'level': '中等',
            'factors': ['资本密集度', '规模经济效应', '品牌忠诚度', '政策准入壁垒'],
            'analysis': '新进入者威胁中等，存在一定的资本和技术壁垒。',
        }
        
        # 总体评估
        porter['overall_assessment'] = self._generate_porter_summary(porter)
        
        return porter
    
    def _assess_moat_claude(
        self,
        stock_code: str,
        company_name: str,
        financial_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        护城河评估 - Claude框架（核心）
        
        评估四大护城河：
        1. 网络效应（Network Effects）
        2. 转换成本（Switching Costs）
        3. 规模经济（Scale Economies）
        4. 无形资产（Intangible Assets）
        """
        moat = {
            'ratings': {},
            'durable_advantages': [],
            'structural_vulnerabilities': [],
            'trajectory': None,
            'overall_strength': None,
        }
        
        # 获取护城河评估标准
        moat_categories = {}
        if self.industry_metrics:
            moat_categories = self.industry_metrics.get('moat_categories', {})
        
        # 1. 网络效应评估
        network_effects = self._assess_network_effects(financial_data, moat_categories)
        moat['ratings']['network_effects'] = network_effects
        
        # 2. 转换成本评估
        switching_costs = self._assess_switching_costs(financial_data, moat_categories)
        moat['ratings']['switching_costs'] = switching_costs
        
        # 3. 规模经济评估
        scale_economies = self._assess_scale_economies(financial_data, moat_categories)
        moat['ratings']['scale_economies'] = scale_economies
        
        # 4. 无形资产评估
        intangible_assets = self._assess_intangible_assets(financial_data, moat_categories)
        moat['ratings']['intangible_assets'] = intangible_assets
        
        # 综合评估
        strong_count = sum(1 for r in moat['ratings'].values() if r.get('rating') == 'Strong')
        moderate_count = sum(1 for r in moat['ratings'].values() if r.get('rating') == 'Moderate')
        
        if strong_count >= 2:
            moat['overall_strength'] = 'Wide Moat'
        elif strong_count >= 1 or moderate_count >= 2:
            moat['overall_strength'] = 'Narrow Moat'
        else:
            moat['overall_strength'] = 'No Moat'
        
        # 持久优势
        for category, rating in moat['ratings'].items():
            if rating.get('rating') in ['Strong', 'Moderate']:
                moat['durable_advantages'].append({
                    'category': category,
                    'evidence': rating.get('evidence', []),
                })
        
        # 结构性弱点
        for category, rating in moat['ratings'].items():
            if rating.get('rating') == 'Weak':
                moat['structural_vulnerabilities'].append(category)
        
        # 轨迹判断
        moat['trajectory'] = self._assess_moat_trajectory(financial_data, moat['ratings'])
        
        return moat
    
    def _assess_network_effects(
        self,
        financial_data: Dict[str, Any],
        moat_categories: Dict[str, Any],
    ) -> Dict[str, Any]:
        """评估网络效应"""
        result = {
            'rating': 'Weak',
            'evidence': [],
            'analysis': '',
        }
        
        # 网络效应通常需要业务数据判断
        # 这里基于财务数据进行简化评估
        
        # 检查收入增长与用户增长的相关性（如果有数据）
        if financial_data:
            income_statement = financial_data.get('income_statement', {})
            revenues = income_statement.get('revenue', [])
            
            if revenues and len(revenues) >= 3:
                # 检查增长率是否加速（网络效应的特征）
                growth_rates = []
                for i in range(1, len(revenues)):
                    if revenues[i-1] > 0:
                        growth = (revenues[i] - revenues[i-1]) / revenues[i-1]
                        growth_rates.append(growth)
                
                if growth_rates and len(growth_rates) >= 2:
                    # 增长率递增
                    if growth_rates[-1] > growth_rates[-2]:
                        result['rating'] = 'Moderate'
                        result['evidence'].append('收入增长加速，可能存在网络效应')
        
        result['analysis'] = '网络效应评估需要更多业务数据（用户数、活跃度等）。'
        
        return result
    
    def _assess_switching_costs(
        self,
        financial_data: Dict[str, Any],
        moat_categories: Dict[str, Any],
    ) -> Dict[str, Any]:
        """评估转换成本"""
        result = {
            'rating': 'Weak',
            'evidence': [],
            'analysis': '',
        }
        
        if financial_data:
            # 检查客户留存率（如果有）
            # 检查收入稳定性
            
            income_statement = financial_data.get('income_statement', {})
            revenues = income_statement.get('revenue', [])
            
            if revenues and len(revenues) >= 3:
                # 收入稳定性高可能意味着转换成本高
                revenue_std = np.std(revenues) / np.mean(revenues) if np.mean(revenues) > 0 else 1
                
                if revenue_std < 0.1:
                    result['rating'] = 'Moderate'
                    result['evidence'].append('收入稳定性高，可能存在转换成本')
        
        result['analysis'] = '转换成本评估需要更多客户数据（留存率、流失率等）。'
        
        return result
    
    def _assess_scale_economies(
        self,
        financial_data: Dict[str, Any],
        moat_categories: Dict[str, Any],
    ) -> Dict[str, Any]:
        """评估规模经济"""
        result = {
            'rating': 'Weak',
            'evidence': [],
            'analysis': '',
        }
        
        if financial_data:
            income_statement = financial_data.get('income_statement', {})
            
            # 检查毛利率和营业利润率
            gross_margins = income_statement.get('gross_margin', [])
            operating_margins = income_statement.get('operating_margin', [])
            
            if gross_margins and operating_margins:
                avg_gross_margin = np.mean(gross_margins)
                avg_operating_margin = np.mean(operating_margins)
                
                # 高毛利率 + 高营业利润率 = 规模经济
                if avg_gross_margin > 30 and avg_operating_margin > 15:
                    result['rating'] = 'Strong'
                    result['evidence'].append(f'毛利率{avg_gross_margin:.1f}%，体现成本优势')
                    result['evidence'].append(f'营业利润率{avg_operating_margin:.1f}%，体现规模效应')
                elif avg_gross_margin > 20 or avg_operating_margin > 10:
                    result['rating'] = 'Moderate'
                    result['evidence'].append('存在一定的规模经济优势')
        
        result['analysis'] = f"规模经济评估：{result['rating']}。"
        
        return result
    
    def _assess_intangible_assets(
        self,
        financial_data: Dict[str, Any],
        moat_categories: Dict[str, Any],
    ) -> Dict[str, Any]:
        """评估无形资产"""
        result = {
            'rating': 'Weak',
            'evidence': [],
            'analysis': '',
        }
        
        if financial_data:
            income_statement = financial_data.get('income_statement', {})
            
            # 检查毛利率（品牌溢价）
            gross_margins = income_statement.get('gross_margin', [])
            
            if gross_margins:
                avg_gross_margin = np.mean(gross_margins)
                
                # 高毛利率可能意味着品牌溢价
                if avg_gross_margin > 40:
                    result['rating'] = 'Strong'
                    result['evidence'].append(f'毛利率{avg_gross_margin:.1f}%，体现品牌溢价能力')
                elif avg_gross_margin > 30:
                    result['rating'] = 'Moderate'
                    result['evidence'].append('存在一定的品牌价值')
        
        result['analysis'] = f"无形资产评估：{result['rating']}。"
        
        return result
    
    def _assess_moat_trajectory(
        self,
        financial_data: Dict[str, Any],
        ratings: Dict[str, Any],
    ) -> str:
        """评估护城河轨迹"""
        # 基于财务趋势判断护城河是在扩大还是缩小
        
        if not financial_data:
            return 'Stable'
        
        income_statement = financial_data.get('income_statement', {})
        gross_margins = income_statement.get('gross_margin', [])
        operating_margins = income_statement.get('operating_margin', [])
        
        if gross_margins and len(gross_margins) >= 2:
            if gross_margins[-1] > gross_margins[0]:
                return 'Expanding'
            elif gross_margins[-1] < gross_margins[0]:
                return 'Narrowing'
        
        return 'Stable'
    
    def _analyze_positioning(
        self,
        stock_code: str,
        company_name: str,
        industry_data: Dict[str, Any],
        financial_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        竞争定位可视化（Claude Step 5）
        
        包括：2x2矩阵、雷达图、层级图等
        """
        positioning = {
            'visualization_type': None,
            'dimensions': [],
            'position': None,
            'analysis': '',
        }
        
        if industry_data:
            competitive_landscape = industry_data.get('competitive_landscape', {})
            target_position = competitive_landscape.get('target_company_position', {})
            
            if target_position:
                positioning['position'] = {
                    'tier': target_position.get('tier', 'N/A'),
                    'ranking': target_position.get('ranking', 'N/A'),
                    'market_share': target_position.get('market_share', 'N/A'),
                }
                
                # 推荐可视化类型
                if target_position.get('tier') == 'Tier 1':
                    positioning['visualization_type'] = '2x2 Matrix (Scale vs Growth)'
                    positioning['dimensions'] = ['Market Share', 'Growth Rate']
                else:
                    positioning['visualization_type'] = 'Radar Chart (Multi-factor)'
                    positioning['dimensions'] = ['Scale', 'Growth', 'Margins', 'Innovation']
        
        positioning['analysis'] = f"竞争定位：{positioning['position']['tier'] if positioning['position'] else 'N/A'}。"
        
        return positioning
    
    def _analyze_comparative(
        self,
        stock_code: str,
        company_name: str,
        industry_data: Dict[str, Any],
        financial_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        比较分析（Claude Step 7）
        
        多维度对比：规模、增长、利润率等
        """
        comparative = {
            'dimensions': [],
            'comparison_table': None,
        }
        
        # 定义比较维度
        comparative['dimensions'] = [
            {'name': 'Scale', 'description': '市场规模', 'metric': 'Market Cap'},
            {'name': 'Growth', 'description': '增长速度', 'metric': 'Revenue Growth'},
            {'name': 'Margins', 'description': '盈利能力', 'metric': 'Gross Margin'},
            {'name': 'Profitability', 'description': '利润水平', 'metric': 'Net Margin'},
        ]
        
        # TODO: 实现多公司对比表
        
        return comparative
    
    def _analyze_swot(
        self,
        stock_code: str,
        company_name: str,
        financial_data: Dict[str, Any],
        porter_five_forces: Dict[str, Any],
        moat_assessment: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        SWOT分析
        """
        swot = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': [],
        }
        
        # 优势 - 从护城河评估提取
        for advantage in moat_assessment.get('durable_advantages', []):
            swot['strengths'].append(f"{advantage['category']}: {', '.join(advantage['evidence'])}")
        
        # 劣势 - 从结构性弱点提取
        for vulnerability in moat_assessment.get('structural_vulnerabilities', []):
            swot['weaknesses'].append(f"{vulnerability}护城河较弱")
        
        # 机会
        swot['opportunities'] = [
            '市场份额提升',
            '新产品/新市场拓展',
            '行业整合机遇',
        ]
        
        # 威胁 - 从Porter五力提取
        for force_name, force_data in porter_five_forces.items():
            if force_name == 'overall_assessment':
                continue
            if isinstance(force_data, dict) and force_data.get('level') in ['高', '强']:
                swot['threats'].append(f"{force_data.get('analysis', '')}")
        
        return swot
    
    def _generate_synthesis(
        self,
        competitive_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        战略综合（Claude Step 9）
        
        包括：护城河评估、持久优势、结构性弱点、当前状态vs轨迹
        """
        synthesis = {
            'moat_summary': None,
            'durable_advantages': [],
            'structural_vulnerabilities': [],
            'current_state_vs_trajectory': None,
            'investment_scenarios': None,
        }
        
        moat_assessment = competitive_analysis.get('moat_assessment', {})
        
        # 护城河总结
        synthesis['moat_summary'] = {
            'overall_strength': moat_assessment.get('overall_strength', 'Unknown'),
            'trajectory': moat_assessment.get('trajectory', 'Unknown'),
        }
        
        # 持久优势
        synthesis['durable_advantages'] = moat_assessment.get('durable_advantages', [])
        
        # 结构性弱点
        synthesis['structural_vulnerabilities'] = moat_assessment.get('structural_vulnerabilities', [])
        
        # 当前状态vs轨迹
        trajectory = moat_assessment.get('trajectory', 'Stable')
        overall_strength = moat_assessment.get('overall_strength', 'No Moat')
        
        if trajectory == 'Expanding':
            synthesis['current_state_vs_trajectory'] = f"{overall_strength}，护城河正在扩大"
        elif trajectory == 'Narrowing':
            synthesis['current_state_vs_trajectory'] = f"{overall_strength}，护城河正在缩小，需警惕"
        else:
            synthesis['current_state_vs_trajectory'] = f"{overall_strength}，护城河稳定"
        
        # 投资场景（如果是投资分析）
        synthesis['investment_scenarios'] = {
            'bull': {
                'probability': '30%',
                'driver': '市场份额提升，护城河扩大',
            },
            'base': {
                'probability': '50%',
                'driver': '当前趋势延续',
            },
            'bear': {
                'probability': '20%',
                'driver': '竞争加剧，护城河缩小',
            },
        }
        
        return synthesis
    
    def _generate_porter_summary(self, porter: Dict[str, Any]) -> str:
        """生成Porter五力分析总结"""
        summary_parts = []
        
        for force_name, force_data in porter.items():
            if force_name == 'overall_assessment':
                continue
            if isinstance(force_data, dict):
                level = force_data.get('level', '未知')
                summary_parts.append(f"{force_name}: {level}")
        
        return '；'.join(summary_parts)
