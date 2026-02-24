import pandas as pd


host_country_map = {
    # 하계 올림픽
    'Athina': 'GRE',
    'Paris': 'FRA',
    'St. Louis': 'USA',
    'London': 'GBR',
    'Stockholm': 'SWE',
    'Antwerpen': 'BEL',
    'Amsterdam': 'NED',
    'Los Angeles': 'USA',
    'Berlin': 'GER',
    'Helsinki': 'FIN',
    'Melbourne': 'AUS',
    'Roma': 'ITA',
    'Tokyo': 'JPN',
    'Mexico City': 'MEX',
    'Munich': 'GER', 
    'Montreal': 'CAN',
    'Moskva': 'RUS', 
    'Seoul': 'KOR',
    'Barcelona': 'ESP',
    'Atlanta': 'USA',
    'Sydney': 'AUS',
    'Beijing': 'CHN',
    'Rio de Janeiro': 'BRA',

    # 동계 올림픽
    'Chamonix': 'FRA',
    'Sankt Moritz': 'SUI',
    'Lake Placid': 'USA',
    'Garmisch-Partenkirchen': 'GER',
    'Oslo': 'NOR',
    'Cortina d\'Ampezzo': 'ITA',
    'Squaw Valley': 'USA',
    'Innsbruck': 'AUT',
    'Grenoble': 'FRA',
    'Sapporo': 'JPN',
    'Sarajevo': 'YUG',
    'Calgary': 'CAN',
    'Albertville': 'FRA',
    'Lillehammer': 'NOR',
    'Nagano': 'JPN',
    'Salt Lake City': 'USA',
    'Torino': 'ITA',
    'Vancouver': 'CAN',
    'Sochi': 'RUS'
}

def load_olympic():
    olympic_df = pd.read_csv('data/athlete_events.csv')
    olympic_df['host_NOC'] = olympic_df['City'].map(host_country_map)
    olympic_df['is_host'] = olympic_df['NOC'] == olympic_df['host_NOC']
    return olympic_df.drop_duplicates()

def get_noc_region_map():
    noc_df = pd.read_csv('data/noc_regions.csv')
    return noc_df.set_index('NOC')['region'].to_dict()

# NOC(Olympic) -> ISO-3(World Bank) 매핑
noc_to_iso = {
    'GER': 'DEU', 'ALG': 'DZA', 'NED': 'NLD', 'SUI': 'CHE',
    'GRE': 'GRC', 'KSA': 'SAU', 'RSA': 'ZAF', 'BRN': 'BHR',
    'INA': 'IDN', 'IRI': 'IRN', 'DEN': 'DNK', 'ESA': 'SLV',
    'LAT': 'LVA', 'MAS': 'MYS', 'MYA': 'MMR', 'NGR': 'NGA',
    'POR': 'PRT', 'VIE': 'VNM', 'ZIM': 'ZWE', 'CHI': 'CHL',
    'CRO': 'HRV', 'GRN': 'GRD', 'HAI': 'HTI', 'ISL': 'ISL', # ISL은 동일
    'KUW': 'KWT', 'LIB': 'LBN', 'MAW': 'MWI', 'MON': 'MCO',
    'PAR': 'PRY', 'PHI': 'PHL', 'PUR': 'PRI', 'ROC': 'TWN', # 대만(ROC) 주의
    'SRI': 'LKA', 'SUD': 'SDN', 'TPE': 'TWN', 'URU': 'URY',

    # 역사적 변동 및 특수 케이스
    'URS': 'RUS',  # 구소련 -> 러시아 (경제 데이터 연속성을 위해)
    'FRG': 'DEU',  # 서독 -> 독일
    'GDR': 'DEU',  # 동독 -> 독일
    'ROU': 'ROU',  # 루마니아 (ROM에서 ROU로 변경됨)
    'TCH': 'CZE',  # 체코슬로바키아 -> 체코 (데이터 가용성에 따라 선택)
    'YUG': 'SRB',  # 유고슬라비아 -> 세르비아
    'EUA': 'DEU',  # 독일 단일팀

    # ISO와 NOC가 같아서 누락되기 쉬운 주요국 (명시적 포함)
    'USA': 'USA', 'FRA': 'FRA', 'GBR': 'GBR', 'ITA': 'ITA',
    'JPN': 'JPN', 'KOR': 'KOR', 'CHN': 'CHN', 'CAN': 'CAN',
    'AUS': 'AUS', 'ESP': 'ESP', 'BRA': 'BRA', 'IND': 'IND'
}


def load_gdp():
    olympic_df = load_olympic()
    gdp_df = pd.read_csv('data/world_gdp.csv')

    # 2. World Bank 데이터(wb_df)에서 해당 연도만 필터링
    olympic_years = [ str(y) for y in sorted(olympic_df['Year'].unique())]
    id_vars = ['Country Name', 'Country Code']
    available_years = [y for y in olympic_years if y in gdp_df.columns]
    gdp_subset = gdp_df[id_vars + available_years]
    gdp_long = gdp_subset.melt(
        id_vars=id_vars,
        var_name='Year',
        value_name='GDP'
    )

    # 6. 데이터 타입 맞추기 (Year를 int로 변환해야 올림픽 df와 합칠 수 있음)
    gdp_long['Year'] = gdp_long['Year'].astype(int)

    # 3. NOC 코드 추가
    iso_to_noc = {v: k for k, v in noc_to_iso.items()}
    gdp_long['NOC'] = gdp_long['Country Code'].map(iso_to_noc)
    gdp_long['NOC'] = gdp_long['NOC'].fillna(gdp_long['Country Code'])
    return gdp_long

def load_population():
    olympic_df = load_olympic()
    pop_df = pd.read_csv('data/world_population.csv')

    # 2. World Bank 데이터(wb_df)에서 해당 연도만 필터링
    olympic_years = [ str(y) for y in sorted(olympic_df['Year'].unique())]
    id_vars = ['Country Name', 'Country Code']
    available_years = [y for y in olympic_years if y in pop_df.columns]
    pop_subset = pop_df[id_vars + available_years]
    pop_long = pop_subset.melt(
        id_vars=id_vars,
        var_name='Year',
        value_name='population'
    )

    # 6. 데이터 타입 맞추기 (Year를 int로 변환해야 올림픽 df와 합칠 수 있음)
    pop_long['Year'] = pop_long['Year'].astype(int)
    iso_to_noc = {v: k for k, v in noc_to_iso.items()}
    pop_long['NOC'] = pop_long['Country Code'].map(iso_to_noc)
    pop_long['NOC'] = pop_long['NOC'].fillna(pop_long['Country Code'])
    return pop_long

def get_economic_indicators():
    gdp = load_gdp()
    pop = load_population()

    # GDP와 인구 데이터 병합
    econ_df = pd.merge(gdp, pop[['Country Code', 'Year', 'population']],
                       on=['Country Code', 'Year'], how='inner')

    # 1인당 GDP 계산
    econ_df['gdp_per_capita'] = econ_df['GDP'] / econ_df['population']
    return econ_df

def get_medal_counts(olympic_df):
    # 단체전 메달 중복 제거 (Year, Event, Medal, NOC가 같으면 하나로 취급)
    medals = olympic_df.dropna(subset=['Medal']).copy()
    medals = medals.drop_duplicates(subset=['Year', 'Season', 'Event', 'NOC', 'Medal'])

    # 국가별/연도별 메달 합산
    medal_counts = medals.groupby(['Year', 'NOC'])['Medal'].count().reset_index()
    return medal_counts


def apply_noc_mapping(df):
    """
    GDP/인구 데이터프레임에 NOC 코드를 부여하는 공통 로직
    """
    # 1. 사전 매핑 적용
    iso_to_noc = {v: k for k, v in noc_to_iso.items()}
    df['NOC'] = df['Country Code'].map(iso_to_noc)

    # 2. 매핑되지 않은 경우, ISO 코드(Country Code)를 NOC로 그대로 사용
    # (많은 국가가 ISO-3와 NOC가 동일함)
    df['NOC'] = df['NOC'].fillna(df['Country Code'])

    return df


def check_missing_economics(olympic_df, econ_df):
    """
    올림픽 참여국 중 경제 데이터가 없는 국가 목록을 반환합니다.
    """
    olympic_nocs = set(olympic_df['NOC'].unique())
    econ_nocs = set(econ_df['NOC'].unique())

    missing = olympic_nocs - econ_nocs
    print(f"경제 데이터가 없는 NOC 개수: {len(missing)}")
    return sorted(list(missing))


def get_final_analysis_df():
    """
    올림픽 메달 데이터와 경제 지표를 결합하여
    분석에 즉시 사용 가능한 최종 DataFrame을 반환합니다.
    """
    # 1. 원본 데이터 로드
    olympic = load_olympic()

    # 2. 메달 집계 (단체전 중복 제거 로직 포함)
    medals = get_medal_counts(olympic)

    # 3. 경제 지표 로드 (1인당 GDP 포함)
    econ = get_economic_indicators()

    # 4. 개최국 정보 유지를 위한 병합
    # olympic에서 국가별/연도별 개최 여부 매핑 정보만 추출
    host_info = olympic[['Year', 'NOC', 'is_host']].drop_duplicates()

    # 5. 데이터 통합 (Medal + Econ + Host_Info)
    # 경제 데이터가 있는 연도(주로 1960년 이후) 위주로 inner join
    final_df = pd.merge(medals, econ, on=['Year', 'NOC'], how='inner')
    final_df = pd.merge(final_df, host_info, on=['Year', 'NOC'], how='left')

    # 개최국 정보가 없는 경우 False로 채움
    final_df['is_host'] = final_df['is_host'].fillna(False)

    return final_df

if __name__ == '__main__':
    olympic = load_olympic()
    print(olympic[olympic['Year'] > 2000].info())
    noc_region = get_noc_region_map()
    print(noc_region['AUS'])