from django.core.management.base import BaseCommand
from django.db import transaction
from i18n.models import Language, Translation


class Command(BaseCommand):
    help = '다국어 지원을 위한 초기 언어 및 번역 데이터를 생성합니다.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('다국어 초기 데이터 생성을 시작합니다...'))
        
        with transaction.atomic():
            # 1. 언어 데이터 생성
            self.create_languages()
            
            # 2. 기본 번역 데이터 생성
            self.create_basic_translations()
            
            self.stdout.write(
                self.style.SUCCESS('다국어 초기 데이터 생성이 완료되었습니다!')
            )

    def create_languages(self):
        """지원 언어 생성"""
        languages = [
            {
                'code': 'ko',
                'name': 'Korean',
                'native_name': '한국어',
                'flag_icon': '🇰🇷',
                'is_active': True,
                'rtl': False
            },
            {
                'code': 'en',
                'name': 'English',
                'native_name': 'English',
                'flag_icon': '🇺🇸',
                'is_active': True,
                'rtl': False
            },
            {
                'code': 'ja',
                'name': 'Japanese',
                'native_name': '日本語',
                'flag_icon': '🇯🇵',
                'is_active': True,
                'rtl': False
            },
            {
                'code': 'zh',
                'name': 'Chinese',
                'native_name': '中文',
                'flag_icon': '🇨🇳',
                'is_active': True,
                'rtl': False
            },
            {
                'code': 'es',
                'name': 'Spanish',
                'native_name': 'Español',
                'flag_icon': '🇪🇸',
                'is_active': False,
                'rtl': False
            },
            {
                'code': 'fr',
                'name': 'French',
                'native_name': 'Français',
                'flag_icon': '🇫🇷',
                'is_active': False,
                'rtl': False
            },
            {
                'code': 'de',
                'name': 'German',
                'native_name': 'Deutsch',
                'flag_icon': '🇩🇪',
                'is_active': False,
                'rtl': False
            },
            {
                'code': 'pt',
                'name': 'Portuguese',
                'native_name': 'Português',
                'flag_icon': '🇧🇷',
                'is_active': False,
                'rtl': False
            },
            {
                'code': 'ru',
                'name': 'Russian',
                'native_name': 'Русский',
                'flag_icon': '🇷🇺',
                'is_active': False,
                'rtl': False
            },
            {
                'code': 'ar',
                'name': 'Arabic',
                'native_name': 'العربية',
                'flag_icon': '🇸🇦',
                'is_active': False,
                'rtl': True
            },
        ]
        
        for lang_data in languages:
            language, created = Language.objects.get_or_create(
                code=lang_data['code'],
                defaults=lang_data
            )
            if created:
                self.stdout.write(f'언어 생성: {language.native_name} ({language.code})')
            else:
                self.stdout.write(f'언어 존재: {language.native_name} ({language.code})')

    def create_basic_translations(self):
        """기본 번역 데이터 생성"""
        
        # 번역 데이터 정의
        translations_data = {
            # 네비게이션
            'nav.home': {
                'ko': '홈',
                'en': 'Home',
                'ja': 'ホーム',
                'zh': '首页',
                'category': 'navigation'
            },
            'nav.charts': {
                'ko': '차트',
                'en': 'Charts',
                'ja': 'チャート',
                'zh': '图表',
                'category': 'navigation'
            },
            'nav.prediction': {
                'ko': '예측하기',
                'en': 'Prediction',
                'ja': '予測',
                'zh': '预测',
                'category': 'navigation'
            },
            'nav.my_predictions': {
                'ko': '내 예측',
                'en': 'My Predictions',
                'ja': '私の予測',
                'zh': '我的预测',
                'category': 'navigation'
            },
            'nav.ranking': {
                'ko': '랭킹',
                'en': 'Ranking',
                'ja': 'ランキング',
                'zh': '排名',
                'category': 'navigation'
            },
            'nav.events': {
                'ko': '이벤트',
                'en': 'Events',
                'ja': 'イベント',
                'zh': '活动',
                'category': 'navigation'
            },
            'nav.subscription': {
                'ko': '구독',
                'en': 'Subscription',
                'ja': '購読',
                'zh': '订阅',
                'category': 'navigation'
            },
            'nav.partners': {
                'ko': '홍보파트너',
                'en': 'Partners',
                'ja': 'パートナー',
                'zh': '合作伙伴',
                'category': 'navigation'
            },
            
            # 버튼
            'btn.login': {
                'ko': '로그인',
                'en': 'Login',
                'ja': 'ログイン',
                'zh': '登录',
                'category': 'buttons'
            },
            'btn.register': {
                'ko': '회원가입',
                'en': 'Sign Up',
                'ja': '登録',
                'zh': '注册',
                'category': 'buttons'
            },
            'btn.logout': {
                'ko': '로그아웃',
                'en': 'Logout',
                'ja': 'ログアウト',
                'zh': '退出',
                'category': 'buttons'
            },
            'btn.save': {
                'ko': '저장',
                'en': 'Save',
                'ja': '保存',
                'zh': '保存',
                'category': 'buttons'
            },
            'btn.cancel': {
                'ko': '취소',
                'en': 'Cancel',
                'ja': 'キャンセル',
                'zh': '取消',
                'category': 'buttons'
            },
            'btn.confirm': {
                'ko': '확인',
                'en': 'Confirm',
                'ja': '確認',
                'zh': '确认',
                'category': 'buttons'
            },
            'btn.submit': {
                'ko': '제출',
                'en': 'Submit',
                'ja': '送信',
                'zh': '提交',
                'category': 'buttons'
            },
            'btn.delete': {
                'ko': '삭제',
                'en': 'Delete',
                'ja': '削除',
                'zh': '删除',
                'category': 'buttons'
            },
            'btn.edit': {
                'ko': '편집',
                'en': 'Edit',
                'ja': '編集',
                'zh': '编辑',
                'category': 'buttons'
            },
            'btn.view': {
                'ko': '보기',
                'en': 'View',
                'ja': '表示',
                'zh': '查看',
                'category': 'buttons'
            },
            
            # 폼 라벨
            'form.email': {
                'ko': '이메일',
                'en': 'Email',
                'ja': 'メール',
                'zh': '邮箱',
                'category': 'forms'
            },
            'form.password': {
                'ko': '비밀번호',
                'en': 'Password',
                'ja': 'パスワード',
                'zh': '密码',
                'category': 'forms'
            },
            'form.username': {
                'ko': '사용자명',
                'en': 'Username',
                'ja': 'ユーザー名',
                'zh': '用户名',
                'category': 'forms'
            },
            'form.name': {
                'ko': '이름',
                'en': 'Name',
                'ja': '名前',
                'zh': '姓名',
                'category': 'forms'
            },
            'form.phone': {
                'ko': '전화번호',
                'en': 'Phone',
                'ja': '電話番号',
                'zh': '电话',
                'category': 'forms'
            },
            
            # 차트 관련
            'chart.price': {
                'ko': '가격',
                'en': 'Price',
                'ja': '価格',
                'zh': '价格',
                'category': 'charts'
            },
            'chart.volume': {
                'ko': '거래량',
                'en': 'Volume',
                'ja': '取引量',
                'zh': '成交量',
                'category': 'charts'
            },
            'chart.high': {
                'ko': '최고가',
                'en': 'High',
                'ja': '高値',
                'zh': '最高价',
                'category': 'charts'
            },
            'chart.low': {
                'ko': '최저가',
                'en': 'Low',
                'ja': '安値',
                'zh': '最低价',
                'category': 'charts'
            },
            'chart.open': {
                'ko': '시가',
                'en': 'Open',
                'ja': '始値',
                'zh': '开盘价',
                'category': 'charts'
            },
            'chart.close': {
                'ko': '종가',
                'en': 'Close',
                'ja': '終値',
                'zh': '收盘价',
                'category': 'charts'
            },
            
            # 예측 관련
            'prediction.title': {
                'ko': '주식 예측',
                'en': 'Stock Prediction',
                'ja': '株価予測',
                'zh': '股价预测',
                'category': 'predictions'
            },
            'prediction.make_prediction': {
                'ko': '예측하기',
                'en': 'Make Prediction',
                'ja': '予測する',
                'zh': '进行预测',
                'category': 'predictions'
            },
            'prediction.accuracy': {
                'ko': '정확도',
                'en': 'Accuracy',
                'ja': '精度',
                'zh': '准确度',
                'category': 'predictions'
            },
            
            # 메시지
            'msg.success': {
                'ko': '성공',
                'en': 'Success',
                'ja': '成功',
                'zh': '成功',
                'category': 'messages'
            },
            'msg.error': {
                'ko': '오류',
                'en': 'Error',
                'ja': 'エラー',
                'zh': '错误',
                'category': 'messages'
            },
            'msg.warning': {
                'ko': '경고',
                'en': 'Warning',
                'ja': '警告',
                'zh': '警告',
                'category': 'messages'
            },
            'msg.info': {
                'ko': '정보',
                'en': 'Info',
                'ja': '情報',
                'zh': '信息',
                'category': 'messages'
            },
            'msg.loading': {
                'ko': '로딩중...',
                'en': 'Loading...',
                'ja': '読み込み中...',
                'zh': '加载中...',
                'category': 'messages'
            },
            'msg.please_wait': {
                'ko': '잠시만 기다려주세요',
                'en': 'Please wait',
                'ja': 'お待ちください',
                'zh': '请稍候',
                'category': 'messages'
            },
            
            # 제휴 파트너
            'affiliate.title': {
                'ko': '홍보파트너 프로그램',
                'en': 'Affiliate Partner Program',
                'ja': 'アフィリエイトパートナープログラム',
                'zh': '推广合作伙伴计划',
                'category': 'affiliate'
            },
            'affiliate.apply': {
                'ko': '파트너 신청하기',
                'en': 'Apply as Partner',
                'ja': 'パートナー申請',
                'zh': '申请成为合作伙伴',
                'category': 'affiliate'
            },
            'affiliate.dashboard': {
                'ko': '파트너 대시보드',
                'en': 'Partner Dashboard',
                'ja': 'パートナーダッシュボード',
                'zh': '合作伙伴仪表板',
                'category': 'affiliate'
            },
            'affiliate.commission': {
                'ko': '수수료',
                'en': 'Commission',
                'ja': '手数料',
                'zh': '佣金',
                'category': 'affiliate'
            },
            'affiliate.referral_link': {
                'ko': '추천 링크',
                'en': 'Referral Link',
                'ja': '紹介リンク',
                'zh': '推荐链接',
                'category': 'affiliate'
            },
            
            # 결제
            'payment.title': {
                'ko': '결제',
                'en': 'Payment',
                'ja': '支払い',
                'zh': '支付',
                'category': 'payments'
            },
            'payment.amount': {
                'ko': '결제 금액',
                'en': 'Payment Amount',
                'ja': '支払い金額',
                'zh': '支付金额',
                'category': 'payments'
            },
            'payment.method': {
                'ko': '결제 방법',
                'en': 'Payment Method',
                'ja': '支払い方法',
                'zh': '支付方式',
                'category': 'payments'
            },
            'payment.success': {
                'ko': '결제가 완료되었습니다',
                'en': 'Payment completed successfully',
                'ja': '支払いが完了しました',
                'zh': '支付成功',
                'category': 'payments'
            },
            'payment.failed': {
                'ko': '결제에 실패했습니다',
                'en': 'Payment failed',
                'ja': '支払いに失敗しました',
                'zh': '支付失败',
                'category': 'payments'
            },
        }
        
        # 언어별로 번역 데이터 생성
        languages = Language.objects.filter(is_active=True)
        
        for key, translations in translations_data.items():
            category = translations.get('category', 'general')
            
            for language in languages:
                if language.code in translations:
                    translation_text = translations[language.code]
                    
                    translation, created = Translation.objects.get_or_create(
                        key=key,
                        language=language,
                        defaults={
                            'value': translation_text,
                            'category': category,
                            'is_validated': True
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'번역 생성: {key} ({language.code}) = {translation_text}')
                    else:
                        # 기존 번역 업데이트
                        translation.value = translation_text
                        translation.category = category
                        translation.save()
                        self.stdout.write(f'번역 업데이트: {key} ({language.code}) = {translation_text}')
        
        self.stdout.write(
            self.style.SUCCESS(f'기본 번역 데이터 생성 완료: {len(translations_data)}개 키')
        )
