function CifraCard({ texto, numero }) {
  return (
    <div className="rounded-2xl bg-secundario/50 p-5 shadow-lg">
      <p className="text-sm text-texto">{texto}</p>
      <h2 className="mt-3 text-3xl font-bold text-primario">{numero} CLP</h2>
    </div>
  );
}

export default CifraCard;