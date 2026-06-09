from django.db import models
from companies.models import DimCompany

class CompanyScore(models.Model):
    symbol = models.OneToOneField(DimCompany, models.DO_NOTHING, primary_key=True, db_column='symbol')
    health_score = models.DecimalField(max_digits=5, decimal_places=2)
    health_label = models.CharField(max_length=20)
    profitability_score = models.DecimalField(max_digits=5, decimal_places=2)
    growth_score = models.DecimalField(max_digits=5, decimal_places=2)
    solvency_score = models.DecimalField(max_digits=5, decimal_places=2)
    liquidity_score = models.DecimalField(max_digits=5, decimal_places=2)
    efficiency_score = models.DecimalField(max_digits=5, decimal_places=2)
    scale_score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'ml_company_score'
        managed = False

class AnomalyFlag(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column='symbol')
    year_str = models.CharField(max_length=20)
    sales = models.DecimalField(max_digits=15, decimal_places=2)
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=4)
    anomaly_reason = models.TextField()

    class Meta:
        db_table = 'ml_anomaly_flag'
        managed = False

class PeerGroup(models.Model):
    symbol = models.OneToOneField(DimCompany, models.DO_NOTHING, primary_key=True, db_column='symbol', related_name='peer_group')
    peer_1 = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column='peer_1', related_name='peer_1_of')
    peer_2 = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column='peer_2', related_name='peer_2_of')
    peer_3 = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column='peer_3', related_name='peer_3_of')

    class Meta:
        db_table = 'ml_peer_group'
        managed = False

class SalesForecast(models.Model):
    symbol = models.OneToOneField(DimCompany, models.DO_NOTHING, primary_key=True, db_column='symbol')
    current_year = models.IntegerField()
    current_sales = models.DecimalField(max_digits=15, decimal_places=2)
    forecast_year = models.IntegerField()
    forecasted_sales = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        db_table = 'ml_sales_forecast'
        managed = False
