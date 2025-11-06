import { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [appId, setAppId] = useState('')
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [appData, setAppData] = useState(null)
  const [appList, setAppList] = useState([])
  const [loadingList, setLoadingList] = useState(false)
  const [topicModeling, setTopicModeling] = useState(false)
  const [topicResult, setTopicResult] = useState(null)

  // 컴포넌트 마운트 시 앱 목록 불러오기
  useEffect(() => {
    fetchAppList()
  }, [])

  const fetchAppList = async () => {
    setLoadingList(true)
    try {
      const response = await axios.get('/api/apps')
      setAppList(response.data)
    } catch (err) {
      console.error('앱 목록 조회 오류:', err)
    } finally {
      setLoadingList(false)
    }
  }

  const loadAppDetail = async (selectedAppId) => {
    try {
      const response = await axios.get(`/api/apps/${selectedAppId}`)
      setAppData(response.data)
    } catch (err) {
      setError('앱 정보를 불러오는데 실패했습니다.')
    }
  }

  const handleCrawl = async () => {
    if (!appId.trim()) {
      setError('앱 ID를 입력해주세요.')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await axios.post('/api/apps/crawl', {
        app_id: appId
      })
      setAppData(response.data)
      setSuccess('앱 정보와 리뷰가 수집되었습니다!')
      setAppId('')
      // 앱 목록 새로고침
      fetchAppList()
    } catch (err) {
      setError(err.response?.data?.detail || '크롤링 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!appData) return

    setAnalyzing(true)
    setError('')
    setSuccess('')

    try {
      await axios.post('/api/apps/analyze', {
        app_id: appData.app_info.app_id
      })

      // 분석 결과 다시 조회
      const response = await axios.get(`/api/apps/${appData.app_info.app_id}`)
      setAppData(response.data)
      setSuccess('리뷰 분석이 완료되었습니다!')
    } catch (err) {
      setError(err.response?.data?.detail || '분석 중 오류가 발생했습니다.')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleDelete = async () => {
    if (!appData) return
    if (!confirm('정말 삭제하시겠습니까?')) return

    try {
      await axios.delete(`/api/apps/${appData.app_info.app_id}`)
      setAppData(null)
      setSuccess('앱 정보가 삭제되었습니다.')
      // 앱 목록 새로고침
      fetchAppList()
    } catch (err) {
      setError(err.response?.data?.detail || '삭제 중 오류가 발생했습니다.')
    }
  }

  const handleTopicModeling = async () => {
    if (!appData) return

    setTopicModeling(true)
    setError('')
    setSuccess('')
    setTopicResult(null)

    try {
      const response = await axios.post('/api/apps/topic-modeling', {
        app_id: appData.app_info.app_id
      })

      setTopicResult(response.data.result)
      setSuccess('토픽 모델링이 완료되었습니다!')
    } catch (err) {
      setError(err.response?.data?.detail || '토픽 모델링 중 오류가 발생했습니다.')
    } finally {
      setTopicModeling(false)
    }
  }

  const renderStars = (rating) => {
    const fullStars = Math.floor(rating)
    const stars = []
    for (let i = 0; i < fullStars; i++) {
      stars.push('⭐')
    }
    return stars.join('')
  }

  return (
    <div className="app">
      <div className="header">
        <h1>📱 앱 리뷰 분석기</h1>
        <p>Google Play Store 앱 리뷰를 수집하고 AI로 분석합니다</p>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="input-section">
        <input
          type="text"
          placeholder="앱 ID를 입력하세요 (예: com.example.app)"
          value={appId}
          onChange={(e) => setAppId(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleCrawl()}
          disabled={loading}
        />
        <button
          className="btn btn-primary"
          onClick={handleCrawl}
          disabled={loading}
        >
          {loading ? '수집 중...' : '리뷰 수집'}
        </button>
      </div>

      <div className="main-content">
        {/* 왼쪽: 앱 목록 */}
        <div className="app-list-sidebar">
          <div className="sidebar-header">
            <h3>📋 등록된 앱 ({appList.length})</h3>
            <button className="btn-refresh" onClick={fetchAppList} disabled={loadingList}>
              🔄
            </button>
          </div>
          
          {loadingList ? (
            <div className="sidebar-loading">불러오는 중...</div>
          ) : appList.length === 0 ? (
            <div className="sidebar-empty">
              <p>등록된 앱이 없습니다</p>
              <p style={{fontSize: '0.85rem', color: '#888'}}>위에서 앱 ID를 입력하여<br/>리뷰를 수집하세요</p>
            </div>
          ) : (
            <div className="app-list">
              {appList.map((app) => (
                <div
                  key={app.id}
                  className={`app-list-item ${appData?.app_info.id === app.id ? 'active' : ''}`}
                  onClick={() => loadAppDetail(app.app_id)}
                >
                  <div className="app-list-item-header">
                    <span className="app-name">{app.app_name}</span>
                    {app.rating && (
                      <span className="app-rating">⭐ {app.rating}</span>
                    )}
                  </div>
                  <div className="app-list-item-meta">
                    <span>{app.review_count}</span>
                    {app.overall_analysis && (
                      <span className="analyzed-badge">✓ 분석완료</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 오른쪽: 상세 정보 */}
        <div className="app-detail-content">

      {/* 로딩 모달 - 리뷰 수집 중 */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-modal">
            <div className="spinner"></div>
            <h3>🔍 리뷰 수집 중</h3>
            <p>Google Play Store에서</p>
            <p>앱 정보와 리뷰를 수집하고 있습니다...</p>
            <div className="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </div>
          </div>
        </div>
      )}

      {/* 로딩 모달 - 분석 중 */}
      {analyzing && (
        <div className="loading-overlay">
          <div className="loading-modal analyzing">
            <div className="spinner"></div>
            <h3>🤖 AI 분석 중</h3>
            <p>Gemini AI가 리뷰를 분석하고 있습니다...</p>
            <p className="sub-text">최대 1분 정도 소요될 수 있습니다</p>
            <div className="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </div>
          </div>
        </div>
      )}

      {/* 로딩 모달 - 토픽 모델링 중 */}
      {topicModeling && (
        <div className="loading-overlay">
          <div className="loading-modal topic-modeling">
            <div className="spinner"></div>
            <h3>📊 형용사 토픽 모델링 중</h3>
            <p>리뷰에서 <strong>형용사</strong>를 추출하고 있습니다...</p>
            <p>주요 토픽을 분류하고 t-SNE 차트를 생성 중...</p>
            <div className="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </div>
          </div>
        </div>
      )}

      {appData && (
        <>
          <div className="app-info-section">
            <div className="app-info-header">
              <h2>{appData.app_info.app_name}</h2>
              <button className="btn btn-danger" onClick={handleDelete}>
                삭제
              </button>
            </div>

            <div className="app-stats">
              <div className="stat-card">
                <h3>⭐ 별점</h3>
                <p>{appData.app_info.rating || '정보 없음'}</p>
              </div>
              <div className="stat-card">
                <h3>리뷰 수</h3>
                <p>{appData.app_info.review_count}</p>
              </div>
              <div className="stat-card">
                <h3>다운로드 수</h3>
                <p>{appData.app_info.download_count}</p>
              </div>
            </div>

            <div className="analyze-section">
              <button
                className="btn btn-secondary"
                onClick={handleAnalyze}
                disabled={analyzing}
              >
                {analyzing ? '분석 중...' : '🤖 앱 리뷰 분석'}
              </button>
              <button
                className="btn btn-topic"
                onClick={handleTopicModeling}
                disabled={topicModeling}
              >
                {topicModeling ? '모델링 중...' : '📊 형용사 토픽 모델링'}
              </button>
            </div>

            {appData.app_info.overall_analysis && (
              <div className="overall-analysis">
                <h3>📊 전체 리뷰 분석</h3>
                <pre>{appData.app_info.overall_analysis}</pre>
              </div>
            )}

            {topicResult && (
              <div className="topic-modeling-result">
                <div className="topic-header">
                  <h3>📊 형용사 기반 토픽 모델링 결과</h3>
                  <button 
                    className="btn-close-topic" 
                    onClick={() => setTopicResult(null)}
                  >
                    ✕
                  </button>
                </div>
                
                <p className="topic-summary">
                  총 {topicResult.total_reviews}개의 리뷰에서 <strong>형용사</strong>를 추출하여 {topicResult.n_topics}개의 토픽으로 분류했습니다.
                </p>

                {/* t-SNE 차트 */}
                {topicResult.chart && (
                  <div className="tsne-chart">
                    <h4>🗺️ 토픽 분포 시각화 (t-SNE)</h4>
                    <img src={topicResult.chart} alt="t-SNE Chart" />
                  </div>
                )}

                {/* 토픽 목록 */}
                <div className="topics-list">
                  <h4>🏷️ 발견된 토픽 (주요 형용사)</h4>
                  {topicResult.topics.map((topic) => (
                    <div key={topic.topic_id} className="topic-card">
                      <h5>토픽 {topic.topic_id}</h5>
                      <div className="topic-words">
                        {topic.words.map((word, idx) => (
                          <span key={idx} className="topic-word" title="형용사">
                            {word}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {/* 문서별 토픽 할당 */}
                <div className="doc-topics">
                  <h4>📝 리뷰별 토픽 분류</h4>
                  <div className="doc-topics-list">
                    {topicResult.doc_topics.slice(0, 10).map((doc) => (
                      <div key={doc.review_index} className="doc-topic-item">
                        <span className={`topic-badge topic-${doc.main_topic}`}>
                          토픽 {doc.main_topic}
                        </span>
                        <span className="confidence">
                          신뢰도: {(doc.confidence * 100).toFixed(1)}%
                        </span>
                        <p className="review-preview">{doc.review_preview}</p>
                      </div>
                    ))}
                    {topicResult.doc_topics.length > 10 && (
                      <p className="more-reviews">
                        ...외 {topicResult.doc_topics.length - 10}개 리뷰
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="reviews-section">
            <h2>💬 리뷰 목록 ({appData.reviews.length}개)</h2>

            {appData.reviews.length === 0 ? (
              <div className="empty-state">
                <h3>리뷰가 없습니다</h3>
                <p>수집된 리뷰가 없습니다.</p>
              </div>
            ) : (
              appData.reviews.map((review) => (
                <div key={review.id} className="review-card">
                  <div className="review-header">
                    <div className="rating">
                      <span className="stars">{renderStars(review.rating)}</span>
                      <span>({review.rating}점)</span>
                    </div>
                    <div className="review-date">{review.review_date}</div>
                  </div>

                  <div className="review-content">
                    {review.review_content}
                  </div>

                  {review.individual_analysis && (
                    <div className="review-analysis">
                      <h4>🔍 AI 분석</h4>
                      <p>{review.individual_analysis}</p>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}

          {!appData && !loading && (
            <div className="empty-state">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3>시작하기</h3>
              <p>왼쪽 목록에서 앱을 선택하거나<br/>위에서 새 앱 ID를 입력하세요</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App


