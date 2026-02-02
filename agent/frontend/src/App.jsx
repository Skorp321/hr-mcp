import { useState, useRef, useEffect } from 'react'
import './App.css'

const API_BASE = '/api'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [mcpStatus, setMcpStatus] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    fetch(`${API_BASE}/mcp/status`)
      .then((r) => r.json())
      .then(setMcpStatus)
      .catch(() => setMcpStatus({ connected: false, error: 'Не удалось загрузить статус' }))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }))
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, history }),
      })
      const data = await res.json()
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response || 'Ошибка получения ответа' },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Ошибка: ${err.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>HR-ассистент</h1>
        <p className="subtitle">Задайте вопрос об отпусках, персональных днях, больничных и льготах</p>
        {mcpStatus && (
          <div className={`mcp-status ${mcpStatus.connected ? 'connected' : 'disconnected'}`}>
            <span className="mcp-dot" title={mcpStatus.connected ? 'MCP подключён' : 'MCP отключён'} />
            MCP: {mcpStatus.connected ? (
              <span>подключён — инструменты: {mcpStatus.tools?.map((t) => t.name).join(', ') || '—'}</span>
            ) : (
              <span>{mcpStatus.error || 'нет соединения'}</span>
            )}
          </div>
        )}
      </header>

      <div className="chat">
        {messages.length === 0 && (
          <div className="welcome">
            <p>Например:</p>
            <ul>
              <li>Сколько дней отпуска у сотрудника ivanov?</li>
              <li>Как оформить больничный?</li>
              <li>Какие персональные дни есть у petrova?</li>
            </ul>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="bubble">{msg.content}</div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="bubble typing">Думаю...</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Введите вопрос..."
          rows={2}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          Отправить
        </button>
      </div>
    </div>
  )
}

export default App
