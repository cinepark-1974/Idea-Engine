"""
Market Lens Pack v1.1
BLUE JEANS PICTURES · Idea Engine v1.4 신규 모듈 · v2.3.5 베트남(VN) 추가

target_market 입력에 따라 시장별 진단 좌표를 동적으로 주입한다.
Stage 4 (포맷·장르·시장 좌표) / Stage 5 (레퍼런스) / Stage 6 (Market 진단)
프롬프트가 시장 중립적으로 작동하도록 시장 프로필을 외부에서 공급한다.

[지원 시장]
  KR — 한국 (기본값, 현재 동작 보존)
  JP — 일본 (JP_DOC 모드 — 3트랙 외 0점 처리)
  ID — 인도네시아 (JAFF Market·이슬람 문화 제약 반영)
  VN — 베트남 (v2.3.5 · 범용 국가 프로필 · 근거 등급 4종 · 8축 평가)

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
# 4. 베트남 시장 (VN) — 범용 국가별 Market Lens (v2.3.5 신규)
# ============================================================================
#
# 설계 원칙
#   - 특정 작품·장르를 전제로 설계하지 않는다. 입력된 기획을 평가할 때만 적용한다.
#   - 모든 산업 사실에 근거 등급과 출처·기준일을 붙인다.
#   - 서로 다른 조사 기관의 수치는 합치거나 직접 비교하지 않는다.
#   - 확인되지 않은 제작비·수익률·손익분기점·개봉 일정은 생성하지 않는다.
#
# 자료 기준일: 2026-10-23 (아래 VN_SOURCES의 각 자료 기준일 참조)

VN_DATA_AS_OF = "2026-10-23"

VN_SOURCES = [
    {"id": "S1", "name": "ACFM The A Report — Vietnam 2026 H1 (LÊ Hồng Lâm)",
     "as_of": "2026-10-06 갱신",
     "url": "https://www.acfm.kr/eng/html/areport/reportRead.asp?mode=H1&page_num=15&piffcode=2026"},
    {"id": "S2", "name": "Cinemark 베트남 극장시장 2026 H1 보고서 (Box Office Vietnam 데이터, VietnamFinance 보도)",
     "as_of": "2026-08-06 보도 / 집계 2026-01-01~06-30",
     "url": "https://vietnamfinance.vn/gan-35-trieu-luot-ve-va-bai-toan-tang-truong-moi-cua-dien-anh-viet-d148632.html"},
    {"id": "S3", "name": "ACFM The A Report — Vietnam 2025 H2 (LÊ Hồng Lâm)",
     "as_of": "2026-05-12 갱신",
     "url": "https://www.acfm.kr/eng/html/areport/reportRead.asp?mode=H2&page_num=17&piffcode=2025"},
    {"id": "S4", "name": "KOFIC 통신원리포트 2026-39 「2025년 베트남 영화산업 결산」",
     "as_of": "2026-06-25",
     "url": "https://www.kobiz.or.kr/new/kor/03_worldfilm/news/corrReports.jsp?blbdComCd=601003&mode=VIEW&seq=3331"},
    {"id": "S5", "name": "베트남 영화법 Luật Điện ảnh 05/2022/QH15",
     "as_of": "2023-01-01 시행",
     "url": "https://thuvienphapluat.vn/van-ban/van-hoa-xa-hoi/luat-dien-anh-2022-486445.aspx"},
    {"id": "S6", "name": "문화체육관광부 시행규칙 Thông tư 05/2023/TT-BVHTTDL (등급분류 기준·표시)",
     "as_of": "2023-05-20 시행",
     "url": "https://vbpl.moj.gov.vn/TW/Lists/vbpq/Attachments/160086/05_2023_TT-BVHTTDL_563559.doc"},
    {"id": "S7", "name": "베트남 영화국장 공문 보도 (VTC News)",
     "as_of": "2026-06-19",
     "url": "https://vtcnews.vn/rap-viet-ngap-tran-phim-kinh-di-cuc-truong-cuc-dien-anh-ra-cong-van-nong-ar1024578.html"},
    {"id": "S8", "name": "MoMo Cinema 「Thị trường phim chiếu rạp H1/2026」 (MoMo 결제 거래 데이터)",
     "as_of": "2026-06-18 집계",
     "url": "https://www.momo.vn/cinema/blog/thi-truong-phim-chieu-rap-h1-2026-2670"},
    {"id": "S9", "name": "Tuổi Trẻ 「Thêm 'ông lớn' Nhật Bản nhảy vào thị trường rạp phim Việt Nam」",
     "as_of": "2025-12-08",
     "url": "https://tuoitre.vn/them-ong-lon-nhat-ban-nhay-vao-thi-truong-rap-phim-viet-nam-20251208001613405.htm"},
    {"id": "S10", "name": "Doanh nhân Pháp luật — 베트남 온라인 동영상 시장 (Sensor Tower·DataReportal 인용)",
     "as_of": "2026-06-22",
     "url": "https://doanhnhan.baophapluat.vn/thi-truong-video-truc-tuyen-viet-nam-doanh-thu-thue-bao-chung-lai-nen-tang-noi-dia-chuyen-huong-kinh-doanh.html"},
]

VN_LENS = """
[VN Market Lens 사용 규칙 — 반드시 먼저 적용]
- 이 렌즈는 특정 작품·장르를 전제하지 않는 범용 시장 프로필이다. 입력된 기획에만 적용한다.
- 근거 등급 4종을 구분한다.
  VERIFIED = 아래 출처(S1~S10)로 확인된 산업 사실 / INFERENCE = 자료에 근거한 분석적 추론
  CREATIVE_JUDGMENT = 작품에 대한 창작적·비평적 판단 / VERIFICATION_REQUIRED = 추가 검증이 필요한 사항
- VERIFIED는 이 렌즈에 [V·출처] 표시가 있는 항목만 인용한다. 표시가 없는 내용을 VERIFIED로 올리지 않는다.
- 서로 다른 출처의 수치를 더하거나 직접 비교하지 않는다. (예: 2025 평균 티켓가 S3과 2026 H1 평균 티켓가 S2는 집계 기관이 다르다.)
- 특정 장르의 최근 흥행만으로 가점을 주지 않는다. 장르 흥행 데이터는 경쟁 강도·포화도·관객층 판단 근거로만 쓴다.
- 확인되지 않은 제작비·투자 수익률·손익분기점·미래 개봉 일정·특정 배급사의 선택 가능성은 만들지 않는다. 필요하면 VERIFICATION_REQUIRED로 표기한다.
- 작가가 확정한 설정과 LOCKED 시드는 시장 평가를 이유로 바꾸지 않는다. 현지화 제안은 조건·권고로만 제시한다.
- 아래 작품명은 시장 데이터 포인트다. 모범 답안·표준작이 아니며, 입력 기획을 이 작품들에 맞추라고 권하지 않는다.

[시장 정체]
- 2025 연간: 극장 매출 5조 5,930억 VND, 전년 대비 +24% [V·S3, CGV Vietnam 보고 인용]. 관람권 7,000만 장 이상 [V·S3·S4].
  ※ 관람권 증가율은 S3 +29%, S4 +26%로 출처 간 불일치 — 증가율 인용 시 출처를 함께 적는다.
- 2025 자국 영화 점유율: S3은 약 62%(자국 영화 약 3조 4,000억 VND 기준), S4는 요약 62%·본문 57%로 내부 불일치. 62%를 인용할 때 "S3 기준"을 명시한다.
- 2025 1인당 연간 관람 0.7회, 2019년 수준 회복 [V·S4].
- 2026 H1 (Box Office Vietnam 데이터, 2026-01-01~06-30) [V·S2]:
  매출 3조 1,984억 VND / 관람권 약 3,513만 장 / 상영 회차 약 122.9만 / 224편·270개 극장·59개 성시
  평균 티켓가 91,036 VND / 평균 좌석 점유율 21.1% / 자국 영화 매출 점유율 65.3%(국적 식별분 기준)
- 2026 H1 전년 동기 대비 약 +6.0%(2025 H1 3조 170억 VND 대비), 자국 영화 개봉 35편(2025 H1 19편), 수입 영화 150편 [V·S1].
- 결제 플랫폼 MoMo의 자사 거래 집계(2026-06-18까지)는 H1 GMV 약 2조 6,000억 VND·전년 대비 약 -13.5%로 S1·S2와 방향이 다르다 [V·S8]. 집계 범위가 다른 자료이므로 S2를 시장 총량 기준으로 쓰고 S8은 관객 성향 참고용으로만 쓴다.
- 자국 영화 개봉 편수: 2025 약 50편, 2026 전망 70~80편 [V·S1]. 공급 증가 → 편당 경쟁 심화는 INFERENCE.
- 흥행 양극화: 2025 개봉작의 절반 이상이 상업적으로 실패, 다수가 10억 VND 미만 [V·S3]. 흥행 양극화를 구조적 과제로 지적 [V·S4].
- 극장이 1차 회수 창구, OTT는 2차 창구 [V·S1·S3].

[장르군별 산업 좌표 — 8개 장르군 독립 평가]
※ 한국 장르 10분류(Creator/Writer 룰팩)와는 별개인 시장 분석 축이다. 매핑은 아래 괄호를 참조하되 장르 LOCK 값을 바꾸지 않는다.

1) 가족·휴먼 드라마 (DRAMA·MELO 일부)
   - 2026 H1 흥행 1위는 드라마·스릴러 결합의 설 개봉작(4,495억 VND) [V·S1]. 2025 H2 한·베 공동제작 가족 드라마 1,717억 VND, 가족 드라마 823억 VND [V·S3].
   - 가족 영화가 장르 중 가장 높은 좌석 점유율(약 27.1%) [V·S2].
   - 상위 흥행이 배우 겸 감독 브랜드(감독 브랜드로 Trấn Thành·Lý Hải·Victor Vũ 거론)에 집중 [V·S1·S3]. 이 관객 신뢰가 신인 기획에 그대로 이전되지 않는다는 점은 INFERENCE.
2) 코미디·로맨틱 코미디 (COMEDY·MELO)
   - 2025 H2 액션 코미디 2,070억 VND, 코미디 330억 VND, 호러 코미디 1,010억 VND로 편차가 크다 [V·S3].
   - 코미디·드라마 관객은 여성 비중이 높고 18~30세, 1~2일 전 예매 경향 [V·S8 — MoMo 결제 데이터이며 관객 조사 통계가 아님].
3) 로맨스·멜로드라마 (MELO)
   - 2026 H1 드라마·로맨스 2편이 각 1,187억·1,036억 VND로 자국 Top 10 진입 [V·S1].
   - 로맨스 관객은 여성 비중이 높고 18~26세 [V·S8].
4) 액션·범죄·스릴러 (ACTION·CRIME)
   - 2025 H2 항공 납치 액션 스릴러 2,518억 VND(공안 계열 스튜디오 제작) [V·S3]. 2026 H1 드라마·액션 1,132억, 드라마·스릴러 1,129억 VND [V·S1].
   - 공안·군 계열 국영 스튜디오가 대형 액션·전쟁물 제작에 참여 [V·S1·S3]. 외국 기획사의 동일 소재 접근 난이도는 VERIFICATION_REQUIRED.
5) 역사·전쟁·시대극 (PERIOD)
   - 2025 베트남 전쟁 서사극이 7,140억 VND, 관객 800만 명 이상으로 역대 자국 영화 최고 기록 [V·S3·S4]. 2025 4월 개봉 전쟁물 약 1,700억 VND [V·S3].
   - 국가 기념일을 겨냥한 역사물 약 10편이 개발·제작 중 [V·S1] — 같은 장르의 공급 집중 위험은 INFERENCE.
   - 영화법은 역사 왜곡·혁명 성과 부정·영웅 모욕을 금지 [V·S5 제9조]. 해석 범위는 VERIFICATION_REQUIRED.
6) 공포·미스터리·초자연 스릴러 (HORROR)
   - 2026 H1 호러 매출 9,774억 VND, 전체의 30.6%. 월별 점유율 1월 10.2% → 6월 65.6% [V·S2].
   - 호러 59편 중 자국 약 10편이 호러 매출의 70% 이상 [V·S2] → 소수 집중·다수 부진 구조.
   - 영화국장 공문(2026-06): 과도한 폭력·유혈·미신 요소에 대한 신중 권고, 장르 다양화 권장. 새 규정이 아닌 권고 [V·S7·S1].
   - 호러 관객은 남녀 비슷, 18~26세, 당일 구매 경향 [V·S8].
   - 판정: 호러는 "흥행 장르"가 아니라 "포화·규제 주의 장르"로 먼저 본다. 가점 금지.
7) 판타지·SF·애니메이션 (FANTASY)
   - 수입 애니메이션이 상위권 점유(2026 H1 2위 2,045억 VND, 2025 H2 Top 10 중 3편) [V·S1·S3]. 애니메이션 평균 티켓가가 가장 높음(98,667 VND) [V·S2].
   - VFX·애니메이션·후반 작업은 주로 해외 하청 중심, 대형 버추얼 프로덕션·사운드스테이지 부족 [V·S1·S3].
   - 자국산 판타지·SF·애니메이션의 극장 흥행 사례는 확인 자료 없음 → VERIFICATION_REQUIRED.
8) 독립·예술영화
   - 아트하우스 전용관 없음 [V·S3]. 독립영화 유통 인프라 부재 [V·S4]. 개봉·관객 비중 미미 [V·S1].
   - 국가 영화 기금·경쟁력 있는 세제 환급 제도 없음 [V·S3].
   - 진입 경로는 해외 영화제·공동제작 펀드 중심이 될 것이라는 판단은 INFERENCE.

[관객·소비 특성]
- 지역 집중: 2026 H1 매출의 호찌민시 32.6%, 하노이 22%(합계 54.6%) [V·S2].
- 2선 도시 점유율이 대도시보다 높은 곳 존재(빈즈엉 27.4%, 다낭 26.7%, 하이퐁 24.8%) [V·S2]. 극장 미집계 성 7곳 [V·S2].
- 시간대: 17~22시 매출 39%, 심야 점유율 약 28% [V·S2]. 오전은 주요 체인 모두 점유율 16% 미만, 가족 관객 위주 [V·S1].
- 티켓가: 2026 H1 월평균 1월 97,045 → 6월 86,224 VND(-11.2%), 매출은 가격보다 점유율과 더 강하게 연동 [V·S2]. 가격 민감도에 대한 관객 조사 통계는 없음 → VERIFICATION_REQUIRED.
- 연령대 자료는 결제 플랫폼 거래 데이터(S8)뿐이며 18~30세 중심이다. 40대 이상·지방 관객의 성향은 VERIFICATION_REQUIRED.
- SNS 입소문이 대형 흥행작 확산에 작동 [V·S1]. 개별 기획의 SNS 화제성 예측은 CREATIVE_JUDGMENT.
- 자국 영화와 수입 영화: 2026 H1 수입작 점유 34.7%, 수입 내 미국 14.2%·일본 8.2%·한국 5.1% [V·S1·S2]. 2025 한국 영화 매출 1,326만 달러(-33.6%) [V·S4].

[제작·투자 환경]
- 평균 제작비: 2025 기준 편당 150억~200억 VND [V·S3]. 대형 투자배급사 1곳(CJ HK)의 2026 평균은 약 250억 VND(제작 190억 + 마케팅 60억) [V·S1] — 한 회사 사례이므로 업계 평균으로 쓰지 않는다.
- 조달: 민간 자본 중심(단독 투자·공동 투자·제작-배급 파트너십), 전용 펀드·벤처캐피털 참여 미미 [V·S3]. 대형 투자배급사가 50~70%, 제작 파트너가 30~50%를 부담하고 극장·장비·후반 업체·개인 주주에서 잔여 자금을 모으는 사례 [V·S1].
- 국제 공동 투자는 아직 의미 있는 규모가 아니며 단기 우선순위가 아님(국내 극장 매출 중심·해외 회수 제한·법적 절차·현지 관객 이해 부족이 이유) [V·S1]. 현지 사무소나 대리인이 있는 해외 파트너 선호 [V·S1].
- 한·베 공동제작 가족 드라마가 2025 H2 흥행 4위 [V·S3]. 반면 일부 공동제작은 부진 [V·S3]. 한국 측에는 직접 배급보다 공동제작형 현지화 협력이 유효하다는 제언 [V·S4].
- 인력: 각본·VFX·사운드 디자인 인력 부족 [V·S3].
- 투자 수익률·손익분기점 수치는 확인 자료 없음 → 생성 금지, VERIFICATION_REQUIRED.

[극장·배급 구조]
- 전국 200개 이상 극장, 약 1,200개 스크린, 호찌민·하노이 집중 [V·S1].
- 사업자 점유율 (출처별로 따로 읽는다. 합치지 않는다):
  · S4(2025 결산): CGV 45.4%, 롯데시네마 23.8%, 한국 자본 계열 합계 약 70%
  · S9(2025-12 보도, 산출 근거 미표기): CGV 약 45%, 롯데 26%, Galaxy 10%, Beta 8%, BHD 약 5.5%
  · S1(2026 H1): CGV 약 83개 극장·480개 스크린·41.2%, 롯데 약 45개·210개 스크린·약 17.5%
  · Cinestar·Mega GS·DCINE·국영 극장의 점유율 → VERIFICATION_REQUIRED
- 신규 진입: AEON Beta(베트남 Beta Media + 일본 Aeon Entertainment 합작) 2025-12 하노이 1호점, 2035년까지 50개 계획 [V·S9].
- 배급·상영 수직 계열화로 체인이 개봉 일정과 스크린 배정에 큰 영향력 [V·S1·S3]. 배급 주체: CGV·롯데(상영 겸 배급), Galaxy Studio·BHD·Beta(국내 배급) [V·S1].
- 자국 영화가 수입 영화보다 스크린·시간대 배정에서 우위, 성수기 일부 자국 대작은 하루 5,000회 이상 상영 [V·S1].
- 하위 흥행작의 상영 지속 가능성·스크린 회수 시점에 대한 공개 데이터는 없음 → VERIFICATION_REQUIRED.

[OTT·디지털 유통]
- 글로벌: Netflix·iQIYI·Apple TV+ / 로컬: FPT Play·VieON·Galaxy Play·VTV Go [V·S1·S3]. 2025 극장 흥행작이 TV360 공개 24시간 만에 100만 뷰 [V·S4].
- 2025 OTT 가입자 556만 → 740만(+33%), 매출 1조 7,000억 VND(+7%), Netflix 소셜 화제성 38.5% 1위 [V·S4].
- 구독 매출(Sensor Tower, 2020~2026 누적): VieON 약 1,400만 달러, iQIYI 927만, FPT Play 896만 달러, 로컬 3사(VieON·FPT Play·Galaxy Play)가 조사 그룹의 75.5% [V·S10]. 유료 전환율 10% 미만 [V·S10].
- 로컬 플랫폼은 광고·라이선스·IP 사업으로 다각화 [V·S10]. 유료TV K+는 2026-01 서비스 종료 [V·S4].
- 2026-05 정부 공문 제38호로 저작권 침해 스트리밍 사이트 전국 단속 캠페인 [V·S1]. 해외 OTT의 콘텐츠·세금·현지법 준수 요구 강화 [V·S1].
- 극장 홀드백 기간·플랫폼별 구매 단가는 확인 자료 없음 → VERIFICATION_REQUIRED.
- 극장용 영화와 OTT 전용 콘텐츠는 회수 구조가 다르므로 따로 평가한다.

[개봉 시즌]
- 설(Tết)이 가장 중요한 시즌, 4월 30일~5월 1일 연휴가 두 번째 [V·S1].
- 2026년 2월(설 시즌) 매출 7,237억 VND·좌석 점유율 32.4%로 상반기 최고 [V·S1·S2]. 1월 점유율 16.6% [V·S2].
- 설 시즌 최상위 흥행은 배우 겸 감독 브랜드 작품이 반복 점유 [V·S1] → 신인 기획의 설 정면 경쟁은 고위험이라는 판단은 INFERENCE.
- 여름: 6월 호러 점유 65.6% [V·S2] → 여름 호러 과밀은 INFERENCE.
- 국가 기념일: 기념일 연계 역사물 다수 개발 중 [V·S1].
- 연말 시즌의 매출·경쟁 데이터는 이번 자료에 없음 → VERIFICATION_REQUIRED.
- 미래 경쟁작·개봉 일정은 만들지 않는다.

[문화·사회 환경 — 확인 사실과 해석을 분리]
- 확인 사실: 영화법이 국가 통합 훼손, 역사 왜곡, 종교 모욕·불법 종교활동 선전, 사생활 공개, 아동 권리 침해, 성차별을 금지 [V·S5 제9조].
- 확인 사실: 공문(2026-06)이 미신적 소재에 대한 신중함을 권고 [V·S7].
- 가족·세대 관계, 도시-지방 격차, 청년층 연애·소비 문화, 지역 언어(북·중·남부 방언)와 관습, 민속 신앙은 작품 판단의 핵심 변수다. 이번 자료에는 이를 수치로 확인한 조사가 없으므로 서술할 때는 INFERENCE 또는 VERIFICATION_REQUIRED로 표기한다.
- 현지 고증(지역 방언·종교 의례·현대사 디테일)이 외국 제작진 단독으로 이뤄질 때의 반발 위험은 INFERENCE이며, 현지 공동 작가·자문 어태치를 조건으로 제시하는 것이 표준 처리다.

[법률·심의·규제]
- 근거 법령: 영화법 Luật Điện ảnh 05/2022/QH15, 2023-01-01 시행 [V·S5]. 시행령 131/2022/NĐ-CP, 등급 기준 시행규칙 05/2023/TT-BVHTTDL(2023-05-20 시행) [V·S6].
- 등급 6종 [V·S5 제32조·S6]: P(전 연령) / K(13세 미만은 보호자 동반) / T13 / T16 / T18 / C(상영 불가).
  · 평가 기준 7가지: 주제·내용, 폭력, 노출·성, 마약, 공포, 언어, 위험 모방 행동 [V·S6].
  · T16: 자해·자살은 간접·약하게·짧게, 공포는 강도 높되 짧게 [V·S6].
  · T18: 강한 폭력 허용하되 과도한 수준 미만, 노골적 성행위는 원칙적으로 불가(서사상 필요·짧은 경우 예외) [V·S6].
  · C: 제9조 위반 또는 어느 기준이든 과도한 수준 [V·S6].
- 등급 허가: 극장 상영작은 문화체육관광부(조건 충족 시 성급 인민위원회도) 발급, 유효 서류 접수 후 15일 내 결정, 전국 유효 [V·S5 제27조].
- 온라인: 허가받은 사업자만 온라인 상영 가능, 조건을 갖춘 사업자는 자체 분류 후 결과를 사전 통보, 불가하면 당국 분류 [V·S5 제21조].
- 외국 제작의 베트남 촬영: 베트남 영화 제작 서비스 업체를 통해야 하며 문화체육관광부 허가 필요(베트남어 상세 촬영 대본·용역 계약·제9조 준수 서약 제출, 20일 내 결정) [V·S5 제13조].
- 외국인 투자: 신설 외국인 투자 법인(외국인 지분 상한 51%) 또는 사업 협력 계약 방식, 공동제작·외국 후원 시 제9조 준수 서약 제출 [V·S5 제8·10조 — 조문 원문 재확인 권장].
- 원작 판권·저작권 이전 절차, 해외 심의 결과 승계 여부 → VERIFICATION_REQUIRED.
- 규정이 확인되지 않은 소재는 허용·금지를 판정하지 않고 VERIFICATION_REQUIRED로 둔다.

[구매자 좌표 4분류 — Stage 4 시장 좌표용]
- TENTPOLE (극장 대작): 자국 흥행 상위작 제작·배급 주체로 CJ HK Entertainment, Galaxy Studio, CJ CGV(배급), HKFilm, Bluebells Studios, 856 Pictures, V Pictures, F35 Studio·89s Group, Mega GS, 군·공안 계열 국영 스튜디오가 확인됨 [V·S1·S3]. 특정 회사가 이 기획을 선택할 가능성은 판정하지 않는다.
- MASTERCLASS (작가주의): 아트하우스 전용관·국가 기금 부재 [V·S3]. 해외 영화제·공동제작 펀드 경유가 현실 경로라는 판단은 INFERENCE.
- STREAMING (OTT): Netflix·iQIYI·Apple TV+·FPT Play·VieON·Galaxy Play·VTV Go·TV360 [V·S1·S3·S4].
- GENRE_FEATURE (중소 장르): 독립 제작사는 연 1~3편 제작 [V·S1]. 개봉작 과반 실패 구조 [V·S3]를 리스크로 함께 적는다.

[공동제작 트랙]
- 한·베 공동제작 흥행 사례 존재 [V·S3]. 현지 대리인 보유 해외 파트너 선호 [V·S1].
- 베트남 촬영은 현지 서비스 업체 계약이 법적 필수 [V·S5 제13조] → conditional_requirements의 기본 항목.
- 정부의 공동제작 인센티브·세제 환급은 없음 [V·S3].

[VN 평가 8축 — 작품 입력 후에만 평가]
1 시장 적합성 / 2 장르 경쟁력 / 3 관객 접근성 / 4 현지화 적합성 / 5 제작 실현성 / 6 배급 적합성 / 7 마케팅 가능성 / 8 규제 위험
- 각 축은 0~5 stars. 근거마다 VERIFIED·INFERENCE·CREATIVE_JUDGMENT·VERIFICATION_REQUIRED 중 하나를 붙인다.
- 장르 경쟁력은 "그 장르가 잘 된다"가 아니라 "그 장르의 실제 경쟁 조건에서 이 기획의 차별점이 무엇인가"로 판정한다.
- 규제 위험은 위 [법률·심의·규제]에 있는 조항만 근거로 삼고, 예상 등급(P·K·T13·T16·T18·C)은 CREATIVE_JUDGMENT로 표기한다.

[진단 원칙]
- 베트남이 1차 시장이면 domestic = 베트남, 한국·기타 국가는 global.
- 베트남 극장 수익은 1차 회수 창구이며 OTT는 2차 창구다 [V·S1·S3].
- 외국 기획이 베트남을 무대로 할 때는 현지 제작 서비스 업체·현지 공동 작가 또는 자문 어태치를 conditional_requirements에 적는 것이 표준이다.
"""


# ============================================================================
# 5. 매핑 헬퍼
# ============================================================================

import re

# 시장 코드 → (한글 라벨, 국기) — main.py 화면 라벨과 공유
MARKET_LABELS = {
    "KR": ("한국", "🇰🇷"),
    "JP": ("일본", "🇯🇵"),
    "ID": ("인도네시아", "🇮🇩"),
    "VN": ("베트남", "🇻🇳"),
}

def resolve_market_lens(target_market: str) -> dict:
    """
    target_market 문자열을 분석해 적용할 Market Lens를 결정한다.

    Returns:
        {
            "primary": "KR" | "JP" | "ID" | "VN",
            "secondary": "KR" | "JP" | "ID" | "VN" | None,
            "lens_text": "주입할 프롬프트 텍스트",
            "japan_doc_mode": bool,    # JP가 포함되면 True
            "vietnam_lens_mode": bool, # VN이 포함되면 True (v2.3.5)
        }

    매핑 규칙:
        "한국"/"Korea"/"KR"/"국내"          → KR
        "일본"/"Japan"/"JP"                  → JP
        "인도네시아"/"Indonesia"/"ID"
          /"동남아"/"SEA"/"Southeast"/"JAFF" → ID
        "베트남"/"Vietnam"/"Việt Nam"/"VN"
          /"호찌민"/"호치민"/"하노이"        → VN (v2.3.5)
        명시 없음/"글로벌" 단독             → KR (기본값)

    v2.3.5 보정:
        베트남이 명시되고 인도네시아 고유 키워드(인도네시아·자카르타·Indonesia·JAFF)가
        없을 때는 "동남아"·"SEA"·"Southeast" 같은 권역 표현을 인도네시아로 읽지 않는다.
        (예: "베트남 + Netflix SEA" → VN 단독. 인도네시아 렌즈가 끼어들지 않음)
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

    # v2.3.5: 베트남 감지
    vn_pos = _find_vietnam_position(target_market)
    vn_hit = vn_pos >= 0

    # v2.3.5: 베트남이 명시되면 권역 표현(동남아·SEA·Southeast)만으로는 ID를 붙이지 않는다
    id_explicit = any(k in target_market for k in ["인도네시아", "자카르타"]) or \
                  any(k in tm for k in ["indonesia", "indonesian", "jaff"])
    if vn_hit and not id_explicit:
        id_hit = False

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
    if vn_hit:
        market_positions.append((vn_pos, "VN"))

    if not market_positions:
        return _build_lens_result("KR", None)

    # 등장 순서대로 정렬
    market_positions.sort(key=lambda x: x[0])
    primary = market_positions[0][1]
    secondary = market_positions[1][1] if len(market_positions) > 1 else None
    return _build_lens_result(primary, secondary)


_VN_KEYWORDS = ["베트남", "호찌민", "호치민", "하노이", "vietnam", "viet nam", "việt nam", "hanoi", "ho chi minh", "saigon"]


def _find_vietnam_position(target_market: str) -> int:
    """베트남 키워드가 처음 등장하는 위치. 없으면 -1.
    'VN'은 다른 단어 일부와 겹치지 않도록 앞뒤가 영문자가 아닐 때만 인정한다."""
    tm = target_market.lower()
    positions = [tm.find(k) for k in _VN_KEYWORDS if k in tm]
    m = re.search(r"(?<![a-z])vn(?![a-z])", tm)
    if m:
        positions.append(m.start())
    return min(positions) if positions else -1


def _build_lens_result(primary: str, secondary):
    """프롬프트에 주입할 lens_text를 조립한다."""
    lens_map = {"KR": KR_LENS, "JP": JP_LENS, "ID": ID_LENS, "VN": VN_LENS}
    label_map = {code: MARKET_LABELS[code][0] for code in MARKET_LABELS}

    parts = [f"[Market Lens — 1차 시장: {label_map[primary]}]", lens_map[primary]]

    if secondary:
        parts.append(f"\n[Market Lens — 2차 시장: {label_map[secondary]}]")
        parts.append(lens_map[secondary])

    return {
        "primary": primary,
        "secondary": secondary,
        "lens_text": "\n".join(parts),
        "japan_doc_mode": (primary == "JP" or secondary == "JP"),
        "vietnam_lens_mode": (primary == "VN" or secondary == "VN"),
    }


def get_lens_text(target_market: str) -> str:
    """프롬프트 .format()에 바로 주입하는 헬퍼."""
    return resolve_market_lens(target_market)["lens_text"]


def is_japan_market(target_market: str) -> bool:
    """일본 시장이 타겟에 포함되었는지 판정 (JP_DOC 모드 트리거)."""
    return resolve_market_lens(target_market)["japan_doc_mode"]


def get_primary_market(target_market: str) -> str:
    """1차 시장 코드 반환 (KR | JP | ID | VN)."""
    return resolve_market_lens(target_market)["primary"]


def is_vietnam_market(target_market: str) -> bool:
    """베트남 시장이 1차 또는 2차로 포함되었는지 판정 (VN 8축 평가 트리거, v2.3.5)."""
    return resolve_market_lens(target_market)["vietnam_lens_mode"]


def get_vn_sources_text() -> str:
    """VN Market Lens 출처·기준일 목록 (화면·보고서 표기용, v2.3.5)."""
    lines = [f"VN Market Lens 자료 기준일: {VN_DATA_AS_OF}"]
    for src in VN_SOURCES:
        lines.append(f"{src['id']} · {src['name']} ({src['as_of']}) — {src['url']}")
    return "\n".join(lines)
