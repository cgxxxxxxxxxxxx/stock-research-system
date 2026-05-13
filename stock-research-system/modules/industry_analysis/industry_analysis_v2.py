#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业分析模块 - 基于Claude Financial Services框架
包括：行业关键指标、市场规模、竞争格局、发展趋势、生命周期分析
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class IndustryAnalyzer:
    """行业分析器 - Claude框架"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化行业分析器
        
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
        industry_name: str = None,
        financial_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        行业分析主入口 - Claude框架
        
        Args:
            stock_code: 股票代码
            company_name: 公司名称
            industry_name: 行业名称
            financial_data: 财务数据
            
        Returns:
            行业分析结果
        """
        logger.info(f"开始行业分析（Claude框架）: {stock_code}")
        
        result = {
            'stock_code': stock_code,
            'company_name': company_name,
            'industry_name': industry_name,
            'industry_analysis': {},
        }
        
        try:
            # Step 0: 识别行业关键指标（Claude新增）
            logger.info("识别行业关键指标...")
            key_metrics = self._identify_key_metrics(industry_name)
            result['industry_analysis']['key_metrics'] = key_metrics
            
            # Step 1: 市场概览（Claude: Market Overview）
            logger.info("分析市场概览...")
            market_overview = self._analyze_market_overview(
                stock_code, industry_name, financial_data
            )
            result['industry_analysis']['market_overview'] = market_overview
            
            # Step 2: 行业经济学（Claude: Industry Economics）
            logger.info("分析行业经济学...")
            industry_economics = self._analyze_industry_economics(
                industry_name, financial_data
            )
            result['industry_analysis']['economics'] = industry_economics
            
            # Step 3: 竞争格局（Claude: Competitive Landscape）
            logger.info("分析竞争格局...")
            competitive_landscape = self._analyze_competitive_landscape(
                stock_code, industry_name, financial_data
            )
            result['industry_analysis']['competitive_landscape'] = competitive_landscape
            
            # Step 4: 发展趋势（Claude: Key Trends & Drivers）
            logger.info("分析发展趋势...")
            trends = self._analyze_key_trends(industry_name)
            result['industry_analysis']['trends'] = trends
            
            # Step 5: 行业生命周期判断
            logger.info("判断行业生命周期...")
            lifecycle = self._determine_lifecycle(
                market_overview, competitive_landscape, trends
            )
            result['industry_analysis']['lifecycle'] = lifecycle
            
            # Step 6: 投资启示（Claude: Investment Implications）
            logger.info("生成投资启示...")
            investment_implications = self._generate_investment_implications(
                result['industry_analysis']
            )
            result['industry_analysis']['investment_implications'] = investment_implications
            
            # 生成总结
            summary = self._generate_summary(result['industry_analysis'])
            result['industry_analysis']['summary'] = summary
            
            logger.info("行业分析完成")
            
        except Exception as e:
            logger.error(f"行业分析失败: {e}")
            result['error'] = str(e)
            
        return result
    
    def _identify_key_metrics(self, industry_name: str) -> Dict[str, Any]:
        """
        识别行业关键指标（Claude Step 0）
        
        Args:
            industry_name: 行业名称
            
        Returns:
            行业关键指标
        """
        key_metrics = {
            'industry_type': None,
            'metrics': [],
            'benchmark_companies': [],
        }
        
        if not industry_name or not self.industry_metrics:
            # 默认指标
            key_metrics['metrics'] = [
                {'name': 'Revenue', 'description': '营业收入'},
                {'name': 'Growth Rate', 'description': '增长率'},
                {'name': 'Gross Margin', 'description': '毛利率'},
                {'name': 'ROIC', 'description': '投入资本回报率'},
            ]
            return key_metrics
        
        # 行业名称映射
        industry_mapping = {
            '化学制品': 'Chemical',
            '化工': 'Chemical',
            '软件': 'SaaS',
            '支付': 'Payments',
            '零售': 'Retail',
            '物流': 'Logistics',
            '银行': 'Banking',
            '保险': 'Insurance',
            '房地产': 'RealEstate',
            '新能源': 'NewEnergy',
        }
        
        # 查找匹配的行业
        industry_key = None
        for cn_name, en_key in industry_mapping.items():
            if cn_name in industry_name:
                industry_key = en_key
                break
        
        if industry_key and industry_key in self.industry_metrics.get('industries', {}):
            industry_config = self.industry_metrics['industries'][industry_key]
            key_metrics['industry_type'] = industry_config['name']
            key_metrics['metrics'] = industry_config.get('key_metrics', [])
            key_metrics['benchmark_companies'] = industry_config.get('benchmark_companies', [])
        
        return key_metrics
    
    def _analyze_market_overview(
        self,
        stock_code: str,
        industry_name: str,
        financial_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        市场概览分析（Claude Step 1）
        
        包括：市场规模、增长、细分、行业结构
        """
        overview = {
            'market_size': None,
            'market_growth': None,
            'market_segmentation': None,
            'industry_structure': None,
            'barriers_to_entry': None,
        }
        
        try:
            import akshare as ak
            
            # 获取行业板块数据
            if industry_name:
                try:
                    industry_board = ak.stock_board_industry_name_em(symbol=industry_name)
                    
                    if industry_board is not None and not industry_board.empty:
                        # 市场规模
                        total_market_cap = industry_board['总市值'].sum() if '总市值' in industry_board.columns else 0
                        
                        overview['market_size'] = {
                            'total_market_cap': total_market_cap,
                            'unit': '亿元',
                            'company_count': len(industry_board),
                            'data_source': 'AkShare',
                        }
                        
                        # 行业结构
                        top5_market_cap = industry_board.head(5)['总市值'].sum()
                        top5_share = (top5_market_cap / total_market_cap * 100) if total_market_cap > 0 else 0
                        
                        overview['industry_structure'] = {
                            'concentration': 'Concentrated' if top5_share > 50 else 'Fragmented',
                            'top5_market_share': f"{top5_share:.2f}%",
                            'total_companies': len(industry_board),
                        }
                        
                except Exception as e:
                    logger.warning(f"获取行业板块数据失败: {e}")
                    
        except ImportError:
            logger.warning("AkShare未安装")
        
        return overview
    
    def _analyze_industry_economics(
        self,
        industry_name: str,
        financial_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        行业经济学分析（Claude Step 2）
        
        包括：价值链、商业模式、利润池分布
        """
        economics = {
            'value_chain': None,
            'business_models': None,
            'profit_pool': None,
            'analysis': '',
        }
        
        # 行业价值链模板
        value_chain_map = {
            '化学制品': {
                'upstream': ['原材料供应商', '设备制造商'],
                'midstream': ['化工生产商', '加工企业'],
                'downstream': ['终端客户', '分销商'],
                'value_accretion': '中游生产商（规模效应）',
            },
            '软件': {
                'upstream': ['基础设施提供商', '开发工具'],
                'midstream': ['软件开发商', '平台运营商'],
                'downstream': ['企业客户', '个人用户'],
                'value_accretion': '平台运营商（网络效应）',
            },
        }
        
        # 查找匹配的价值链
        for key, value_chain in value_chain_map.items():
            if key in (industry_name or ''):
                economics['value_chain'] = value_chain
                break
        
        # 商业模式分析
        economics['business_models'] = {
            'types': ['B2B', 'B2C', 'B2B2C'],
            'revenue_models': ['产品销售', '订阅服务', '交易佣金'],
        }
        
        # 利润池分布（简化）
        economics['profit_pool'] = {
            'upstream_margin': '10-15%',
            'midstream_margin': '15-25%',
            'downstream_margin': '5-10%',
        }
        
        economics['analysis'] = f"{industry_name}行业价值链分析：价值主要在{economics['value_chain']['value_accretion'] if economics['value_chain'] else '中游'}环节积累。"
        
        return economics
    
    def _analyze_competitive_landscape(
        self,
        stock_code: str,
        industry_name: str,
        financial_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        竞争格局分析（Claude Step 3）
        
        包括：市场集中度、主要玩家、竞争动态
        """
        landscape = {
            'market_concentration': None,
            'key_players': [],
            'competitive_dynamics': None,
            'target_company_position': None,
        }
        
        try:
            import akshare as ak
            
            if industry_name:
                industry_board = ak.stock_board_industry_name_em(symbol=industry_name)
                
                if industry_board is not None and not industry_board.empty:
                    # 按市值排序
                    sorted_board = industry_board.sort_values('总市值', ascending=False)
                    total_market_cap = sorted_board['总市值'].sum()
                    
                    # 计算市场集中度（Claude标准）
                    cr3 = (sorted_board.head(3)['总市值'].sum() / total_market_cap * 100) if total_market_cap > 0 else 0
                    cr5 = (sorted_board.head(5)['总市值'].sum() / total_market_cap * 100) if total_market_cap > 0 else 0
                    cr10 = (sorted_board.head(10)['总市值'].sum() / total_market_cap * 100) if total_market_cap > 0 else 0
                    
                    # 判断集中度类型（基于Claude阈值）
                    concentration_type = self._assess_concentration_type(cr3, cr5, cr10)
                    
                    landscape['market_concentration'] = {
                        'CR3': f"{cr3:.2f}%",
                        'CR5': f"{cr5:.2f}%",
                        'CR10': f"{cr10:.2f}%",
                        'type': concentration_type['name'],
                        'competition_intensity': concentration_type['intensity'],
                    }
                    
                    # 主要玩家（Top 5）
                    key_players = []
                    for idx, row in sorted_board.head(5).iterrows():
                        player = {
                            'code': row.get('代码', ''),
                            'name': row.get('名称', ''),
                            'market_cap': row.get('总市值', 0),
                            'market_share': f"{(row.get('总市值', 0) / total_market_cap * 100):.2f}%" if total_market_cap > 0 else 'N/A',
                        }
                        key_players.append(player)
                    
                    landscape['key_players'] = key_players
                    
                    # 目标公司位置
                    target_company = sorted_board[sorted_board['代码'] == stock_code]
                    if not target_company.empty:
                        ranking = sorted_board.index.get_loc(target_company.index[0]) + 1
                        target_market_cap = target_company.iloc[0]['总市值']
                        target_share = (target_market_cap / total_market_cap * 100) if total_market_cap > 0 else 0
                        
                        landscape['target_company_position'] = {
                            'ranking': ranking,
                            'market_share': f"{target_share:.2f}%",
                            'tier': 'Tier 1' if ranking <= 3 else 'Tier 2' if ranking <= 10 else 'Tier 3',
                        }
                    
                    # 竞争动态
                    landscape['competitive_dynamics'] = {
                        'competition_basis': ['价格', '产品', '服务', '渠道'],
                        'share_trends': '龙头企业市场份额持续提升',
                        'disruption_risk': '中等',
                    }
                    
        except Exception as e:
            logger.warning(f"竞争格局分析失败: {e}")
        
        return landscape
    
    def _assess_concentration_type(self, cr3: float, cr5: float, cr10: float) -> Dict[str, str]:
        """
        评估市场集中度类型（基于Claude阈值）
        """
        if self.industry_metrics:
            thresholds = self.industry_metrics.get('concentration_thresholds', {})
            
            if cr3 >= thresholds.get('oligopoly', {}).get('cr3_threshold', 70):
                return {'name': '寡头垄断', 'intensity': '低'}
            elif cr3 >= thresholds.get('oligopolistic_competition', {}).get('cr3_threshold', 50):
                return {'name': '寡头竞争', 'intensity': '中等'}
            elif cr5 >= thresholds.get('competitive', {}).get('cr5_threshold', 50):
                return {'name': '竞争型市场', 'intensity': '高'}
            else:
                return {'name': '分散市场', 'intensity': '很高'}
        
        # 默认判断
        if cr3 > 70:
            return {'name': '寡头垄断', 'intensity': '低'}
        elif cr3 > 50:
            return {'name': '寡头竞争', 'intensity': '中等'}
        elif cr5 > 50:
            return {'name': '竞争型市场', 'intensity': '高'}
        else:
            return {'name': '分散市场', 'intensity': '很高'}
    
    def _analyze_key_trends(self, industry_name: str) -> Dict[str, Any]:
        """
        发展趋势分析（Claude Step 4）
        
        包括：长期趋势、逆风因素、技术颠覆、监管变化
        """
        trends = {
            'tailwinds': [],
            'headwinds': [],
            'technology_disruption': [],
            'regulatory_developments': [],
            'ma_activity': [],
        }
        
        # 行业趋势模板
        industry_trends = {
            '化学制品': {
                'tailwinds': [
                    '下游需求稳定增长',
                    '进口替代空间广阔',
                    '高端产品附加值提升',
                ],
                'headwinds': [
                    '环保成本上升',
                    '原材料价格波动',
                    '产能过剩压力',
                ],
                'technology_disruption': [
                    '绿色化学技术',
                    '智能制造',
                    '新材料研发',
                ],
                'regulatory_developments': [
                    '碳中和政策',
                    '环保标准提升',
                    '安全生产监管',
                ],
            },
            '软件': {
                'tailwinds': [
                    '数字化转型加速',
                    '云原生普及',
                    'AI应用扩展',
                ],
                'headwinds': [
                    '竞争加剧',
                    '人才成本上升',
                    '安全合规要求',
                ],
                'technology_disruption': [
                    'AI/ML集成',
                    '低代码平台',
                    '边缘计算',
                ],
                'regulatory_developments': [
                    '数据隐私法规',
                    '网络安全要求',
                    '跨境数据流动限制',
                ],
            },
        }
        
        # 查找匹配的趋势
        for key, industry_trend in industry_trends.items():
            if key in (industry_name or ''):
                trends = industry_trend
                break
        
        return trends
    
    def _determine_lifecycle(
        self,
        market_overview: Dict[str, Any],
        competitive_landscape: Dict[str, Any],
        trends: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        判断行业生命周期（基于Claude标准）
        """
        lifecycle = {
            'stage': None,
            'characteristics': [],
            'investment_implications': '',
        }
        
        # 基于市场集中度和增长趋势判断
        concentration = competitive_landscape.get('market_concentration', {})
        concentration_type = concentration.get('type', '')
        
        # 获取生命周期标准
        lifecycle_stages = {}
        if self.industry_metrics:
            lifecycle_stages = self.industry_metrics.get('lifecycle_stages', {})
        
        # 判断逻辑
        if concentration_type == '寡头垄断':
            lifecycle['stage'] = '成熟期'
            lifecycle['characteristics'] = [
                '市场集中度高',
                '增长放缓',
                '竞争格局稳定',
            ]
            lifecycle['investment_implications'] = '关注龙头企业的分红和现金流'
        elif concentration_type == '寡头竞争':
            lifecycle['stage'] = '成长期'
            lifecycle['characteristics'] = [
                '市场集中度适中',
                '增长较快',
                '竞争格局演变中',
            ]
            lifecycle['investment_implications'] = '关注市场份额提升者'
        else:
            lifecycle['stage'] = '成长早期'
            lifecycle['characteristics'] = [
                '市场分散',
                '竞争激烈',
                '行业标准未形成',
            ]
            lifecycle['investment_implications'] = '关注具有创新能力和差异化优势的企业'
        
        return lifecycle
    
    def _generate_investment_implications(
        self,
        industry_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        生成投资启示（Claude Step 5）
        """
        implications = {
            'opportunities': [],
            'thematic_bets': [],
            'key_debates': [],
            'catalysts': [],
        }
        
        lifecycle = industry_analysis.get('lifecycle', {})
        trends = industry_analysis.get('trends', {})
        
        # 基于生命周期和趋势生成投资启示
        if lifecycle.get('stage') == '成长期':
            implications['opportunities'] = [
                '市场份额提升机会',
                '行业整合机遇',
                '新产品/新市场拓展',
            ]
            implications['thematic_bets'] = [
                '行业龙头',
                '细分领域冠军',
            ]
        elif lifecycle.get('stage') == '成熟期':
            implications['opportunities'] = [
                '现金流稳定',
                '分红收益',
                '成本优化空间',
            ]
            implications['thematic_bets'] = [
                '高股息股票',
                '价值股',
            ]
        
        # 关键争论
        implications['key_debates'] = [
            '增长可持续性',
            '竞争格局演变',
            '技术颠覆风险',
        ]
        
        # 催化剂
        implications['catalysts'] = [
            '政策变化',
            '技术突破',
            '行业整合',
        ]
        
        return implications
    
    def _generate_summary(self, industry_analysis: Dict[str, Any]) -> str:
        """生成行业分析总结"""
        summary_parts = []
        
        # 市场概览
        market_overview = industry_analysis.get('market_overview', {})
        if market_overview.get('market_size'):
            summary_parts.append(
                f"**市场规模**：总市值{market_overview['market_size']['total_market_cap']/10000:.2f}万亿元，"
                f"共{market_overview['market_size']['company_count']}家上市公司。"
            )
        
        # 竞争格局
        competitive_landscape = industry_analysis.get('competitive_landscape', {})
        concentration = competitive_landscape.get('market_concentration', {})
        if concentration:
            summary_parts.append(
                f"**竞争格局**：{concentration['type']}，CR3为{concentration['CR3']}，"
                f"竞争强度{concentration['competition_intensity']}。"
            )
        
        # 生命周期
        lifecycle = industry_analysis.get('lifecycle', {})
        if lifecycle.get('stage'):
            summary_parts.append(
                f"**生命周期**：{lifecycle['stage']}，{lifecycle['investment_implications']}。"
            )
        
        return '\n\n'.join(summary_parts)
