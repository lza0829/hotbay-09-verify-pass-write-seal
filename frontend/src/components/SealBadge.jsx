export default function SealBadge({ gate }) {
  if (!gate) return null
  return (
    <section className={gate.封印 ? 'panel seal on' : 'panel seal'} style={{ marginTop: 14 }}>
      <h2>写闸 · {gate.封印 ? '当日已封印' : '放行'}</h2>
      <p className="muted">营业日 {gate.营业日} · {gate.规则}</p>
      {gate.依据流水 && (
        <p className="muted">
          依据：互证流水 #{gate.依据流水.id}（{gate.依据流水.status} · 漂移 {gate.依据流水.drift_count}）· {gate.依据流水.created_at}
        </p>
      )}
      <ul className="plain">
        {gate.各口.map(d => (
          <li key={d.门}>{d.门} · {d.允许 ? '可写' : '已挡'} · {d.因}</li>
        ))}
      </ul>
      {gate.解封 && <p className="muted">解封：{gate.解封}</p>}
    </section>
  )
}
