# 股票深度研究报告自动生成系统

> 版本：1.1
> 创建日期：2026-05-13
> 最后更新：2026-05-13

基于WorkBuddy投研数据源与工具清单设计，集成Claude Financial Services最佳实践的模块化股票研究报告生成系统。

## 核心特性

- **模块化设计**：按需组合分析模块，灵活配置
- **多报告类型**：支持首发覆盖报告、季报更新报告
- **多市场支持**：A股（主）、港股、美股
- **本地优先**：优先使用本地raw文档库，避免重复下载
- **知识沉淀**：生成的报告自动入库，形成知识资产
- **Claude集成**：参考Claude Financial Services的专业技能实现
- **MCP数据源**：支持11个华尔街级数据连接器（可配置）

## 系统架构

```
stock-research-system/
├── main.py                      # 主入口
├── config/
│   └── system_config.yaml       # 系统配置
├── core/
│   └── orchestrator.py          # 调度引擎
├── modules/
│   ├── data_fetch/              # 数据获取模块
│   │   ├── local_checker.py     # 本地文档检查
│   │   └── a_stock_fetcher.py   # A股数据获取
│   ├── financial_analysis/      # 财务分析模块
│   │   ├── financial_statement.py
│   │   ├── financial_indicator.py
│   │   └── roic_analysis.py
│   ├── valuation/               # 估值建模模块
│   │   ├── dcf_model.py
│   │   └── comps_analysis.py
│   ├── industry_analysis/       # 行业分析模块
│   │   └── industry_analysis.py
│   ├── competitive_analysis/    # 竞争分析模块
│   │   └── competitive_landscape.py
│   └── report_generation/       # 报告生成模块
│       ├── initiating_coverage.py
│       └── earnings_update.py
├── utils/
│   └── logger.py                # 日志工具
└── docs/
    └── SYSTEM_DESIGN.md         # 系统设计文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install akshare pandas pyyaml
```

### 2. 配置系统

编辑 `config/system_config.yaml`，设置本地数据路径：

```yaml
data_sources:
  local_raw_path: "D:\\Chen_Guoxi\\知识库\\raw\\"
  knowledge_base_path: "D:\\Chen_Guoxi\\知识库\\"
  report_output_path: "D:\\Chen_Guoxi\\知识库\\reports\\"
```

### 3. 生成报告

#### 首发覆盖报告（完整流程）

```bash
python main.py --report-type initiating_coverage --stock-code 600309
```

#### 季报更新报告

```bash
python main.py --report-type earnings_update --stock-code 600309 --quarter 2025Q1
```

#### 指定模块运行

```bash
# 只运行财务分析和估值模块
python main.py --report-type initiating_coverage --stock-code 600309 \
    --modules financial_analysis,valuation
```

#### 自定义估值参数

```bash
python main.py --report-type initiating_coverage --stock-code 600309 \
    --growth-rate 0.06 --wacc 0.09 --target-price 95.00 --rating 买入
```

## 可用模块

| 模块ID | 模块名称 | 说明 |
|--------|---------|------|
| `data_fetch` | 数据获取 | 获取财务数据、行情数据、行业数据等 |
| `financial_analysis` | 财务分析 | 三大报表分析、财务指标计算、ROIC分析 |
| `valuation` | 估值建模 | DCF估值、可比公司分析 |
| `industry_analysis` | 行业分析 | 行业规模、竞争格局、发展趋势 |
| `competitive_analysis` | 竞争分析 | 竞争格局、护城河评估、Porter五力 |
| `report_generation` | 报告生成 | 生成结构化研究报告 |

查看所有模块：

```bash
python main.py --list-modules
```

## 模块依赖关系

```
data_fetch
    ↓
financial_analysis
    ↓
valuation
    ↓
industry_analysis → competitive_analysis
    ↓
report_generation
```

## 报告输出示例

### 首发覆盖报告结构

```markdown
# 万华化学（600309.SH）首次覆盖报告

## 投资要点
## 一、公司概况
## 二、行业分析
## 三、财务分析
## 四、估值分析
## 五、风险提示
## 六、投资建议
```

### 季报更新报告结构

```markdown
# 万华化学（600309.SH）2025Q1季报点评

## 业绩概览
## 经营亮点
## 财务分析
## 盈利预测调整
## 估值更新
## 投资建议
```

## 与现有技能的集成

本系统参考Claude Financial Services的设计理念，实现了以下专业技能：

### 已集成的Claude Skills

| Claude Skill | 我们的实现 | 说明 |
|-------------|-----------|------|
| `/dcf` | `modules/valuation/dcf_model.py` | DCF估值模型，含WACC计算和敏感性分析 |
| `/comps` | `modules/valuation/comps_analysis.py` | 可比公司分析，生成交易倍数报告 |
| `/3-statement-model` | `modules/financial_analysis/financial_statement.py` | 三大财务报表分析 |
| `/initiate` | `modules/report_generation/initiating_coverage.py` | 首次覆盖报告生成 |
| `/earnings` | `modules/report_generation/earnings_update.py` | 季报更新报告 |

### 可用的数据连接器（WorkBuddy数据源）

通过配置`config/data_connectors.json`可连接以下数据源：

**A股数据源**：
- **AkShare**（免费，核心数据源）：三大报表、行情、财务指标、资金流向、宏观数据
- **东方财富网**：实时行情、财务数据、研报
- **巨潮资讯**：证监会指定披露平台，公告原文

**港股数据源**：
- **IR Asia**：港股投资者材料最全平台（年报、投资者演示、业绩电话会）
- **港交所披露易**：港股官方披露平台

**美股数据源**：
- **SEC EDGAR**：美股官方披露系统（10-K/10-Q/8-K）
- **yfinance**：美股行情和财务摘要

**本地数据资产**：
- **本地raw文档库**：319个文件，311MB（万华化学、台积电、谷歌等）
- **本地知识库**：entity/concept结构化知识

**数据源优势**：
- 完全免费，无需API密钥
- 本地化，针对中国市场优化
- 离线优先，本地文档库可离线使用
- 多市场覆盖：A股/港股/美股/宏观

详细说明请参考：`docs/DATA_SOURCES_GUIDE.md`

## 配置说明

### 系统配置 (`config/system_config.yaml`)

```yaml
# 数据源配置
data_sources:
  local_raw_path: "本地raw文档库路径"
  knowledge_base_path: "知识库路径"
  report_output_path: "报告输出路径"
  
# 模块配置
modules:
  valuation:
    dcf:
      default_forecast_years: 5    # 默认预测期
      default_growth_rate: 0.05    # 默认永续增长率
      default_wacc: 0.10           # 默认WACC
```

## 开发路线

### 第一阶段：核心框架（当前）

- [x] 系统架构设计
- [x] 调度引擎实现
- [x] 数据获取模块框架
- [x] 报告生成模块框架
- [ ] 完善各模块实现

### 第二阶段：功能完善

- [ ] 财务分析模块详细实现
- [ ] 估值建模模块详细实现
- [ ] 行业分析模块详细实现
- [ ] 竞争分析模块详细实现

### 第三阶段：优化扩展

- [ ] 支持港股/美股
- [ ] 支持Word/PPT输出
- [ ] Web界面
- [ ] AI增强分析

## 注意事项

1. **数据延迟**：AkShare行情延迟约15分钟
2. **数据质量**：免费数据源可能存在错误，需人工校验
3. **估值合理性**：估值结果仅供参考，不构成投资建议
4. **本地路径**：需在配置文件中设置正确的本地数据路径

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系系统开发者。
