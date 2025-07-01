import { useEffect, useState } from 'react'
import './App.css'

const API_BASE = 'https://6b4c767dc82992.lhr.life';

function App() {
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ title: '', description: '', deadline: '' })
  const [editingId, setEditingId] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)

  // Проверка аутентификации при загрузке
  useEffect(() => {
    checkAuth()
  }, [])

  // Проверка аутентификации
  const checkAuth = async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        credentials: 'include' // Важно для отправки cookies
      })
      if (res.ok) {
        const userData = await res.json()
        setUser(userData)
        setIsAuthenticated(true)
        fetchGoals()
      } else {
        setIsAuthenticated(false)
        setUser(null)
      }
    } catch (e) {
      console.error('Auth check failed:', e)
      setIsAuthenticated(false)
      setUser(null)
    }
  }

  // Автоматический login через Mini App
  useEffect(() => {
    if (isAuthenticated) return
    
    // Проверяем, запущено ли приложение в Telegram Mini App
    if (window.Telegram && window.Telegram.WebApp) {
      const initData = window.Telegram.WebApp.initData
      if (initData) {
        handleTelegramAuth(initData)
      }
    }
  }, [isAuthenticated])

  // Аутентификация через Telegram initData
  const handleTelegramAuth = async (initData) => {
    setError('')
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/auth/signin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // Важно для получения cookies
        body: JSON.stringify({ initData })
      })
      
      if (res.ok) {
        await checkAuth() // Проверяем аутентификацию после входа
      } else {
        const errorData = await res.json()
        setError(errorData.detail || 'Ошибка авторизации')
      }
    } catch (e) {
      setError('Ошибка авторизации')
      console.error('Auth error:', e)
    }
    setLoading(false)
  }

  // Получение целей
  const fetchGoals = async () => {
    if (!isAuthenticated) return
    
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API_BASE}/goals/`, {
        credentials: 'include' // Важно для отправки cookies
      })
      
      if (res.status === 401) {
        // Токен истек, пробуем обновить
        const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
          method: 'POST',
          credentials: 'include'
        })
        
        if (refreshRes.ok) {
          // Повторяем запрос после обновления токена
          const retryRes = await fetch(`${API_BASE}/goals/`, {
            credentials: 'include'
          })
          if (retryRes.ok) {
            const data = await retryRes.json()
            setGoals(data)
          } else {
            throw new Error('Ошибка загрузки целей')
          }
        } else {
          setIsAuthenticated(false)
          setUser(null)
          throw new Error('Сессия истекла')
        }
      } else if (res.ok) {
        const data = await res.json()
        setGoals(data)
      } else {
        throw new Error('Ошибка загрузки целей')
      }
    } catch (e) {
      setError(e.message)
    }
    setLoading(false)
  }

  // Добавление или редактирование цели
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const method = editingId ? 'PUT' : 'POST'
      const url = editingId ? `${API_BASE}/goals/${editingId}` : `${API_BASE}/goals/`
      const payload = {
        ...form,
        deadline: form.deadline ? new Date(form.deadline).toISOString() : null,
        description: form.description || null,
      }
      
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      })
      
      if (res.status === 401) {
        // Токен истек, пробуем обновить
        const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
          method: 'POST',
          credentials: 'include'
        })
        
        if (refreshRes.ok) {
          // Повторяем запрос после обновления токена
          const retryRes = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload),
          })
          
          if (!retryRes.ok) throw new Error('Ошибка сохранения цели')
        } else {
          setIsAuthenticated(false)
          setUser(null)
          throw new Error('Сессия истекла')
        }
      } else if (!res.ok) {
        throw new Error('Ошибка сохранения цели')
      }
      
      setForm({ title: '', description: '', deadline: '' })
      setEditingId(null)
      fetchGoals()
    } catch (e) {
      setError(e.message)
    }
  }

  // Удаление цели
  const handleDelete = async (id) => {
    if (!window.confirm('Удалить цель?')) return
    setError('')
    try {
      const res = await fetch(`${API_BASE}/goals/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      
      if (res.status === 401) {
        // Токен истек, пробуем обновить
        const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
          method: 'POST',
          credentials: 'include'
        })
        
        if (refreshRes.ok) {
          // Повторяем запрос после обновления токена
          const retryRes = await fetch(`${API_BASE}/goals/${id}`, {
            method: 'DELETE',
            credentials: 'include'
          })
          
          if (!retryRes.ok) throw new Error('Ошибка удаления')
        } else {
          setIsAuthenticated(false)
          setUser(null)
          throw new Error('Сессия истекла')
        }
      } else if (!res.ok) {
        throw new Error('Ошибка удаления')
      }
      
      fetchGoals()
    } catch (e) {
      setError(e.message)
    }
  }

  // Начать редактирование
  const handleEdit = (goal) => {
    setForm({
      title: goal.title,
      description: goal.description || '',
      deadline: goal.deadline ? goal.deadline.slice(0, 16) : '',
    })
    setEditingId(goal.id)
  }

  // Выход
  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })
    } catch (e) {
      console.error('Logout error:', e)
    }
    
    setIsAuthenticated(false)
    setUser(null)
    setGoals([])
  }

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h2>Мои цели</h2>
      {error && <div style={{ color: 'red', marginBottom: 16 }}>{error}</div>}
      
      {!isAuthenticated && (
        <div style={{ margin: '32px 0', textAlign: 'center' }}>
          {loading ? (
            <div>Авторизация...</div>
          ) : (
            <div>
              <p>Для использования приложения необходимо авторизоваться через Telegram</p>
              {window.Telegram && window.Telegram.WebApp ? (
                <p>Откройте приложение через Telegram бота</p>
              ) : (
                <p>Это приложение работает только в Telegram Mini App</p>
              )}
            </div>
          )}
        </div>
      )}
      
      {isAuthenticated && user && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <strong>Пользователь:</strong> {user.first_name} {user.last_name}
              {user.username && <span> (@{user.username})</span>}
            </div>
            <button onClick={handleLogout}>Выйти</button>
          </div>
          
          <form onSubmit={handleSubmit} style={{ marginBottom: 24 }}>
            <input
              type="text"
              placeholder="Название"
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              required
              style={{ width: '100%', marginBottom: 8 }}
            />
            <textarea
              placeholder="Описание"
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              style={{ width: '100%', marginBottom: 8 }}
            />
            <input
              type="datetime-local"
              value={form.deadline}
              onChange={e => setForm(f => ({ ...f, deadline: e.target.value }))}
              style={{ width: '100%', marginBottom: 8 }}
            />
            <button type="submit">{editingId ? 'Сохранить' : 'Добавить'}</button>
            {editingId && (
              <button type="button" onClick={() => { 
                setEditingId(null); 
                setForm({ title: '', description: '', deadline: '' }); 
              }}>
                Отмена
              </button>
            )}
          </form>
          
          {loading ? (
            <div>Загрузка...</div>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {goals.map(goal => (
                <li key={goal.id} style={{ border: '1px solid #ccc', padding: 12, marginBottom: 8, borderRadius: 6 }}>
                  <div><b>{goal.title}</b></div>
                  {goal.description && <div>{goal.description}</div>}
                  {goal.deadline && <div>Дедлайн: {new Date(goal.deadline).toLocaleString()}</div>}
                  <div>Статус: {goal.is_completed ? '✅ Выполнено' : '⏳ В процессе'}</div>
                  <button onClick={() => handleEdit(goal)} style={{ marginRight: 8 }}>Редактировать</button>
                  <button onClick={() => handleDelete(goal.id)}>Удалить</button>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  )
}

export default App
