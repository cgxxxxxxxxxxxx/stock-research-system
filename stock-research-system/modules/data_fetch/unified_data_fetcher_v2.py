#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据获取器V2 - 多数据源降级机制
优先级：本地文件 → 本地缓存 → AkShare → 东方财富 → Tushare
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path
import json
import hashlib
import os

logger = logging.getLogger(__name__)


class UnifiedDataFetcherV2:
    """统一数据获取器V2 - 本地优先"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化统一数据获取器
        
        Args:
            config: 系统配置
        """
        self.config = config
        
        # 数据源优先级（本地优先）
        self.data_source_priority = [
            'local_files',  # 优先使用本地文件
            'local_cache',  # 本地缓存
            'akshare',      # AkShare
            'eastmoney',    # 东方财富
            'tushare',      # Tushare（需要token）
        ]
        
        # 初始化各数据源
        self.akshare = None
        self.tushare = None
        
        # 本地文件目录
        self.local_data_dir = Path(config.get('data_sources', {}).get('local_data_dir', 'data/local'))
        self.local_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 缓存配置
        self.cache_enabled = config.get('modules', {}).get('data_fetch', {}).get('cache_enabled', True)
        self.cache_expire_days = config.get('modules', {}).get('data_fetch', {}).get('cache_expire_days', 7)
        self.cache_dir = Path(config.get('data_sources', {}).get('cache_db', 'data/cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据源状态
        self.source_status = {
            'local_files': {'available': True, 'last_check': datetime.now()},
            'local_cache': {'available': True, 'last_check': datetime.now()},
            'akshare': {'available': False, 'last_check': None},
            'eastmoney': {'available': False, 'last_check': None},
            'tushare': {'available': False, 'last_check': None},
        }
        
        # 检查数据源可用性
        self._check_data_sources()
    
    def _check_data_sources(self):
        """检查各数据源可用性"""
        # 检查AkShare
        try:
            import akshare as ak
            self.akshare = ak
            self.source_status['akshare']['available'] = True
            self.source_status['akshare']['last_check'] = datetime.now()
            logger.info("AkShare数据源可用")
        except ImportError:
            logger.warning("AkShare未安装")
        
        # 检查Tushare
        try:
            import tushare as ts
            self.tushare = ts
            # 检查是否设置了token
            if os.getenv('TUSHARE_TOKEN'):
                ts.set_token(os.getenv('TUSHARE_TOKEN'))
                self.source_status['tushare']['available'] = True
                self.source_status['tushare']['last_check'] = datetime.now()
                logger.info("Tushare数据源可用")
        except ImportError:
            logger.warning("Tushare未安装")
    
    def fetch(
        self,
        stock_code: str,
        data_types: List[str] = None,
    ) -> Dict[str, Any]:
        """
        统一数据获取入口
        
        Args:
            stock_code: 股票代码
            data_types: 需要获取的数据类型列表
            
        Returns:
            数据字典
        """
        logger.info(f"统一数据获取: {stock_code}")
        
        if data_types is None:
            data_types = [
                'company_info',
                'balance_sheet',
                'income_statement',
                'cash_flow',
                'financial_indicators',
                'realtime_quote',
            ]
        
        result = {
            'stock_code': stock_code,
            'data_source': None,
            'fetch_time': datetime.now().isoformat(),
        }
        
        # 尝试各数据源
        for source in self.data_source_priority:
            try:
                logger.info(f"尝试使用{source}数据源...")
                
                if source == 'local_files':
                    # 优先尝试本地文件
                    data = self._load_from_local_files(stock_code, data_types)
                elif source == 'local_cache':
                    # 尝试本地缓存
                    data = self._load_from_cache(stock_code)
                elif source == 'akshare':
                    if not self.source_status.get(source, {}).get('available', False):
                        continue
                    data = self._fetch_from_akshare(stock_code, data_types)
                elif source == 'eastmoney':
                    if not self.source_status.get(source, {}).get('available', False):
                        continue
                    data = self._fetch_from_eastmoney(stock_code, data_types)
                elif source == 'tushare':
                    if not self.source_status.get(source, {}).get('available', False):
                        continue
                    data = self._fetch_from_tushare(stock_code, data_types)
                else:
                    continue
                
                if data:
                    result.update(data)
                    result['data_source'] = source
                    
                    # 保存到缓存（如果不是从缓存加载的）
                    if self.cache_enabled and source not in ['local_files', 'local_cache']:
                        self._save_to_cache(stock_code, data)
                    
                    logger.info(f"成功从{source}获取数据")
                    return result
                    
            except Exception as e:
                logger.warning(f"{source}数据源获取失败: {e}")
                # 标记该数据源暂时不可用
                if source in self.source_status:
                    self.source_status[source]['available'] = False
                continue
        
        logger.error(f"所有数据源均不可用")
        result['error'] = "所有数据源均不可用"
        return result
    
    def _load_from_local_files(
        self,
        stock_code: str,
        data_types: List[str],
    ) -> Optional[Dict[str, Any]]:
        """从本地文件加载数据"""
        data = {}
        
        # 本地文件命名规则：{stock_code}_{data_type}.csv 或 .xlsx
        for data_type in data_types:
            # 尝试不同的文件格式
            for ext in ['.csv', '.xlsx', '.json']:
                file_path = self.local_data_dir / f"{stock_code}_{data_type}{ext}"
                
                if file_path.exists():
                    logger.info(f"从本地文件加载: {file_path}")
                    
                    try:
                        if ext == '.csv':
                            df = pd.read_csv(file_path)
                            data[data_type] = df
                        elif ext == '.xlsx':
                            df = pd.read_excel(file_path)
                            data[data_type] = df
                        elif ext == '.json':
                            with open(file_path, 'r', encoding='utf-8') as f:
                                json_data = json.load(f)
                                data[data_type] = json_data
                        
                        logger.info(f"成功加载本地文件: {data_type}")
                    except Exception as e:
                        logger.warning(f"加载本地文件失败: {e}")
        
        return data if data else None
    
    def _fetch_from_akshare(
        self,
        stock_code: str,
        data_types: List[str],
    ) -> Optional[Dict[str, Any]]:
        """从AkShare获取数据"""
        data = {}
        
        try:
            # 公司信息
            if 'company_info' in data_types:
                logger.info("获取公司信息...")
                try:
                    info = self.akshare.stock_individual_info_em(symbol=stock_code)
                    if info is not None and not info.empty:
                        data['company_info'] = info.to_dict('records')
                except Exception as e:
                    logger.warning(f"获取公司信息失败: {e}")
            
            # 资产负债表
            if 'balance_sheet' in data_types:
                logger.info("获取资产负债表...")
                try:
                    balance_sheet = None
                    
                    try:
                        balance_sheet = self.akshare.stock_balance_sheet_by_report_em(symbol=stock_code)
                    except:
                        pass
                    
                    if balance_sheet is None or balance_sheet.empty:
                        try:
                            balance_sheet = self.akshare.stock_balance_sheet_by_date_em(symbol=stock_code)
                        except:
                            pass
                    
                    if balance_sheet is not None and not balance_sheet.empty:
                        data['balance_sheet'] = balance_sheet
                except Exception as e:
                    logger.warning(f"获取资产负债表失败: {e}")
            
            # 利润表
            if 'income_statement' in data_types:
                logger.info("获取利润表...")
                try:
                    income_statement = None
                    
                    try:
                        income_statement = self.akshare.stock_profit_sheet_by_report_em(symbol=stock_code)
                    except:
                        pass
                    
                    if income_statement is None or income_statement.empty:
                        try:
                            income_statement = self.akshare.stock_profit_sheet_by_date_em(symbol=stock_code)
                        except:
                            pass
                    
                    if income_statement is not None and not income_statement.empty:
                        data['income_statement'] = income_statement
                except Exception as e:
                    logger.warning(f"获取利润表失败: {e}")
            
            # 现金流量表
            if 'cash_flow' in data_types:
                logger.info("获取现金流量表...")
                try:
                    cash_flow = None
                    
                    try:
                        cash_flow = self.akshare.stock_cash_flow_sheet_by_report_em(symbol=stock_code)
                    except:
                        pass
                    
                    if cash_flow is None or cash_flow.empty:
                        try:
                            cash_flow = self.akshare.stock_cash_flow_sheet_by_date_em(symbol=stock_code)
                        except:
                            pass
                    
                    if cash_flow is not None and not cash_flow.empty:
                        data['cash_flow'] = cash_flow
                except Exception as e:
                    logger.warning(f"获取现金流量表失败: {e}")
            
            # 财务指标
            if 'financial_indicators' in data_types:
                logger.info("获取财务指标...")
                try:
                    indicators = self.akshare.stock_financial_analysis_indicator(symbol=stock_code)
                    if indicators is not None and not indicators.empty:
                        data['financial_indicators'] = indicators
                except Exception as e:
                    logger.warning(f"获取财务指标失败: {e}")
            
            # 实时行情
            if 'realtime_quote' in data_types:
                logger.info("获取实时行情...")
                try:
                    quote = self.akshare.stock_zh_a_spot_em()
                    if quote is not None and not quote.empty:
                        stock_quote = quote[quote['代码'] == stock_code]
                        if not stock_quote.empty:
                            data['realtime_quote'] = stock_quote.iloc[0].to_dict()
                except Exception as e:
                    logger.warning(f"获取实时行情失败: {e}")
            
            return data if data else None
            
        except Exception as e:
            logger.error(f"AkShare获取数据失败: {e}")
            raise
    
    def _fetch_from_eastmoney(
        self,
        stock_code: str,
        data_types: List[str],
    ) -> Optional[Dict[str, Any]]:
        """从东方财富获取数据（通过AkShare的东方财富接口）"""
        data = {}
        
        try:
            # 历史行情数据
            if 'realtime_quote' in data_types or 'price_history' in data_types:
                logger.info("从东方财富获取历史行情...")
                try:
                    hist = self.akshare.stock_zh_a_hist(
                        symbol=stock_code,
                        period='daily',
                        start_date=(datetime.now() - timedelta(days=365)).strftime('%Y%m%d'),
                        end_date=datetime.now().strftime('%Y%m%d'),
                        adjust='qfq'
                    )
                    if hist is not None and not hist.empty:
                        data['price_history'] = hist
                        data['realtime_quote'] = {
                            'price': hist.iloc[-1]['收盘'],
                            'date': hist.iloc[-1]['日期'],
                        }
                except Exception as e:
                    logger.warning(f"获取历史行情失败: {e}")
            
            return data if data else None
            
        except Exception as e:
            logger.error(f"东方财富获取数据失败: {e}")
            raise
    
    def _fetch_from_tushare(
        self,
        stock_code: str,
        data_types: List[str],
    ) -> Optional[Dict[str, Any]]:
        """从Tushare获取数据"""
        data = {}
        
        try:
            import tushare as ts
            
            pro = ts.pro_api()
            
            # 转换股票代码格式（600309 -> 600309.SH）
            ts_code = f"{stock_code}.SH" if stock_code.startswith('6') else f"{stock_code}.SZ"
            
            # 公司信息
            if 'company_info' in data_types:
                logger.info("从Tushare获取公司信息...")
                try:
                    info = pro.stock_company(ts_code=ts_code)
                    if info is not None and not info.empty:
                        data['company_info'] = info.iloc[0].to_dict()
                except Exception as e:
                    logger.warning(f"获取公司信息失败: {e}")
            
            # 资产负债表
            if 'balance_sheet' in data_types:
                logger.info("从Tushare获取资产负债表...")
                try:
                    bs = pro.balancesheet(ts_code=ts_code)
                    if bs is not None and not bs.empty:
                        data['balance_sheet'] = bs
                except Exception as e:
                    logger.warning(f"获取资产负债表失败: {e}")
            
            # 利润表
            if 'income_statement' in data_types:
                logger.info("从Tushare获取利润表...")
                try:
                    income = pro.income(ts_code=ts_code)
                    if income is not None and not income.empty:
                        data['income_statement'] = income
                except Exception as e:
                    logger.warning(f"获取利润表失败: {e}")
            
            # 现金流量表
            if 'cash_flow' in data_types:
                logger.info("从Tushare获取现金流量表...")
                try:
                    cf = pro.cashflow(ts_code=ts_code)
                    if cf is not None and not cf.empty:
                        data['cash_flow'] = cf
                except Exception as e:
                    logger.warning(f"获取现金流量表失败: {e}")
            
            # 日线行情
            if 'realtime_quote' in data_types:
                logger.info("从Tushare获取日线行情...")
                try:
                    daily = pro.daily(ts_code=ts_code)
                    if daily is not None and not daily.empty:
                        data['price_history'] = daily
                        data['realtime_quote'] = {
                            'price': daily.iloc[0]['close'],
                            'date': daily.iloc[0]['trade_date'],
                        }
                except Exception as e:
                    logger.warning(f"获取日线行情失败: {e}")
            
            return data if data else None
            
        except Exception as e:
            logger.error(f"Tushare获取数据失败: {e}")
            raise
    
    def _get_cache_key(self, stock_code: str) -> str:
        """生成缓存键"""
        key_str = f"{stock_code}_unified"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _load_from_cache(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """从缓存加载数据"""
        if not self.cache_enabled:
            return None
        
        cache_key = self._get_cache_key(stock_code)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # 检查缓存是否过期
            cache_time = datetime.fromisoformat(cached_data['cache_time'])
            if datetime.now() - cache_time > timedelta(days=self.cache_expire_days):
                logger.info("缓存已过期")
                return None
            
            logger.info(f"从缓存加载数据: {stock_code}")
            return cached_data['data']
            
        except Exception as e:
            logger.warning(f"读取缓存失败: {e}")
            return None
    
    def _save_to_cache(self, stock_code: str, data: Dict[str, Any]):
        """保存数据到缓存"""
        if not self.cache_enabled:
            return
        
        cache_key = self._get_cache_key(stock_code)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            # 转换DataFrame为可序列化格式
            serializable_data = {}
            for key, value in data.items():
                if isinstance(value, pd.DataFrame):
                    serializable_data[key] = {
                        'type': 'DataFrame',
                        'data': value.to_dict('records'),
                        'columns': list(value.columns),
                    }
                elif isinstance(value, pd.Series):
                    serializable_data[key] = {
                        'type': 'Series',
                        'data': value.to_dict(),
                    }
                else:
                    serializable_data[key] = value
            
            cache_data = {
                'stock_code': stock_code,
                'cache_time': datetime.now().isoformat(),
                'data': serializable_data,
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已缓存: {stock_code}")
            
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")
    
    def get_source_status(self) -> Dict[str, Any]:
        """获取数据源状态"""
        return self.source_status
