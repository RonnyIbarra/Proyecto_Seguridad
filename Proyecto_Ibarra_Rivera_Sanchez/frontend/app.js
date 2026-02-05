const API_BASE = 'http://localhost:8000'
let authToken = null

function showApp(){
  document.getElementById('app-content').style.display = ''
  document.getElementById('main-nav').style.display = ''
  document.getElementById('btn-logout').style.display = ''
  document.getElementById('auth').style.display = 'none'
}

function hideApp(){
  document.getElementById('app-content').style.display = 'none'
  document.getElementById('main-nav').style.display = 'none'
  document.getElementById('btn-logout').style.display = 'none'
  document.getElementById('auth').style.display = ''
}

async function fetchJson(path, opts = {}){
  const headers = opts.headers || {}
  headers['Content-Type'] = 'application/json'
  if(authToken) headers['Authorization'] = `Bearer ${authToken}`
  const res = await fetch(API_BASE + path, {...opts, headers})
  return res.json().catch(()=>({error:'Respuesta no JSON'}))
}

function show(id, content){
  const el = document.getElementById(id)
  if(!el) return
  el.textContent = typeof content === 'string' ? content : JSON.stringify(content, null, 2)
}

document.addEventListener('DOMContentLoaded', ()=>{
  hideApp()

  document.getElementById('btn-info').addEventListener('click', async ()=>{
    show('info-output','Cargando...')
    const data = await fetchJson('/api/info')
    show('info-output', data)
  })

  document.getElementById('form-register').addEventListener('submit', async (e)=>{
    e.preventDefault()
    const f = e.target
    const body = {username:f.username.value, email:f.email.value, password:f.password.value}
    show('register-result','Enviando...')
    const res = await fetchJson('/api/users/register', {method:'POST', body:JSON.stringify(body)})
    show('register-result', res)
  })

  document.getElementById('form-login').addEventListener('submit', async (e)=>{
    e.preventDefault()
    const f = e.target
    const body = {username:f.username.value, password:f.password.value}
    show('login-result','Enviando...')
    const res = await fetchJson('/api/users/login', {method:'POST', body:JSON.stringify(body)})
    if(res && res.token){
      authToken = res.token
      show('login-result', 'Inicio de sesión correcto')
      showApp()
      // obtener lista inicial de datos
      const list = await fetchJson('/api/data/list')
      show('list-output', list)
    } else {
      show('login-result', res)
    }
  })

  document.getElementById('form-encrypt').addEventListener('submit', async (e)=>{
    e.preventDefault()
    const f = e.target
    const body = {title:f.title.value, data:f.data.value, method:f.method.value}
    show('encrypt-result','Cifrando...')
    const res = await fetchJson('/api/data/encrypt', {method:'POST', body:JSON.stringify(body)})
    show('encrypt-result', res)
  })

  document.getElementById('form-decrypt').addEventListener('submit', async (e)=>{
    e.preventDefault()
    const f = e.target
    const body = {data_id: Number(f.data_id.value)}
    show('decrypt-result','Descifrando...')
    const res = await fetchJson('/api/data/decrypt', {method:'POST', body:JSON.stringify(body)})
    show('decrypt-result', res)
  })

  document.getElementById('btn-list').addEventListener('click', async ()=>{
    show('list-output','Cargando...')
    const res = await fetchJson('/api/data/list')
    show('list-output', res)
  })

  document.getElementById('btn-logout').addEventListener('click', ()=>{
    authToken = null
    hideApp()
    show('login-result','Sesión cerrada')
    show('list-output','')
  })

})
