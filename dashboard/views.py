from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Q
from companies.models import DimCompany, DimSector, FactBalancesheet, FactProfitAndLoss, FactProsAndCons
from ml_engine.models import CompanyScore

def home_view(request):
    sectors = DimSector.objects.all()
    # Featured companies: select up to 6 outperformers
    featured_companies = DimCompany.objects.filter(companyscore__health_label='OUTPERFORM')[:6]
    
    # Materialize values to avoid Django Lazy Loading queries
    comp_list = []
    for c in featured_companies:
        comp_list.append({
            'symbol': c.symbol,
            'company_name': c.company_name,
            'company_logo': c.company_logo,
            'about_company': c.about_company,
            'roe_percentage': float(c.roe_percentage or 0)
        })

    return render(request, 'home.html', {
        'sectors': sectors,
        'featured_companies': comp_list
    })

def company_list_view(request):
    sectors = DimSector.objects.all()
    selected_sector = request.GET.get('sector', '')
    selected_health = request.GET.get('health', '')
    selected_sort = request.GET.get('sort', '')
    search_query = request.GET.get('search', '')

    companies_qs = DimCompany.objects.all()

    if selected_sector:
        companies_qs = companies_qs.filter(sector__sector_name=selected_sector)
    if selected_health:
        companies_qs = companies_qs.filter(companyscore__health_label=selected_health)
    if search_query:
        companies_qs = companies_qs.filter(Q(symbol__icontains=search_query) | Q(company_name__icontains=search_query))

    if selected_sort == 'roe':
        companies_qs = companies_qs.order_by('-roe_percentage')
    elif selected_sort == 'roce':
        companies_qs = companies_qs.order_by('-roce_percentage')
    elif selected_sort == 'book_value':
        companies_qs = companies_qs.order_by('-book_value')

    companies_list = []
    for c in companies_qs:
        try:
            score_obj = CompanyScore.objects.get(symbol=c)
            health_label = score_obj.health_label
        except:
            health_label = 'STABLE'
            
        companies_list.append({
            'symbol': c.symbol,
            'company_name': c.company_name,
            'sector_name': c.sector.sector_name if c.sector else 'Other',
            'roe_percentage': float(c.roe_percentage or 0),
            'roce_percentage': float(c.roce_percentage or 0),
            'book_value': float(c.book_value or 0),
            'health_label': health_label
        })

    return render(request, 'companies.html', {
        'sectors': sectors,
        'companies': companies_list,
        'selected_sector': selected_sector,
        'selected_health': selected_health,
        'selected_sort': selected_sort,
        'search_query': search_query
    })

def company_detail_view(request, symbol):
    company = get_object_or_404(DimCompany, symbol=symbol.upper())
    pros_cons = FactProsAndCons.objects.filter(symbol=company).first()
    
    # Materialize to float
    company_data = {
        'symbol': company.symbol,
        'company_name': company.company_name,
        'company_logo': company.company_logo,
        'about_company': company.about_company,
        'website': company.website,
        'nse_profile': company.nse_profile,
        'bse_profile': company.bse_profile,
        'chart_link': company.chart_link,
        'face_value': float(company.face_value or 0),
        'book_value': float(company.book_value or 0),
        'roce_percentage': float(company.roce_percentage or 0),
        'roe_percentage': float(company.roe_percentage or 0),
        'sector_name': company.sector.sector_name if company.sector else 'Other'
    }

    return render(request, 'company_detail.html', {
        'company': company_data,
        'pros_cons': pros_cons
    })

def compare_view(request):
    all_companies = DimCompany.objects.all().order_by('symbol')
    
    selected_symbols = []
    for i in "1234":
        sym = request.GET.get(f'c{i}', '')
        if sym:
            selected_symbols.append(sym.upper())

    comparison_data = []
    if selected_symbols:
        companies_qs = DimCompany.objects.filter(symbol__in=selected_symbols)
        for c in companies_qs:
            try:
                score_obj = CompanyScore.objects.get(symbol=c)
                health_score = float(score_obj.health_score)
                health_label = score_obj.health_label
            except:
                health_score = 50.0
                health_label = 'STABLE'

            latest_pl = FactProfitAndLoss.objects.filter(symbol=c).order_by('-year__sort_order').first()
            opm_val = float(latest_pl.opm_percentage or 0) if latest_pl else 0.0

            latest_bs = FactBalancesheet.objects.filter(symbol=c).order_by('-year__sort_order').first()
            de_val = float(latest_bs.debt_to_equity or 0) if latest_bs else 0.0

            comparison_data.append({
                'symbol': c.symbol,
                'company_name': c.company_name,
                'sector_name': c.sector.sector_name if c.sector else 'Other',
                'health_score': health_score,
                'health_label': health_label,
                'roe_percentage': float(c.roe_percentage or 0),
                'roce_percentage': float(c.roce_percentage or 0),
                'book_value': float(c.book_value or 0),
                'face_value': float(c.face_value or 0),
                'opm_percentage': opm_val,
                'debt_to_equity': de_val
            })

    return render(request, 'compare.html', {
        'all_companies': all_companies,
        'selected_symbols': selected_symbols,
        'comparison_data': comparison_data
    })

def screener_view(request):
    sectors = DimSector.objects.all()
    
    min_roe = request.GET.get('min_roe', '')
    max_de = request.GET.get('max_de', '')
    selected_sector = request.GET.get('sector', '')
    selected_health = request.GET.get('health', '')

    companies_qs = DimCompany.objects.all()

    if selected_sector:
        companies_qs = companies_qs.filter(sector__sector_name=selected_sector)
    if selected_health:
        companies_qs = companies_qs.filter(companyscore__health_label=selected_health)
    if min_roe:
        companies_qs = companies_qs.filter(roe_percentage__gte=float(min_roe))

    screened_companies = []
    for c in companies_qs:
        # Check debt-to-equity filter
        latest_bs = FactBalancesheet.objects.filter(symbol=c).order_by('-year__sort_order').first()
        de_val = float(latest_bs.debt_to_equity or 0) if latest_bs else 0.0
        
        if max_de and de_val > float(max_de):
            continue

        try:
            score_obj = CompanyScore.objects.get(symbol=c)
            health_label = score_obj.health_label
        except:
            health_label = 'STABLE'

        screened_companies.append({
            'symbol': c.symbol,
            'company_name': c.company_name,
            'sector_name': c.sector.sector_name if c.sector else 'Other',
            'roe_percentage': float(c.roe_percentage or 0),
            'debt_to_equity': de_val,
            'health_label': health_label
        })

    return render(request, 'screener.html', {
        'sectors': sectors,
        'screened_companies': screened_companies,
        'min_roe': min_roe,
        'max_de': max_de,
        'selected_sector': selected_sector,
        'selected_health': selected_health
    })

def sector_view(request, name):
    companies_qs = DimCompany.objects.filter(sector__sector_name=name)
    
    companies_list = []
    for c in companies_qs:
        try:
            score_obj = CompanyScore.objects.get(symbol=c)
            health_label = score_obj.health_label
        except:
            health_label = 'STABLE'

        companies_list.append({
            'symbol': c.symbol,
            'company_name': c.company_name,
            'roe_percentage': float(c.roe_percentage or 0),
            'roce_percentage': float(c.roce_percentage or 0),
            'book_value': float(c.book_value or 0),
            'health_label': health_label
        })

    avg_stats = companies_qs.aggregate(
        avg_roe=Avg('roe_percentage'),
        avg_roce=Avg('roce_percentage')
    )

    return render(request, 'sector.html', {
        'sector_name': name,
        'companies': companies_list,
        'avg_roe': avg_stats.get('avg_roe') or 0.0,
        'avg_roce': avg_stats.get('avg_roce') or 0.0
    })
