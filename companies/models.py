from django.db import models

class DimSector(models.Model):
    sector_name = models.CharField(max_length=100, primary_key=True, db_column='sector_name')
    sector_desc = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'dim_sector'
        managed = False

    def __str__(self):
        return self.sector_name

class DimCompany(models.Model):
    symbol = models.CharField(max_length=50, primary_key=True, db_column='symbol')
    company_name = models.CharField(max_length=255)
    company_logo = models.TextField(blank=True, null=True)
    chart_link = models.TextField(blank=True, null=True)
    about_company = models.TextField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    nse_profile = models.TextField(blank=True, null=True)
    bse_profile = models.TextField(blank=True, null=True)
    face_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    book_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    roce_percentage = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    roe_percentage = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    sector = models.ForeignKey(DimSector, models.DO_NOTHING, db_column='sector_name', blank=True, null=True)
    is_banking = models.BooleanField(default=False)

    class Meta:
        db_table = 'dim_company'
        managed = False

    def __str__(self):
        return f"{self.symbol} - {self.company_name}"

class DimYear(models.Model):
    year_str = models.CharField(max_length=20, primary_key=True, db_column='year_str')
    sort_order = models.IntegerField()
    is_ttm = models.BooleanField(default=False)

    class Meta:
        db_table = 'dim_year'
        managed = False

    def __str__(self):
        return self.year_str

class FactBalancesheet(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column='symbol')
    year = models.ForeignKey(DimYear, models.DO_NOTHING, db_column='year_str')
    equity_capital = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    reserves = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    borrowings = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    other_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    fixed_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    cwip = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    investments = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    other_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    total_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = 'fact_balancesheet'
        managed = False

class FactProfitAndLoss(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column='symbol')
    year = models.ForeignKey(DimYear, models.DO_NOTHING, db_column='year_str')
    sales = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    expenses = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    operating_profit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    opm_percentage = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    other_income = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    interest = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    depreciation = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    profit_before_tax = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    tax_percentage = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    eps = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dividend_payout = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    net_profit_margin_pct = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = 'fact_profitandloss'
        managed = False

class FactCashflow(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column='symbol')
    year = models.ForeignKey(DimYear, models.DO_NOTHING, db_column='year_str')
    operating_activity = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    investing_activity = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    financing_activity = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    net_cash_flow = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    free_cash_flow = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'fact_cashflow'
        managed = False

class FactAnalysis(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column='symbol')
    compounded_sales_growth = models.TextField(blank=True, null=True)
    compounded_profit_growth = models.TextField(blank=True, null=True)
    stock_price_cagr = models.TextField(blank=True, null=True)
    roe = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'fact_analysis'
        managed = False

class FactProsAndCons(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column='symbol')
    pros = models.TextField(blank=True, null=True)
    cons = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'fact_prosandcons'
        managed = False

class FactDocuments(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column='symbol')
    year_int = models.IntegerField()
    annual_report_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'fact_documents'
        managed = False
