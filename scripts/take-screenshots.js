const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const pages = [
  { file: 'integrated-analysis.html', name: '통합분석', menu: 1 },
  { file: 'intelligence.html', name: '판세정보', menu: 2 },
  { file: 'strategy.html', name: '전략 비교&추천', menu: 3 },
  { file: 'pledges.html', name: '공약 비교&추천', menu: 4 },
  { file: 'vehicle-strategy.html', name: '선거차량 동선최적화', menu: 5 },
  { file: 'ai-chat.html', name: 'AI톡과 질문과 대화', menu: 6 },
  { file: 'dashboard.html', name: '대시보드', menu: 7 },
  { file: 'blog.html', name: '블로그-기사', menu: 8 },
  { file: 'external-materials.html', name: '외부자료', menu: 9 },
  { file: 'warroom.html', name: '워룸-위기대응센터', menu: 10 },
  { file: 'reports.html', name: '분석리포트', menu: 11 },
  { file: 'organization-chart.html', name: '조직도', menu: 12 },
  { file: 'ai-premium.html', name: 'AI 프리미엄 도구들', menu: 13 },
  { file: 'settings.html', name: '설정', menu: 14 }
];

async function takeScreenshots() {
  const browser = await chromium.launch();
  const assetsDir = path.join(__dirname, '..', 'assets', 'screenshots');

  // Create assets/screenshots directory if it doesn't exist
  if (!fs.existsSync(assetsDir)) {
    fs.mkdirSync(assetsDir, { recursive: true });
  }

  console.log('📸 페이지 스크린샷 생성 중...\n');

  for (const page of pages) {
    try {
      const context = await browser.newContext({
        viewport: { width: 1280, height: 720 }
      });
      const pageObj = await context.newPage();

      // Navigate to page
      const filePath = path.join(__dirname, '..', 'pages', page.file);
      const fileUrl = `file://${filePath.replace(/\\/g, '/')}`;

      await pageObj.goto(fileUrl, { waitUntil: 'networkidle' });

      // Wait a moment for any animations to settle
      await pageObj.waitForTimeout(1000);

      // Take screenshot
      const screenshotPath = path.join(assetsDir, `menu-${String(page.menu).padStart(2, '0')}-${page.file.replace('.html', '.png')}`);
      await pageObj.screenshot({ path: screenshotPath, fullPage: false });

      console.log(`✅ Menu ${String(page.menu).padStart(2, '0')}: ${page.name}`);
      console.log(`   📁 ${screenshotPath.replace(/\\/g, '/')}\n`);

      await context.close();
    } catch (error) {
      console.error(`❌ Menu ${page.menu}: ${page.name}`);
      console.error(`   오류: ${error.message}\n`);
    }
  }

  await browser.close();
  console.log('✨ 모든 스크린샷 생성 완료!');
}

takeScreenshots().catch(error => {
  console.error('스크립트 오류:', error);
  process.exit(1);
});
