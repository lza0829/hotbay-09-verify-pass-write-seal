import { useEffect, useState } from 'react'
import { api } from '../api'
import SealBadge from '../components/SealBadge'

export default function Settings() {
  const [day, setDay] = useState('')
  const [gate, setGate] = useState(null)
  const [msg, setMsg] = useState('')
  useEffect(() => {
    api.settings().then(s => setDay(s.营业日 || ''))
    api.writeGate().then(setGate)
  }, [])
  async function save(e) {
    e.preventDefault()
    try {
      const r = await api.setDay(day)
      setMsg(`营业日已设为 ${r.营业日}` + (r.写闸?.封印 ? ' · 该日写闸已封印' : ' · 该日写闸放行'))
      setGate(r.写闸)
    } catch (err) { setMsg(err.message) }
  }
  return (
    <div className="page">
      <h1>营业日</h1>
      <p className="lede">营业日是写闸的解封/复封杠杆：切到当日尚无一致互证流水的一天即解封；切回已封印的营业日会重新封印。</p>
      <form className="panel form row" onSubmit={save}>
        <label>营业日<input type="date" value={day} onChange={e => setDay(e.target.value)} /></label>
        <button type="submit">保存</button>
      </form>
      {msg && <p className="msg">{msg}</p>}
      <SealBadge gate={gate} />
    </div>
  )
}
