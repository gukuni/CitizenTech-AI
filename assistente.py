
from calculos import (carregar_premissas, valores, comparar, tarifa_final,
                      area_coletor_m2, brl)

LIMITACOES = (
    "Limitações: valores são ESTIMATIVAS, não garantias. Dependem da tarifa da sua distribuidora, da "
    "bandeira do mês, do seu uso real, do espaço e da orientação do telhado e do orçamento do "
    "aquecedor solar. Confira o valor do kWh na sua conta de luz."
)
FONTES = (
    "Fontes: ANEEL (tarifas e bandeiras); matérias sobre o reajuste da Enel SP (jul/2026); "
    "CRESESB/INPE (irradiação solar); MCTI (fator de emissão). Detalhes em docs/referencias.md."
)


def pedir_numero(texto, padrao):
    resposta = input(f"{texto} [{padrao}]: ").strip().replace(",", ".")
    try:
        valor = float(resposta) if resposta else float(padrao)
        return valor if valor > 0 else float(padrao)
    except ValueError:
        print("Não entendi, vou usar o valor padrão.")
        return float(padrao)


def rodape():
    print(f"\n{LIMITACOES}\n{FONTES}\n")


def calcular_e_comparar(p):
    print("\nVamos estimar o consumo do banho na sua casa. Aperte Enter para usar o valor padrão.")
    q = dict(p)
    q["pessoas"] = pedir_numero("Quantas pessoas tomam banho por dia?", p["pessoas"])
    q["banho_min"] = pedir_numero("Quantos minutos dura cada banho?", p["banho_min"])
    q["potencia_chuveiro_w"] = pedir_numero("Potência do chuveiro (W, veja na etiqueta)", p["potencia_chuveiro_w"])
    r = comparar(q)
    base, a, b = r["Base (chuveiro atual)"], r["A) Hábitos e regulagem"], r["B) Aquecedor solar"]
    print(f"\nHoje, o chuveiro consome cerca de {base['consumo_kwh_mes']:.0f} kWh/mês, "
          f"ou {brl(base['custo_mes'])}/mês (tarifa estimada de {brl(tarifa_final(q))}/kWh).")
    print(f"\nA) Banho de {q['banho_a_min']:.0f} min e posição morna parte do tempo: economiza cerca de "
          f"{brl(a['economia_mes'])}/mês, sem custo inicial.")
    print(f"B) Aquecedor solar (cobre ~{q['fracao_solar']*100:.0f}% do aquecimento): economiza cerca de "
          f"{brl(b['economia_mes'])}/mês; custo estimado de {brl(b['custo_inicial'])}, retorno em "
          f"~{b['payback_anos']:.1f} anos; coletor de ~{area_coletor_m2(q):.1f} m².")
    print(f"Impacto ambiental: A evita ~{a['co2_evitado_kg_ano']:.0f} kg de CO2/ano e B ~{b['co2_evitado_kg_ano']:.0f} kg, "
          "pouco porque a rede elétrica brasileira já é majoritariamente renovável.")
    print("\nRecomendação: comece pela alternativa A, que é imediata e não custa nada. Se você tem "
          "telhado ou laje com sol e consegue investir, o aquecedor solar (B) compensa no longo prazo.")
    rodape()


RESPOSTAS = {
    ("chuveiro", "gasta", "consome"): "O chuveiro elétrico transforma quase toda a energia em calor, e é um dos maiores consumidores da casa. Quanto mais tempo e mais quente, mais energia.",
    ("solar", "aquecedor", "renovavel", "renovável"): "O aquecedor solar usa o calor do sol para esquentar a água e reduz o uso do chuveiro elétrico. Em dias nublados, o chuveiro entra como apoio.",
    ("economizar", "reduzir", "dica"): "Banhos mais curtos, posição morna sempre que possível e desligar a água na hora de ensaboar reduzem o consumo sem custo.",
    ("bandeira",): "A bandeira tarifária (verde, amarela ou vermelha) é um adicional mensal na conta definido pela ANEEL. Na verde não há cobrança extra.",
    ("co2", "ambiente", "emissao", "emissão"): "A economia de energia reduz emissões, mas como a rede brasileira é majoritariamente renovável, o ganho em CO2 por casa é pequeno; o ganho principal é financeiro.",
}


def perguntar():
    pergunta = input("\nDigite sua dúvida (ex.: 'como economizar?', 'o que é bandeira?'): ").lower()
    for chaves, resposta in RESPOSTAS.items():
        if any(c in pergunta for c in chaves):
            print(f"\n{resposta}")
            rodape()
            return
    print("\nAinda não sei responder isso. Tente falar de chuveiro, aquecedor solar, economia, bandeira ou CO2.\n")


def menu():
    p = valores(carregar_premissas())
    print("=== Citizen Assist AI | Energia: seu banho e a conta de luz ===")
    while True:
        print("\n1) Estimar meu consumo e comparar alternativas\n2) Fazer uma pergunta\n3) Ver fontes e limitações\n0) Sair")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            calcular_e_comparar(p)
        elif opcao == "2":
            perguntar()
        elif opcao == "3":
            rodape()
        elif opcao == "0":
            print("Até mais!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
