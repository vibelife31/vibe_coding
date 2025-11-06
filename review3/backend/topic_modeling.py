# -*- coding: utf-8 -*-
"""
토픽 모델링 및 t-SNE 시각화 모듈
"""
import re
import base64
from io import BytesIO
from typing import List, Dict, Any

import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.manifold import TSNE

# matplotlib 설정 (인코딩 문제 방지를 위해 영문 사용)
import matplotlib
matplotlib.use('Agg')  # GUI 없이 사용
import warnings
warnings.filterwarnings('ignore')  # 경고 무시

def preprocess_korean_text(text: str) -> str:
    """
    한글 텍스트 전처리
    - 한글, 영문, 숫자만 유지
    - 특수문자 제거
    """
    if not text:
        return ""
    
    # 한글, 영문, 숫자, 공백만 유지
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
    # 여러 공백을 하나로
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_adjectives(text: str) -> List[str]:
    """
    형용사만 추출하는 함수
    KoNLPy가 설치되어 있으면 사용, 없으면 간단한 방법 사용
    """
    # 전처리
    text = preprocess_korean_text(text)
    
    try:
        # KoNLPy의 Okt 사용 시도
        from konlpy.tag import Okt
        okt = Okt()
        
        # 형태소 분석 및 형용사만 추출
        pos_tags = okt.pos(text)
        adjectives = [word for word, pos in pos_tags if pos == 'Adjective' and len(word) >= 2]
        
        return adjectives
    except ImportError:
        # KoNLPy가 없으면 간단한 형용사 패턴 매칭 사용
        return simple_adjective_extraction(text)
    except Exception:
        # 기타 오류 시 대체 방법 사용
        return simple_adjective_extraction(text)

def simple_adjective_extraction(text: str) -> List[str]:
    """
    간단한 형용사 추출 (KoNLPy 없이)
    형용사 어미 패턴을 사용한 휴리스틱 방법
    """
    # 일반적인 한국어 형용사 어미 패턴
    adj_patterns = ['좋', '나쁘', '크', '작', '많', '적', '빠르', '느리', '쉬', '어렵', 
                    '예쁘', '못생기', '맛있', '맛없', '재미있', '재미없', '편하', '불편',
                    '가벼', '무거', '밝', '어두', '따뜻하', '차갑', '깨끗하', '더럽',
                    '새롭', '오래', '높', '낮', '넓', '좁', '두껍', '얇',
                    '강하', '약하', '빠르', '느리', '똑똑하', '멍청하', '친절하', '불친절']
    
    words = text.split()
    adjectives = []
    
    for word in words:
        # 형용사 패턴과 일치하거나
        if any(pattern in word for pattern in adj_patterns):
            adjectives.append(word)
        # 다, 네요, 어요 등의 어미로 끝나는 경우
        elif len(word) >= 2 and any(word.endswith(ending) for ending in ['다', '네요', '어요', '습니다', '아요']):
            adjectives.append(word)
    
    return [adj for adj in adjectives if len(adj) >= 2]

def perform_topic_modeling(
    reviews: List[Dict[str, Any]], 
    n_topics: int = 5,
    n_top_words: int = 10
) -> Dict[str, Any]:
    """
    형용사 기반 토픽 모델링 수행
    
    Args:
        reviews: 리뷰 데이터 리스트 (review_content 필드 필요)
        n_topics: 추출할 토픽 수
        n_top_words: 각 토픽당 상위 형용사 수
    
    Returns:
        토픽 모델링 결과 (토픽, 형용사, t-SNE 차트 등)
    """
    # 리뷰 텍스트 추출
    texts = [r.get('review_content', '') for r in reviews if r.get('review_content')]
    
    if len(texts) < 3:
        raise ValueError("토픽 모델링을 수행하기에 리뷰가 너무 적습니다. (최소 3개 필요)")
    
    # 텍스트 전처리
    processed_texts = [preprocess_korean_text(text) for text in texts]
    
    # CountVectorizer로 문서-단어 행렬 생성 (형용사만)
    vectorizer = CountVectorizer(
        tokenizer=extract_adjectives,
        max_features=500,  # 형용사는 명사보다 적으므로 조정
        min_df=1,  # 최소 1개 문서에 등장 (형용사가 적을 수 있음)
        max_df=0.9  # 90% 이상 문서에 등장하는 단어 제외
    )
    
    try:
        doc_term_matrix = vectorizer.fit_transform(processed_texts)
    except ValueError as e:
        error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
        raise ValueError(f"텍스트 벡터화 실패: 리뷰에서 형용사를 충분히 추출하지 못했습니다. 더 많은 리뷰가 필요하거나 리뷰 내용이 유사할 수 있습니다.")
    except Exception as e:
        raise ValueError(f"형용사 추출 중 오류가 발생했습니다. 리뷰 내용을 확인해주세요.")
    
    if doc_term_matrix.shape[1] < n_topics:
        n_topics = max(2, doc_term_matrix.shape[1] - 1)
    
    # LDA 토픽 모델링
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=50
    )
    
    lda_output = lda_model.fit_transform(doc_term_matrix)
    
    # 토픽별 상위 단어 추출
    feature_names = vectorizer.get_feature_names_out()
    topics = []
    
    for topic_idx, topic in enumerate(lda_model.components_):
        top_words_idx = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics.append({
            'topic_id': topic_idx + 1,
            'words': top_words,
            'weights': [float(topic[i]) for i in top_words_idx]
        })
    
    # 각 문서의 주요 토픽 할당
    doc_topics = []
    for idx, doc_dist in enumerate(lda_output):
        main_topic = int(np.argmax(doc_dist)) + 1
        confidence = float(np.max(doc_dist))
        doc_topics.append({
            'review_index': idx,
            'main_topic': main_topic,
            'confidence': confidence,
            'review_preview': texts[idx][:50] + '...' if len(texts[idx]) > 50 else texts[idx]
        })
    
    # t-SNE 시각화 (2D)
    if lda_output.shape[0] >= 5:  # t-SNE는 최소 5개 샘플 필요
        try:
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(texts) - 1))
            tsne_output = tsne.fit_transform(lda_output)
            
            # t-SNE 차트 생성
            chart_base64 = create_tsne_chart(tsne_output, lda_output, n_topics)
        except Exception:
            # t-SNE 생성 실패 시 차트 없이 진행
            chart_base64 = None
    else:
        chart_base64 = None
    
    return {
        'n_topics': n_topics,
        'topics': topics,
        'doc_topics': doc_topics,
        'chart': chart_base64,
        'total_reviews': len(texts)
    }

def create_tsne_chart(tsne_output: np.ndarray, lda_output: np.ndarray, n_topics: int) -> str:
    """
    t-SNE 차트 생성 및 base64 인코딩
    
    Args:
        tsne_output: t-SNE 결과 (n_samples, 2)
        lda_output: LDA 토픽 분포 (n_samples, n_topics)
        n_topics: 토픽 수
    
    Returns:
        base64 인코딩된 차트 이미지
    """
    try:
        # 각 문서의 주요 토픽 결정
        main_topics = np.argmax(lda_output, axis=1)
        
        # 차트 생성
        plt.figure(figsize=(12, 8))
        
        # 토픽별로 다른 색상
        colors = plt.cm.rainbow(np.linspace(0, 1, n_topics))
        
        for topic_id in range(n_topics):
            indices = main_topics == topic_id
            if np.sum(indices) > 0:
                plt.scatter(
                    tsne_output[indices, 0],
                    tsne_output[indices, 1],
                    c=[colors[topic_id]],
                    label=f'Topic {topic_id + 1}',  # 영문으로 변경 (인코딩 문제 방지)
                    alpha=0.7,
                    s=100,
                    edgecolors='black',
                    linewidth=0.5
                )
        
        plt.title('Review Topic Distribution (t-SNE)', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('t-SNE Dimension 1', fontsize=12)
        plt.ylabel('t-SNE Dimension 2', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 이미지를 base64로 인코딩
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    except Exception:
        # 차트 생성 실패 시 None 반환
        plt.close()
        return None

