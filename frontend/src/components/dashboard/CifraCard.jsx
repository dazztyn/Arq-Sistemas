function CifraCard({ texto, numero }) {
  // null significa "no se pudo calcular" (la API de divisas no respondió), que no
  // es lo mismo que cero: mostrar $0 haría creer que el usuario no gasta nada.
  const numeroFormateado =
    numero == null
      ? "—"
      : new Intl.NumberFormat('es-CL', {
          style: 'currency',
          currency: 'CLP',
          minimumFractionDigits: 0,
        }).format(numero);

  return (
    <div className="rounded-2xl bg-secundario/20 p-5 shadow-lg">
      <p className="text-sm font-bold text-texto">{texto}</p>
      {/* Intl con currency: 'CLP' ya imprime el símbolo, agregar " CLP" lo duplicaba */}
      <h2 className="mt-3 text-3xl font-bold text-primario">{numeroFormateado}</h2>
    </div>
  );
}

export default CifraCard;
