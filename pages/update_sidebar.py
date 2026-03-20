import os
import re

# 파일별 active 메뉴 매핑
file_active_map = {
    'integrated-analysis.html': '1.통합분석',
    'intelligence.html': '2.판세정보 분석&비교',
    'strategy.html': '3.전략 비교&추천',
    'pledges.html': '4.공약 비교&추천',
    'vehicle-strategy.html': '5.차량 전략',
    'ai-chat.html': '6.AI톡과 질문과 대화',
    'dashboard.html': '7.대시보드',
    'blog.html': '8.블로그-기사',
    'external-materials.html': '9.외부자료 업로드',
    'warroom.html': '10.워룸-위기대응센터',
    'reports.html': '11.분석리포트 관리',
    'organization-chart.html': '12.조직도',
    'ai-premium.html': '13.AI 프리미엄 도구들',
    'settings.html': '14.설정',
    'strategy-comparison.html': '12.수행계획 수립',  # 사이드바에는 유지
    'competitors.html': '7.경쟁분석',  # 사이드바에는 유지
}

# 새로운 사이드바 메뉴 항목 (기본형, active 없음)
new_sidebar_html = '''        <li><a href="index.html">대시보드</a></li>
        <li><a href="integrated-analysis.html">1.통합분석</a></li>
        <li><a href="intelligence.html">2.판세정보 분석&비교</a></li>
        <li><a href="strategy.html">3.전략 비교&추천</a></li>
        <li><a href="pledges.html">4.공약 비교&추천</a></li>
        <li><a href="vehicle-strategy.html">5.차량 전략</a></li>
        <li><a href="ai-chat.html">6.AI톡과 질문과 대화</a></li>
        <li><a href="dashboard.html">7.대시보드</a></li>
        <li><a href="blog.html">8.블로그-기사</a></li>
        <li><a href="external-materials.html">9.외부자료 업로드</a></li>
        <li><a href="warroom.html">10.워룸-위기대응센터</a></li>
        <li><a href="reports.html">11.분석리포트 관리</a></li>
        <li><a href="organization-chart.html">12.조직도</a></li>
        <li><a href="ai-premium.html">13.AI 프리미엄 도구들</a></li>
        <li><a href="settings.html">14.설정</a></li>'''

for filename, active_text in file_active_map.items():
    filepath = os.path.join('.', filename)
    if not os.path.exists(filepath):
        print(f"파일 없음: {filename}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 사이드바 메뉴 부분 찾기 (ul 태그 내용)
    pattern = r'<ul>\s*<li><a[^>]*>대시보드</a></li>.*?</ul>'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"사이드바 패턴을 찾을 수 없음: {filename}")
        continue
    
    # active 클래스를 추가한 새로운 메뉴 생성
    sidebar_with_active = new_sidebar_html.replace(
        f'<a href="{os.path.basename(filepath)}">{active_text}</a>',
        f'<a href="{os.path.basename(filepath)}" class="active">{active_text}</a>'
    )
    
    # 콘텐츠에서 기존 ul 부분 교체
    new_content = content[:match.start()] + '<ul>\n' + sidebar_with_active + '\n      </ul>' + content[match.end():]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"업데이트됨: {filename} (active: {active_text})")

print("완료!")
