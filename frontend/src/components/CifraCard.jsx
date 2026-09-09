function CifraCard({ texto, numero }) {
  const numeroFormateado = new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
  }).format(numero);

  return (
    <div className="rounded-2xl bg-secundario/20 p-5 shadow-lg">
      <p className="text-sm font-bold text-texto">{texto}</p>
      <h2 className="mt-3 text-3xl font-bold text-primario">{numeroFormateado} CLP</h2>
    </div>
  );
}

export default CifraCard;