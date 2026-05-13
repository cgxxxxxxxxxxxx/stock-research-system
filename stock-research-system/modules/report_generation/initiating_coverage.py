#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首发覆盖报告生成器 - 自动生成完整的股票首次覆盖研究报告
参考Claude Financial Services的报告生成最佳实践
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class InitiatingCoverageGenerator:
    """首发覆盖报告生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化
        
        Args:
            config: 系统配置
        """
        self.config = config
        self.include_disclaimer = config['modules']['report'].get('include_disclaimer', True)
        
    def generate(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成首发覆盖报告
        
        Args:
            report_data: 报告数据
            
        Returns:
            生成结果
        """
        logger.info("生成首发覆盖报告...")
        
        stock_code = report_data.get('stock_code')
        company_name = report_data.get('company_name', stock_code)
        
        # 生成报告内容
        report_content = self._generate_content(report_data)
        
        # 保存报告
        output_path = Path(self.config['data_sources']['report_output_path'])
        output_path.mkdir(parents=True, exist_ok=True)
        
        report_filename = f"{company_name}_首发覆盖_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = output_path / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"报告已生成: {report_path}")
        
        return {
            'report_path': str(report_path),
            'word_count': len(report_content),
            'sections': self._count_sections(report_content),
        }
        
    def _generate_content(self, data: Dict[str, Any]) -> str:
        """
        生成报告内容
        
        Args:
            data: 报告数据
            
        Returns:
            报告内容
        """
        stock_code = data.get('stock_code')
        company_name = data.get('company_name', stock_code)
        market = data.get('market', 'A股')
        report_date = data.get('report_date', datetime.now().strftime('%Y-%m-%d'))
        rating = data.get('rating', '持有')
        target_price = data.get('target_price', 'N/A')
        
        # 提取分析数据
        company_info = data.get('data_fetch', {}).get('api_data', {}).get('company_info', {})
        financial_analysis = data.get('financial_analysis', {})
        valuation = data.get('valuation', {})
        industry_analysis = data.get('industry_analysis', {})
        competitive_analysis = data.get('competitive_analysis', {})
        
        # 构建报告各部分
        sections = []
        
        # 标题
        sections.append(self._generate_header(company_name, stock_code, market, report_date, rating, target_price))
        
        # 投资要点
        sections.append(self._generate_investment_highlights(data, company_info, financial_analysis, valuation))
        
        # 公司概况
        sections.append(self._generate_company_overview(company_info))
        
        # 行业分析
        sections.append(self._generate_industry_analysis(industry_analysis))
        
        # 财务分析
        sections.append(self._generate_financial_analysis(financial_analysis))
        
        # 估值分析
        sections.append(self._generate_valuation_analysis(valuation, stock_code))
        
        # 风险提示
        sections.append(self._generate_risk_warnings(company_info, financial_analysis))
        
        # 投资建议
        sections.append(self._generate_investment_recommendation(rating, target_price, valuation))
        
        # 免责声明
        if self.include_disclaimer:
            sections.append(self._generate_disclaimer())
        
        return '\n\n'.join(sections)
        
    def _generate_header(
        self,
        company_name: str,
        stock_code: str,
        market: str,
        report_date: str,
        rating: str,
        target_price: Any
    ) -> str:
        """生成报告标题"""
        exchange = '.SH' if market == 'A股' else '.HK' if market == '港股' else ''
        target_price_str = f"{target_price:.2f}" if isinstance(target_price, (int, float)) else str(target_price)
        
        return f"""# {company_name}（{stock_code}{exchange}）首次覆盖报告

**报告日期**：{report_date}
**投资评级**：{rating}
**目标价**：{target_price_str}元

---"""
        
    def _generate_investment_highlights(
        self,
        data: Dict[str, Any],
        company_info: Dict[str, Any],
        financial_analysis: Dict[str, Any],
        valuation: Dict[str, Any]
    ) -> str:
        """生成投资要点"""
        highlights = []
        
        # 核心逻辑
        industry = company_info.get('industry', '')
        main_business = company_info.get('main_business', '')
        core_logic = f"{industry}行业龙头企业" if industry else "行业领先企业"
        if main_business:
            core_logic += f"，主营{main_business[:50]}..."
        highlights.append(f"- **核心逻辑**：{core_logic}")
        
        # 成长驱动
        growth_analysis = financial_analysis.get('income_statement_analysis', {}).get('growth_analysis', {})
        revenue_growth = growth_analysis.get('revenue_growth_yoy', 0)
        if revenue_growth:
            growth_desc = f"营收同比增长{revenue_growth*100:.1f}%"
            highlights.append(f"- **成长驱动**：{growth_desc}")
        else:
            highlights.append(f"- **成长驱动**：[待补充]")
            
        # 估值吸引力
        dcf_result = valuation.get('dcf', {})
        per_share_value = dcf_result.get('per_share_value', 0)
        if per_share_value > 0:
            highlights.append(f"- **估值吸引力**：DCF估值{per_share_value:.2f}元/股")
        else:
            highlights.append(f"- **估值吸引力**：[待补充]")
            
        # 风险因素
        highlights.append(f"- **风险因素**：行业竞争加剧、宏观经济波动、原材料价格波动")
        
        return f"""## 投资要点

{chr(10).join(highlights)}

---"""
        
    def _generate_company_overview(self, company_info: Dict[str, Any]) -> str:
        """生成公司概况"""
        stock_name = company_info.get('stock_name', 'N/A')
        industry = company_info.get('industry', 'N/A')
        list_date = company_info.get('list_date', 'N/A')
        region = company_info.get('region', 'N/A')
        main_business = company_info.get('main_business', '暂无')
        description = company_info.get('description', '暂无')
        
        return f"""## 一、公司概况

### 1.1 基本信息

- **公司名称**：{stock_name}
- **所属行业**：{industry}
- **上市日期**：{list_date}
- **注册地**：{region}

### 1.2 主营业务

{main_business}

### 1.3 公司简介

{description[:500]}{'...' if len(description) > 500 else ''}

---"""
        
    def _generate_industry_analysis(self, industry_analysis: Dict[str, Any]) -> str:
        """生成行业分析"""
        # 由于行业分析模块尚未完善，使用占位内容
        return """## 二、行业分析

### 2.1 行业概况

[待补充：行业规模、发展阶段、市场容量等]

### 2.2 竞争格局

[待补充：主要竞争对手、市场份额、竞争态势等]

### 2.3 发展趋势

[待补充：行业发展趋势、政策影响、技术变革等]

---"""
        
    def _generate_financial_analysis(self, financial_analysis: Dict[str, Any]) -> str:
        """生成财务分析"""
        summary = financial_analysis.get('summary', {})
        key_metrics = summary.get('key_metrics', {})
        strengths = summary.get('strengths', [])
        weaknesses = summary.get('weaknesses', [])
        
        # 提取关键指标
        debt_ratio = key_metrics.get('debt_to_asset', 'N/A')
        current_ratio = key_metrics.get('current_ratio', 'N/A')
        gross_margin = key_metrics.get('gross_margin', 'N/A')
        net_margin = key_metrics.get('net_margin', 'N/A')
        ocf_to_np = key_metrics.get('ocf_to_net_profit', 'N/A')
        
        # 格式化指标
        def format_ratio(value):
            if isinstance(value, float):
                return f"{value:.2%}"
            return str(value)
            
        metrics_table = f"""
| 指标 | 数值 | 说明 |
|------|------|------|
| 资产负债率 | {format_ratio(debt_ratio)} | 财务杠杆水平 |
| 流动比率 | {format_ratio(current_ratio)} | 短期偿债能力 |
| 毛利率 | {format_ratio(gross_margin)} | 盈利能力 |
| 净利率 | {format_ratio(net_margin)} | 盈利质量 |
| 经营现金流/净利润 | {format_ratio(ocf_to_np)} | 现金流质量 |
"""
        
        # 优势分析
        strengths_text = '\n'.join([f"- {s}" for s in strengths]) if strengths else '- [待补充]'
        
        # 劣势分析
        weaknesses_text = '\n'.join([f"- {w}" for w in weaknesses]) if weaknesses else '- [待补充]'
        
        return f"""## 三、财务分析

### 3.1 关键财务指标

{metrics_table}

### 3.2 财务优势

{strengths_text}

### 3.3 财务风险

{weaknesses_text}

---"""
        
    def _generate_valuation_analysis(self, valuation: Dict[str, Any], stock_code: str) -> str:
        """生成估值分析"""
        dcf_result = valuation.get('dcf', {})
        comps_result = valuation.get('comps', {})
        
        # DCF估值
        dcf_section = "#### DCF估值\n\n"
        per_share_value = dcf_result.get('per_share_value', 0)
        if per_share_value > 0:
            dcf_section += f"- **每股价值**：{per_share_value:.2f}元\n"
            dcf_section += f"- **企业价值**：{dcf_result.get('enterprise_value', 0):,.0f}元\n"
            dcf_section += f"- **股权价值**：{dcf_result.get('equity_value', 0):,.0f}元\n"
            dcf_section += f"- **关键假设**：\n"
            dcf_section += f"  - 永续增长率：{dcf_result.get('assumptions', {}).get('growth_rate', 0):.2%}\n"
            dcf_section += f"  - WACC：{dcf_result.get('assumptions', {}).get('wacc', 0):.2%}\n"
        else:
            dcf_section += "[DCF估值结果不可用]\n"
            
        # 可比公司估值
        comps_section = "#### 可比公司估值\n\n"
        comps_section += "[待补充：可比公司分析结果]\n"
        
        # 估值结论
        conclusion_section = "#### 估值结论\n\n"
        if per_share_value > 0:
            conclusion_section += f"综合DCF估值结果，公司合理估值区间为{per_share_value*0.9:.2f}-{per_share_value*1.1:.2f}元/股。\n"
        else:
            conclusion_section += "[估值结论待补充]\n"
            
        return f"""## 四、估值分析

{dcf_section}

{comps_section}

{conclusion_section}

---"""
        
    def _generate_risk_warnings(
        self,
        company_info: Dict[str, Any],
        financial_analysis: Dict[str, Any]
    ) -> str:
        """生成风险提示"""
        risks = []
        
        # 行业风险
        industry = company_info.get('industry', '')
        if industry:
            risks.append(f"- **行业风险**：{industry}行业竞争加剧，可能影响公司市场份额和盈利能力")
            
        # 财务风险
        weaknesses = financial_analysis.get('summary', {}).get('weaknesses', [])
        if weaknesses:
            risks.append(f"- **财务风险**：{weaknesses[0] if weaknesses else '需关注财务状况'}")
            
        # 宏观风险
        risks.append(f"- **宏观风险**：宏观经济波动可能影响下游需求和公司业绩")
        
        # 其他风险
        risks.append(f"- **其他风险**：政策变化、原材料价格波动等不确定因素")
        
        return f"""## 五、风险提示

{chr(10).join(risks)}

---"""
        
    def _generate_investment_recommendation(
        self,
        rating: str,
        target_price: Any,
        valuation: Dict[str, Any]
    ) -> str:
        """生成投资建议"""
        target_price_str = f"{target_price:.2f}" if isinstance(target_price, (int, float)) else str(target_price)
        
        recommendation = f"给予\"{rating}\"评级"
        if target_price:
            recommendation += f"，目标价{target_price_str}元"
            
        return f"""## 六、投资建议

{recommendation}。

**投资逻辑**：
1. 公司在行业中具有竞争优势
2. 财务状况稳健，盈利能力良好
3. 估值合理，具有一定安全边际

**催化剂**：
- 行业景气度提升
- 公司业绩超预期
- 新产品/新市场拓展

---"""
        
    def _generate_disclaimer(self) -> str:
        """生成免责声明"""
        return """## 免责声明

本报告仅供参考，不构成投资建议。投资者据此操作，风险自担。

本报告基于公开信息编制，我们不对信息的准确性和完整性作任何保证。报告中的观点、结论和建议仅供参考，不构成对所述证券的买卖出价或征价。

投资者应当充分考虑自身风险承受能力，审慎决策。

---

*本报告由股票深度研究报告系统自动生成*
*生成时间：""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*"
        
    def _count_sections(self, content: str) -> int:
        """统计报告章节数"""
        return content.count('\n## ')
