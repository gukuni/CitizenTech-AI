"""Cálculos da comparação de alternativas para o banho (chuveiro elétrico).

Todas as premissas vêm de dados/premissas.csv. Cada uma está marcada como
dado ou estimativa; nenhum resultado é garantido.
"""
import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CAMINHO_PREMISSAS = RAIZ / "premissas.csv"


def carregar_premissas(caminho=CAMINHO_PREMISSAS):
    """Lê o CSV e devolve {chave: {valor, unidade, tipo, fonte}}."""
    premissas = {}
    with open(caminho, encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            premissas[linha["chave"]] = {
                "valor": float(linha["valor"]),
                "unidade": linha["unidade"],
                "tipo": linha["tipo"],
                "fonte": linha["fonte"],
            }
    return premissas


def valores(premissas):
    return {k: v["valor"] for k, v in premissas.items()}


def tarifa_final(p, adicional_bandeira=0.0):
    """Tarifa em R$/kWh com impostos (estimados). Bandeira entra antes dos impostos."""
    return (p["tarifa_sem_impostos"] + adicional_bandeira) * p["fator_impostos"]


def consumo_kwh_mes(potencia_w, minutos_banho, pessoas, dias):
    """Energia = potência (kW) x tempo (h). Um banho por pessoa por dia."""
    horas_dia = pessoas * minutos_banho / 60
    return potencia_w / 1000 * horas_dia * dias


def comparar(p, adicional_bandeira=0.0):
    """Compara Base, A (hábitos) e B (aquecedor solar) para o mesmo mês."""
    tarifa = tarifa_final(p, adicional_bandeira)
    base_kwh = consumo_kwh_mes(p["potencia_chuveiro_w"], p["banho_min"], p["pessoas"], p["dias_mes"])
    a_kwh = consumo_kwh_mes(p["potencia_chuveiro_w"] * p["fator_potencia_a"], p["banho_a_min"], p["pessoas"], p["dias_mes"])
    b_kwh = base_kwh * (1 - p["fracao_solar"])

    cenarios = {
        "Base (chuveiro atual)": (base_kwh, 0.0),
        "A) Hábitos e regulagem": (a_kwh, 0.0),
        "B) Aquecedor solar": (b_kwh, p["custo_solar"]),
    }
    resultado = {}
    for nome, (kwh, custo_inicial) in cenarios.items():
        eco_kwh = base_kwh - kwh
        eco_mes = eco_kwh * tarifa
        eco_ano = eco_mes * 12
        resultado[nome] = {
            "consumo_kwh_mes": kwh,
            "custo_mes": kwh * tarifa,
            "economia_kwh_mes": eco_kwh,
            "economia_mes": eco_mes,
            "economia_ano": eco_ano,
            "custo_inicial": custo_inicial,
            "payback_anos": (custo_inicial / eco_ano) if custo_inicial and eco_ano > 0 else None,
            "co2_evitado_kg_ano": eco_kwh * 12 * p["fator_emissao"],
        }
    resultado["B) Aquecedor solar"]["ganho_liquido_vida_util"] = (
        resultado["B) Aquecedor solar"]["economia_ano"] * p["vida_util_solar"] - p["custo_solar"]
    )
    return resultado


def area_coletor_m2(p):
    """Área aproximada de coletor para a fração solar assumida (estimativa grosseira)."""
    base_kwh_dia = consumo_kwh_mes(p["potencia_chuveiro_w"], p["banho_min"], p["pessoas"], p["dias_mes"]) / p["dias_mes"]
    energia_util = base_kwh_dia * p["fracao_solar"]
    return energia_util / (p["irradiacao"] * p["eficiencia_coletor"])


def cenarios_sensibilidade(p):
    """Resultados sob tarifas e bandeiras diferentes (a tarifa é a premissa mais incerta)."""
    casos = [
        ("Tarifa -20%", dict(), 0.8),
        ("Tarifa base, bandeira verde", dict(), 1.0),
        ("Tarifa +20%", dict(), 1.2),
        ("Base + bandeira amarela", dict(adicional_bandeira=p["bandeira_amarela"]), 1.0),
        ("Base + bandeira vermelha 1", dict(adicional_bandeira=p["bandeira_vermelha1"]), 1.0),
    ]
    saida = []
    for nome, kwargs, mult in casos:
        q = dict(p)
        q["tarifa_sem_impostos"] = p["tarifa_sem_impostos"] * mult
        r = comparar(q, **kwargs)
        saida.append((nome, r["A) Hábitos e regulagem"]["economia_ano"],
                      r["B) Aquecedor solar"]["economia_ano"], r["B) Aquecedor solar"]["payback_anos"]))
    return saida


def brl(x):
    return "R$ " + f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_relatorio(premissas=None):
    premissas = premissas or carregar_premissas()
    p = valores(premissas)
    r = comparar(p)
    linhas = ["# Comparação das alternativas (gerado por src/calculos.py)", "",
              f"Cenário: {int(p['pessoas'])} pessoas, banho de {p['banho_min']:.0f} min, chuveiro de "
              f"{p['potencia_chuveiro_w']:.0f} W, tarifa final estimada de {brl(tarifa_final(p))}/kWh.", "",
              "| Alternativa | Consumo (kWh/mês) | Custo/mês | Economia/mês | Economia/ano | Custo inicial | Payback | CO₂ evitado (kg/ano) |",
              "|---|---|---|---|---|---|---|---|"]
    for nome, d in r.items():
        pb = f"{d['payback_anos']:.1f} anos" if d["payback_anos"] else "imediato"
        linhas.append(f"| {nome} | {d['consumo_kwh_mes']:.1f} | {brl(d['custo_mes'])} | {brl(d['economia_mes'])} | "
                      f"{brl(d['economia_ano'])} | {brl(d['custo_inicial'])} | {pb} | {d['co2_evitado_kg_ano']:.1f} |")
    linhas += ["", f"Ganho líquido do aquecedor solar em {p['vida_util_solar']:.0f} anos (sem desconto, sem manutenção): "
               f"{brl(r['B) Aquecedor solar']['ganho_liquido_vida_util'])}.",
               f"Área de coletor aproximada: {area_coletor_m2(p):.1f} m² (estimativa grosseira).", "",
               "## Sensibilidade à tarifa e à bandeira", "",
               "| Cenário | Economia/ano A | Economia/ano B | Payback B |", "|---|---|---|---|"]
    for nome, ea, eb, pb in cenarios_sensibilidade(p):
        linhas.append(f"| {nome} | {brl(ea)} | {brl(eb)} | {pb:.1f} anos |")
    linhas += ["", "> Todos os valores são estimativas condicionadas às premissas em `dados/premissas.csv`. "
               "Não são garantia de economia."]
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    texto = gerar_relatorio()
    (RAIZ / "comparacao_alternativas.md").write_text(texto, encoding="utf-8")
    print(texto)
