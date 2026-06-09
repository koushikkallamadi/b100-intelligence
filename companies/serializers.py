from rest_framework import serializers
from companies.models import (
    DimCompany, DimSector, DimYear, FactBalancesheet,
    FactProfitAndLoss, FactCashflow, FactAnalysis, FactProsAndCons, FactDocuments
)
from ml_engine.models import CompanyScore, SalesForecast, PeerGroup

class DimSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimSector
        fields = '__all__'

class DimYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimYear
        fields = '__all__'

class FactBalancesheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactBalancesheet
        fields = '__all__'

class FactProfitAndLossSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactProfitAndLoss
        fields = '__all__'

class FactCashflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactCashflow
        fields = '__all__'

class FactAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactAnalysis
        fields = '__all__'

class FactProsAndConsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactProsAndCons
        fields = '__all__'

class FactDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactDocuments
        fields = '__all__'

class CompanyScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyScore
        fields = '__all__'

class SalesForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesForecast
        fields = '__all__'

class DimCompanySerializer(serializers.ModelSerializer):
    sector = DimSectorSerializer(read_only=True)
    score = CompanyScoreSerializer(source='companyscore', read_only=True)
    
    class Meta:
        model = DimCompany
        fields = '__all__'

class CompanyDetailsSerializer(serializers.ModelSerializer):
    sector = DimSectorSerializer(read_only=True)
    balancesheets = FactBalancesheetSerializer(source='factbalancesheet_set', many=True, read_only=True)
    profitandloss = FactProfitAndLossSerializer(source='factprofitandloss_set', many=True, read_only=True)
    cashflows = FactCashflowSerializer(source='factcashflow_set', many=True, read_only=True)
    analysis = FactAnalysisSerializer(source='factanalysis_set', many=True, read_only=True)
    prosandcons = FactProsAndConsSerializer(source='factprosandcons_set', many=True, read_only=True)
    documents = FactDocumentsSerializer(source='factdocuments_set', many=True, read_only=True)
    score = CompanyScoreSerializer(source='companyscore', read_only=True)
    forecast = SalesForecastSerializer(source='salesforecast', read_only=True)
    
    class Meta:
        model = DimCompany
        fields = '__all__'
