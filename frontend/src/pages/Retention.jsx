import { useEffect, useState } from 'react'
import { api } from '../api'
import SealBadge from '../components/SealBadge'

export default function Retention() {
  const [pols, setPols] = useState([])
  const [runs, setRuns] = useState([])
  const [gate, setGate] = useState(null)
  const [policyId, setPolicyId] = useState('')
  const [mode, setMode] = useState('连目录销毁')
  const [msg, setMsg] = useState('')
  const reload = () => { api.policies().then(p => { setPols(p); if (p[0]) setPolicyId(String(p[0].id)) }); api.destroys().then(setRuns); api.writeGate().then(setGate) }
  useEffect(() => { reload() }, [])
  async function run() {
    setMsg('')
    try {
      const r = await api.runRetention({ policy_id: Number(policyId), mode })
      setMsg(`${r.policy} 影响 ${r.affected.length} 条`)
      reload()
    } catch (e) { setMsg(e.message); reload() }
  }
  return (
    <div className="page">
      <h1>片龄保留</h1>
      <SealBadge gate={gate} />
      <div className="panel form row">
        <label>策略<select value={policyId} onChange={e => setPolicyId(e.target.value)}>
          {pols.map(p => <option key={p.id} value={p.id}>{p.name}（{p.max_age_days}天 · {p.action}）</option>)}
        </select></label>
        <label>销毁模式<select value={mode} onChange={e => setMode(e.target.value)}>
          <option>连目录销毁</option><option>只删元数据</option>
        </select></label>
        <button type="button" onClick={run} disabled={gate?.封印}>执行保留</button>
      </div>
      {msg && <p className="msg">{msg}</p>}
      <div className="table-wrap">
        <table>
          <thead><tr><th>流水</th><th>分区</th><th>策略</th><th>模式</th><th>状态</th><th>时间</th></tr></thead>
          <tbody>
            {runs.map(r => (
              <tr key={r.id}><td>{r.id}</td><td>{r.part_key}</td><td>{r.policy_name}</td><td>{r.mode}</td><td>{r.status}</td><td>{r.created_at}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
