import { useEffect, useState } from 'react'
import { api } from '../api'
import SealBadge from '../components/SealBadge'

export default function Verify() {
  const [inv, setInv] = useState([])
  const [runs, setRuns] = useState([])
  const [gate, setGate] = useState(null)
  const [last, setLast] = useState(null)
  const [msg, setMsg] = useState('')
  const reload = () => {
    api.inventory().then(setInv)
    api.verifyRuns().then(setRuns)
    api.writeGate().then(setGate)
  }
  useEffect(() => { reload() }, [])
  async function run() {
    setMsg('')
    try {
      const r = await api.runVerify()
      setLast(r)
      setGate(r.写闸)
      setMsg(`互证${r.status} · 漂移 ${r.drift_count}` + (r.写闸?.封印 ? ' · 当日写闸已封印' : ''))
      reload()
    } catch (e) { setMsg(e.message) }
  }
  return (
    <div className="page">
      <h1>目录互证</h1>
      <p className="lede">对照湖目录对象清单与分区素材元数据，不是网盘文件浏览器。互证一致即封印当日三个写入口。</p>
      <button type="button" onClick={run}>跑一次互证</button>
      {msg && <p className="msg">{msg}</p>}
      {gate && <SealBadge gate={gate} />}
      {last && last.drifts?.length > 0 && (
        <ul className="plain">{last.drifts.map((d, i) => <li key={i}>{d.对象键} · {d.问题}</li>)}</ul>
      )}
      <h2>目录清单</h2>
      <div className="table-wrap">
        <table>
          <thead><tr><th>对象键</th><th>字节</th><th>片库间</th><th>扫描时刻</th></tr></thead>
          <tbody>{inv.map(x => <tr key={x.id}><td>{x.object_key}</td><td>{x.bytes}</td><td>{x.vault_name}</td><td>{x.scanned_at}</td></tr>)}</tbody>
        </table>
      </div>
      <h2>互证流水 <span className="muted">写闸由此重放</span></h2>
      <div className="table-wrap">
        <table>
          <thead><tr><th>编号</th><th>营业日</th><th>状态</th><th>漂移数</th><th>时间</th></tr></thead>
          <tbody>{runs.map(r => <tr key={r.id}><td>{r.id}</td><td>{r.biz_day}</td><td>{r.status}</td><td>{r.drift_count}</td><td>{r.created_at}</td></tr>)}</tbody>
        </table>
      </div>
    </div>
  )
}
