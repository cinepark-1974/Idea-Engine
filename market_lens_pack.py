"""
Market Lens Pack v1.0
BLUE JEANS PICTURES · Idea Engine v1.4 신규 모듈

target_market 입력에 따라 시장별 진단 좌표를 동적으로 주입한다.
Stage 4 (포맷·장르·시장 좌표) / Stage 5 (레퍼런스) / Stage 6 (Market 진단)
프롬프트가 시장 중립적으로 작동하도록 시장 프로필을 외부에서 공급한다.

[지원 시장]
  KR — 한국 (기본값, 현재 동작 보존)
  JP — 일본 (JP_DOC 모드 — 3트랙 외 0점 처리)
  ID — 인도네시아 (JAFF Market·이슬람 문화 제약 반영)

[매핑 규칙]
  target_market 문자열에 포함된 키워드로 자동 매핑.
  복수 시장 감지 시 1차·2차 듀얼 렌즈 호출.
  명시 없음 → KR 기본값.

[관련 문서]
  IDEA_ENGINE_SPEC.md (v1.4 섹션)
  Creator Engine v2.5.3 (LOCKED 47키)
"""


# ============================================================================
# 1. 한국 시장 (KR) — 기본값
# ============================================================================

KR_LENS = """
[시장 정체]
- 박스오피스 약 1.2조원 (2024) / 관객 약 1억 2천만 / 로컬 점유율 50%대.
- 손익분기 통화 = 손익분기 관객수 (약 100~150만). 극장 + OTT 동시 회수 구조.

[흥행 장르]
- 상위: CRIME · SOCIAL · HORROR(오컬트·무속) · DISASTER · PERIOD · COMEDY.
- 기피: 슬래셔 · B급 호러 · 멜로 단독 (단, 작품성 있는 멜로는 GENRE_FEATURE 가능).
- 핵심 특징: 사회파+장르 결합이 글로벌 K-콘텐츠의 핵심 (〈오징어게임〉〈기생충〉).

[구매자 좌표 4분류]
- TENTPOLE: CJ ENM · 쇼박스 · NEW · 롯데엔터테인먼트 · 플러스엠 (50~150억 제작비).
- MASTERCLASS: 박찬욱 · 봉준호 · 이창동 · 나홍진 · 김지운 사단 / 모호필름 · 바른손이앤에이.
- STREAMING: Netflix Korea · Tving · Wavve · Coupang Play · Disney+ Korea.
- GENRE_FEATURE: 중소 제작사 · OTT 영화 · CGV 아트하우스 · 인디스토리.

[표준작 좌표 (한국 10장르 매핑)]
- CRIME: 〈범죄도시〉〈베테랑〉〈서울의 봄〉〈마더〉
- ACTION: 〈신세계〉〈아수라〉〈탈주〉〈모가디슈〉
- HORROR: 〈장화홍련〉〈곡성〉〈파묘〉〈검은 사제들〉
- COMEDY: 〈극한직업〉〈수상한 그녀〉〈럭키〉
- MELO: 〈오랜만에〉〈건축학개론〉〈8월의 크리스마스〉
- PERIOD: 〈명량〉〈관상〉〈사도〉〈남한산성〉〈국제시장〉
- DRAMA: 〈박하사탕〉〈버닝〉〈변호인〉〈1987〉
- FANTASY: 〈도깨비〉〈호텔 델루나〉〈승리호〉
- DISASTER: 〈해운대〉〈터널〉〈부산행〉〈싱크홀〉
- SOCIAL: 〈오징어게임〉〈더 글로리〉〈지옥〉〈마스크걸〉〈기생충〉

[문화 제약]
- 정치 검열 거의 없음. 종교 영향 적음. 표현 수위 폭넓음.
- 사회파 비판 가능. 식민·전쟁·민주화 직설 가능.

[공동제작 트랙]
- KOFIC 한국영화기획개발 지원
- 부산국제영화제 ACFM (Asian Contents & Film Market)

[진단 원칙]
- 한국 시장은 Idea Engine의 기본 좌표. 모든 진단 가능.
- domestic_market = 한국. global_market = 한국 외 (일본·미국·유럽·동남아).
"""


# ============================================================================
# 2. 일본 시장 (JP) — JP_DOC 좁힘 모드
# ============================================================================

JP_LENS = """
[시장 정체]
- 박스오피스 2069억엔 (2024) / 관객 1억 4441만 / 로컬 점유율 75.3% (자국 강세).
- 2024년 흥행 Top 10 중 8편이 일본 영화, 그 중 7편이 만화/애니메이션 원작.
- 한국 외부 기획자에게 사실상 닫힌 시장 — 3개 진입 트랙만 가능.

[중요 — JP_DOC 좁힘 모드]
한국에서 일본 메이저 시장에 오리지널 실사 영화로 진입하는 트랙은 없다.
도호·쇼치쿠·토에이의 제작위원회 시스템과 만화 원작 IP 의존 구조가 외부 진입을 차단한다.
따라서 일본 시장 진단은 아래 3트랙 중 하나에 해당하는지를 검증한다.
3트랙 어디에도 해당하지 않으면 일본 시장 stars = 0으로 강제 처리한다.

[일본 진입 3트랙]

트랙 1 — INDIE_ARTHOUSE (일본 인디·아트하우스 영화제 트랙)
  진입 조건:
    - 작가주의 시나리오 / 영화제 트랙 명확
    - 자주제작 가능 예산 (5,000만엔 이하 또는 한일 인디 공동 펀딩)
    - 도쿄국제영화제 · 오사카아시안영화제 · TOKYO FILMeX 출품 가능성
  레퍼런스: 〈사무라이 타임 슬리퍼〉(자주제작 2,600만엔 → 10억엔 흥행) · 〈드라이브 마이 카〉 · 고레에다 사단 · 하마구치 류스케 사단
  지원금: 문화청 문진보조금 (극영화 1,500만엔 이상, 신진 감독 우대)

트랙 2 — KR_REMAKE_TARGET (한국 흥행작 일본 리메이크 가능성)
  진입 조건:
    - 한국에서 흥행 검증된 원작 (또는 검증 가능성 명확)
    - 일본 정서 이식 가능성 (혼네/타테마에 문화 · 가족 단위 정서)
    - 만화 원작으로 변환 가능한 구조 (선택적)
  레퍼런스: 〈수상한 그녀〉→〈あやしい彼女〉 · 〈7번방의 선물〉→〈ミラクル7号〉

트랙 3 — COPROD_VIPO (국제공동제작 — VIPO · 유니재팬 · 문화청)
  진입 조건:
    - 일본 측 공동제작사 확보 (제작비 분담 명확)
    - 일본 로케이션 또는 일본 인물·역사 핵심 모티프
    - 유니재팬 "국제공동제작" 인정 가능 + 문화청 5,000만엔 한도 지원
  레퍼런스: 〈브로커〉(한일 공동제작 변형 모델) · VIPO Film Lab 트랙

[3트랙 외 0점 처리]
위 3트랙 중 어디에도 명확히 해당하지 않으면:
  - 일본 시장 stars = 0
  - risk_signals에 "한국 외부 기획이 일본 메이저 시장에 오리지널 실사로 진입하는 트랙은 존재하지 않음" 명시
  - 진단 결론: "일본 시장 타겟을 제외하거나, 3트랙 중 하나로 작품 재설계 권고"

[기피 사항]
- 한국식 SOCIAL 직설 비판 메시지 (혼네/타테마에 문화와 충돌)
- 자극적 폭력 · 슬래셔 · 노골적 성표현
- 정치 직설 (특히 한일 관계 직격)

[OTT 진입 — 부수 좌표]
- Netflix Japan (점유율 21.5%) — 한국 콘텐츠 직배는 활발하나, 일본 오리지널 한국 기획은 드묾.
- U-NEXT (17.9%) — 애니메이션·일본 콘텐츠 강세, 한국 외부 진입 제한적.
- 본 진단에서는 OTT 단독 트랙으로 인정하지 않음 (TRACK_OTT는 INDIE 또는 COPROD에 포함).
"""


# ============================================================================
# 3. 인도네시아 시장 (ID) — JAFF Market 트랙
# ============================================================================

ID_LENS = """
[시장 정체]
- 자국영화 관객 8천만 명 (2024) / 점유율 65% / 2022~2024 박스오피스 회복 후 성장세.
- 외국인 투자 100% 가능 (2016년 법 개정). CJ ENM · 쇼박스 · 바른손이앤에이 진출 사례.
- 신흥 영화제작 인력 풀 확대 — 호러 · 코미디 · 액션 다양한 장르 감독 약진.

[흥행 장르]
- 압도적 1위: HORROR (Supernatural Well-made Horror · 자바 신앙 기반)
- 2위: COMEDY (스탠드업 출신 감독들 — Bayu Skak · Ernest Prakasa · Bene Dion)
- 3위: ROMANCE (이슬람 로맨스 · 청춘 로맨스, 핍진성 요구)
- 4위: FANTASY (Supernatural · Character 중심)
- 한국 작품 리메이크 흥행: 〈Sweet 20〉(수상한 그녀) · 〈Miracle in Cell No. 7〉

[구매자 좌표]
- TENTPOLE: Rapi Films · MD Pictures · Falcon Pictures · BASE Entertainment · Visinema
- MASTERCLASS: Joko Anwar · Mouly Surya · Garin Nugroho 사단 / NETPAC 트랙
- STREAMING: Netflix Indonesia/SEA · Disney+ Hotstar SEA · Vidio · Vision+ · WeTV
- GENRE_FEATURE: 인디 영화 + JAFF Future Project

[표준작]
- HORROR: 〈Pengabdi Setan〉(2017/2022, Joko Anwar) · 〈KKN di Desa Penari〉(2022) · 〈Siksa Kubur〉(2024) · 〈Malam Pencabut Nyawa〉(2024)
- COMEDY: 〈Cado Cado: Doctor 101〉 · 〈Cek Toko Sebelah〉
- ROMANCE: 〈Cinta Tak Pernah Tepat Waktu〉(2025) · 〈Dilan 1990〉
- 한국 리메이크: 〈Sweet 20〉(2017) · 〈Miracle in Cell No. 7〉(2022, 5백만 명 흥행)
- 한국-인니 공동제작: 〈Keadilan: The Verdict〉(2025, 이창희 감독·송현주 제작·윤현호 각본)

[문화 제약]
- 이슬람 문화 — LSF (영화검열위원회) 통과 필수.
- 직설적 이슬람 비판 불가. 이슬람을 우호적·중립적으로 다루면 OK.
- 노골적 성표현 · LGBT 노출 · 음주·도박 미화 회피.
- 라마단 기간 출시 회피. 라마단 직후 이둘피트리는 가족영화 황금기.
- 호러는 7~8월 출시 선호 (라마단 회피 + 학교 방학).
- 자바 vs 자카르타 vs 외도서 (수마트라·발리·술라웨시) 관객 분리 — 자바 케자웬 신앙·VOC 역사 묘사 정확성 필수.
- 한국 제작진 단독 진입 시 "문화 전용(cultural appropriation)" 리스크 — SNS 보이콧이 동남아 배급 봉쇄로 이어질 수 있음.

[OTT 진입 좌표]
- Netflix Indonesia/SEA — Pengabdi Setan 시리즈 흥행 트랙으로 검증됨.
- Disney+ Hotstar SEA — 〈American Horror Story〉 팬덤과 오버랩, 콘텐츠 심의 보수성 제약.
- Vidio (로컬 1위) · Vision+ · WeTV — 로컬 콘텐츠 비중 높음.

[공동제작 트랙 — JAFF Market]
- JAFF Market (Jogja-NETPAC Asian Film Festival Market, 매년 11월)
  : 부산 ACFM과 유사 / JAFF Future Project · Content Market · Talent Day · Film Lab
  : Alexander Matius (프로그램 디렉터) · Linda Gozali (마켓 디렉터) · Ifa Isfansyah (영화제 디렉터)
- APROFI (인도네시아 영화제작자협회) · PGK (Producers Group) Producers Meeting
- 진행 프로세스: NDA → 시나리오/기획서 교환 (인니어 번역 필수) → 파트너십·현지 제작사 모색 → 6개월 이내 KOFIC 지원 신청
- KOFIC 지원: 자카르타 출장 항공권 · 시나리오 번역 · 계약서 법률 자문

[진단 원칙]
- 인도네시아 시장은 domestic. 한국·말레이시아·싱가포르·네덜란드·미국 디아스포라가 global.
- 한국 단독 자본으로 인니 작품 추진 시 문화 전용 리스크 명시 필수.
- 인도네시아 공동제작사 어태치를 conditional_requirements에 박는 것이 표준.
"""


# ============================================================================
# 4. 매핑 헬퍼
# ============================================================================

def resolve_market_lens(target_market: str) -> dict:
    """
    target_market 문자열을 분석해 적용할 Market Lens를 결정한다.

    Returns:
        {
            "primary": "KR" | "JP" | "ID",
            "secondary": "KR" | "JP" | "ID" | None,
            "lens_text": "주입할 프롬프트 텍스트",
            "japan_doc_mode": bool,  # JP가 포함되면 True
        }

    매핑 규칙:
        "한국"/"Korea"/"KR"/"국내"          → KR
        "일본"/"Japan"/"JP"                  → JP
        "인도네시아"/"Indonesia"/"ID"
          /"동남아"/"SEA"/"Southeast"/"JAFF" → ID
        명시 없음/"글로벌" 단독             → KR (기본값)
    """
    if not target_market:
        return _build_lens_result("KR", None)

    tm = target_market.lower()

    # 각 시장 키워드 감지
    kr_hit = any(k in target_market for k in ["한국", "국내"]) or \
             any(k in tm for k in ["korea", "korean", "kr "])
    jp_hit = any(k in target_market for k in ["일본"]) or \
             any(k in tm for k in ["japan", "japanese", "jp ", "jp+", "tokyo"])
    id_hit = any(k in target_market for k in ["인도네시아", "동남아", "자카르타"]) or \
             any(k in tm for k in ["indonesia", "indonesian", "id ", "sea", "southeast", "jaff"])

    # 등장 순서 기반 우선순위 — 작가가 먼저 쓴 시장이 1차 시장
    market_positions = []
    if kr_hit:
        # 가장 먼저 매칭되는 한국 키워드의 위치
        for k in ["한국", "국내", "Korea", "korean", "KR"]:
            if k in target_market:
                market_positions.append((target_market.find(k), "KR"))
                break
    if jp_hit:
        for k in ["일본", "Japan", "japan", "Tokyo"]:
            if k in target_market:
                market_positions.append((target_market.find(k), "JP"))
                break
    if id_hit:
        for k in ["인도네시아", "동남아", "자카르타", "Indonesia", "indonesia", "SEA", "JAFF"]:
            if k in target_market:
                market_positions.append((target_market.find(k), "ID"))
                break

    if not market_positions:
        return _build_lens_result("KR", None)

    # 등장 순서대로 정렬
    market_positions.sort(key=lambda x: x[0])
    primary = market_positions[0][1]
    secondary = market_positions[1][1] if len(market_positions) > 1 else None
    return _build_lens_result(primary, secondary)


def _build_lens_result(primary: str, secondary):
    """프롬프트에 주입할 lens_text를 조립한다."""
    lens_map = {"KR": KR_LENS, "JP": JP_LENS, "ID": ID_LENS}
    label_map = {"KR": "한국", "JP": "일본", "ID": "인도네시아"}

    parts = [f"[Market Lens — 1차 시장: {label_map[primary]}]", lens_map[primary]]

    if secondary:
        parts.append(f"\n[Market Lens — 2차 시장: {label_map[secondary]}]")
        parts.append(lens_map[secondary])

    return {
        "primary": primary,
        "secondary": secondary,
        "lens_text": "\n".join(parts),
        "japan_doc_mode": (primary == "JP" or secondary == "JP"),
    }


def get_lens_text(target_market: str) -> str:
    """프롬프트 .format()에 바로 주입하는 헬퍼."""
    return resolve_market_lens(target_market)["lens_text"]


def is_japan_market(target_market: str) -> bool:
    """일본 시장이 타겟에 포함되었는지 판정 (JP_DOC 모드 트리거)."""
    return resolve_market_lens(target_market)["japan_doc_mode"]


def get_primary_market(target_market: str) -> str:
    """1차 시장 코드 반환 (KR | JP | ID)."""
    return resolve_market_lens(target_market)["primary"]
