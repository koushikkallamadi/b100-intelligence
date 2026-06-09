import os
import re
import numpy as np
import pandas as pd
from celery import shared_task
from django.db import connection, transaction
from companies.models import DimCompany, FactProfitAndLoss, FactBalancesheet
from ml_engine.models import CompanyScore, AnomalyFlag

@shared_task
def calculate_health_scores_task():
    """
    Celery task wrapper to compute 6-dimension financial health scores 
    and update the ml_company_score database table.
    """
    print("Celery task: Calculating health scores...")
    
    # 1. Fetch data from DB
    companies = list(DimCompany.objects.all().values())
    profitloss = list(FactProfitAndLoss.objects.all().values())
    balancesheet = list(FactBalancesheet.objects.all().values())
    
    if not companies or not profitloss or not balancesheet:
        print("[WARNING] Celery task aborted: Empty tables.")
        return "Aborted: Empty database tables."
    
    df_comp = pd.DataFrame(companies)
    df_pl = pd.DataFrame(profitloss)
    df_bs = pd.DataFrame(balancesheet)
    
    # Rename columns to match dataframe operations
    df_pl.rename(columns={"symbol_id": "symbol", "year_id": "year_str"}, inplace=True)
    df_bs.rename(columns={"symbol_id": "symbol", "year_id": "year_str"}, inplace=True)
    
    # 2. Score calculations
    pl_median = df_pl.groupby('symbol')[['sales', 'net_profit', 'opm_percentage', 'net_profit_margin_pct', 'eps']].median().reset_index()
    bs_median = df_bs.groupby('symbol')[['borrowings', 'reserves', 'equity_capital', 'debt_to_equity']].median().reset_index()
    
    score_df = pl_median.merge(bs_median, on='symbol').merge(df_comp[['symbol', 'roce_percentage', 'roe_percentage', 'is_banking']], on='symbol')
    
    # Cast to numeric to avoid decimal type issues in pandas ops
    score_df['roe_percentage'] = pd.to_numeric(score_df['roe_percentage'], errors='coerce')
    score_df['roce_percentage'] = pd.to_numeric(score_df['roce_percentage'], errors='coerce')
    score_df['net_profit_margin_pct'] = pd.to_numeric(score_df['net_profit_margin_pct'], errors='coerce')
    score_df['debt_to_equity'] = pd.to_numeric(score_df['debt_to_equity'], errors='coerce')
    score_df['reserves'] = pd.to_numeric(score_df['reserves'], errors='coerce')
    score_df['opm_percentage'] = pd.to_numeric(score_df['opm_percentage'], errors='coerce')
    score_df['sales'] = pd.to_numeric(score_df['sales'], errors='coerce')
    
    def score_metric(series, ascending=True):
        series = series.fillna(series.median())
        min_val, max_val = series.min(), series.max()
        if max_val == min_val:
            return series * 0 + 50
        if ascending:
            return ((series - min_val) / (max_val - min_val)) * 100
        else:
            return ((max_val - series) / (max_val - min_val)) * 100

    score_df['profitability_score'] = score_metric(score_df['roe_percentage']) * 0.5 + score_metric(score_df['roce_percentage']) * 0.5
    score_df['growth_score'] = score_metric(score_df['net_profit_margin_pct'])
    score_df['solvency_score'] = np.where(score_df['is_banking'], 80.0, score_metric(score_df['debt_to_equity'], ascending=False))
    score_df['liquidity_score'] = score_metric(score_df['reserves'])
    score_df['efficiency_score'] = score_metric(score_df['opm_percentage'])
    score_df['scale_score'] = score_metric(score_df['sales'])
    
    score_df['health_score'] = (
        score_df['profitability_score'] * 0.25 +
        score_df['growth_score'] * 0.15 +
        score_df['solvency_score'] * 0.20 +
        score_df['liquidity_score'] * 0.15 +
        score_df['efficiency_score'] * 0.15 +
        score_df['scale_score'] * 0.10
    )
    
    score_df['health_label'] = pd.cut(
        score_df['health_score'],
        bins=[0, 45, 70, 100],
        labels=['UNDERPERFORM', 'STABLE', 'OUTPERFORM']
    )
    
    # 3. Save directly to DB via bulk creation
    with transaction.atomic():
        # Clear existing
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE ml_company_score CASCADE;")
        
        # Insert
        insert_objs = []
        for idx, row in score_df.iterrows():
            insert_objs.append(
                CompanyScore(
                    symbol_id=row['symbol'],
                    health_score=row['health_score'],
                    health_label=str(row['health_label']),
                    profitability_score=row['profitability_score'],
                    growth_score=row['growth_score'],
                    solvency_score=row['solvency_score'],
                    liquidity_score=row['liquidity_score'],
                    efficiency_score=row['efficiency_score'],
                    scale_score=row['scale_score']
                )
            )
        CompanyScore.objects.bulk_create(insert_objs)
    
    # Trigger webhook event (hooked in Week 7)
    try:
        from api_management.utils import dispatch_webhook_event
        dispatch_webhook_event('score_updated', {'message': 'Health scores recalculated successfully.'})
    except ImportError:
        pass
        
    return f" Recalculated health scores for {len(score_df)} companies."


@shared_task
def detect_anomalies_task():
    """
    Celery task wrapper to detect financial reporting anomalies (Z-score outliers)
    and update the ml_anomaly_flag database table.
    """
    print("Celery task: Detecting anomalies...")
    
    profitloss = list(FactProfitAndLoss.objects.all().values())
    balancesheet = list(FactBalancesheet.objects.all().values())
    
    if not profitloss or not balancesheet:
        print("[WARNING] Celery task aborted: Empty tables.")
        return "Aborted: Empty database tables."
        
    df_pl = pd.DataFrame(profitloss)
    df_bs = pd.DataFrame(balancesheet)
    
    df_pl.rename(columns={"symbol_id": "symbol", "year_id": "year_str"}, inplace=True)
    df_bs.rename(columns={"symbol_id": "symbol", "year_id": "year_str"}, inplace=True)
    
    df_annual = df_pl.merge(df_bs, on=['symbol', 'year_str'])
    
    df_annual['net_profit_margin_pct'] = pd.to_numeric(df_annual['net_profit_margin_pct'], errors='coerce')
    df_annual['debt_to_equity'] = pd.to_numeric(df_annual['debt_to_equity'], errors='coerce')
    df_annual['sales'] = pd.to_numeric(df_annual['sales'], errors='coerce')
    
    def get_zscores(series):
        mean = series.mean()
        std = series.std()
        if std == 0:
            return series * 0
        return (series - mean) / std

    df_annual['z_npm'] = get_zscores(df_annual['net_profit_margin_pct'].fillna(0))
    df_annual['z_de'] = get_zscores(df_annual['debt_to_equity'].fillna(0))
    
    df_annual['is_anomaly'] = np.where((np.abs(df_annual['z_npm']) > 3) | (np.abs(df_annual['z_de']) > 3), 1, 0)
    
    anomalies = df_annual[df_annual['is_anomaly'] == 1].copy()
    
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE ml_anomaly_flag CASCADE;")
            
        insert_objs = []
        for idx, row in anomalies.iterrows():
            insert_objs.append(
                AnomalyFlag(
                    symbol_id=row['symbol'],
                    year_str=row['year_str'],
                    sales=row['sales'],
                    debt_to_equity=row['debt_to_equity'],
                    anomaly_reason="Extreme outlier detected in Net Profit Margin or Debt-to-Equity ratio"
                )
            )
        AnomalyFlag.objects.bulk_create(insert_objs)
        
    try:
        from api_management.utils import dispatch_webhook_event
        dispatch_webhook_event('anomaly_flagged', {'count': len(anomalies)})
    except ImportError:
        pass
        
    return f" Detected and recorded {len(anomalies)} anomalies."
