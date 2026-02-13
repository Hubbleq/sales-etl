# Gerador de dados de vendas realistas para 2025.
# Cria um CSV com centenas de registros distribuídos ao longo do ano,
# com 5 lojas brasileiras e 15 produtos de tecnologia.
# Inclui sazonalidade (picos em novembro/dezembro por Black Friday e Natal).

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

# Lojas fictícias em 5 capitais brasileiras
LOJAS = [
    ("Loja Centro SP", "São Paulo", "SP"),
    ("Loja Shopping RJ", "Rio de Janeiro", "RJ"),
    ("Loja Asa Norte", "Brasília", "DF"),
    ("Loja Batel", "Curitiba", "PR"),
    ("Loja Savassi", "Belo Horizonte", "MG"),
]

# Catálogo de 15 produtos com preço base
PRODUTOS = [
    ("SKU-001", "Mouse Sem Fio", "Periféricos", 49.90),
    ("SKU-002", "Teclado Mecânico", "Periféricos", 189.90),
    ("SKU-003", "Hub USB-C", "Acessórios", 79.90),
    ("SKU-004", "Suporte Monitor", "Mobiliário", 129.90),
    ("SKU-005", "Webcam Full HD", "Periféricos", 199.90),
    ("SKU-006", "Capa Notebook 15\"", "Acessórios", 59.90),
    ("SKU-007", "Headset Gamer", "Áudio", 249.90),
    ("SKU-008", "Caixa de Som Bluetooth", "Áudio", 159.90),
    ("SKU-009", "Mousepad Gamer XL", "Acessórios", 89.90),
    ("SKU-010", "Cabo HDMI 2m", "Cabos", 34.90),
    ("SKU-011", "Carregador USB-C 65W", "Energia", 119.90),
    ("SKU-012", "SSD Externo 1TB", "Armazenamento", 399.90),
    ("SKU-013", "Pen Drive 128GB", "Armazenamento", 69.90),
    ("SKU-014", "Filtro de Tela Privacidade", "Acessórios", 149.90),
    ("SKU-015", "Luz LED para Mesa", "Iluminação", 179.90),
]

# Multiplicador de volume por mês (simula sazonalidade do varejo)
# Novembro e dezembro têm os maiores volumes (Black Friday + Natal)
SAZONALIDADE = {
    1: 0.7, 2: 0.75, 3: 0.85, 4: 0.9,
    5: 1.0, 6: 0.95, 7: 0.8, 8: 0.85,
    9: 1.0, 10: 1.1, 11: 1.4, 12: 1.6,
}

# Arquivo de saída
OUT_PATH = Path(__file__).resolve().parent / "data" / "sample_sales.csv"


def gerar_vendas() -> list[dict]:
    """Gera uma lista de dicionários com vendas simuladas para cada dia de 2025."""
    rows: list[dict] = []
    start = date(2025, 1, 1)
    end = date(2025, 12, 31)

    current = start
    while current <= end:
        mes_mult = SAZONALIDADE.get(current.month, 1.0)

        # Para cada loja, simula de 0 a 3 transações por dia
        for loja_name, cidade, estado in LOJAS:
            n_transacoes = random.choices(
                [0, 1, 2, 3],
                weights=[0.3, 0.4 * mes_mult, 0.2 * mes_mult, 0.1 * mes_mult],
            )[0]

            for _ in range(n_transacoes):
                sku, nome_prod, categoria, preco_base = random.choice(PRODUTOS)

                # Pequena variação aleatória no preço (+-5%)
                preco = round(preco_base * random.uniform(0.95, 1.05), 2)
                qtd = random.randint(1, 25)

                # Desconto: 60% sem desconto, 30% desconto pequeno, 10% grande
                tipo_desc = random.choices(
                    ["nenhum", "pequeno", "grande"],
                    weights=[0.6, 0.3, 0.1],
                )[0]
                if tipo_desc == "nenhum":
                    desconto = 0.0
                elif tipo_desc == "pequeno":
                    desconto = round(preco * qtd * random.uniform(0.03, 0.08), 2)
                else:
                    desconto = round(preco * qtd * random.uniform(0.10, 0.20), 2)

                rows.append({
                    "sale_date": current.isoformat(),
                    "store_name": loja_name,
                    "city": cidade,
                    "state": estado,
                    "sku": sku,
                    "product_name": nome_prod,
                    "category": categoria,
                    "quantity": qtd,
                    "unit_price": preco,
                    "discount": desconto,
                })

        current += timedelta(days=1)

    return rows


def main():
    """Gera as vendas e salva no arquivo CSV."""
    rows = gerar_vendas()
    random.shuffle(rows)  # Embaralha para parecer mais orgânico

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sale_date", "store_name", "city", "state",
            "sku", "product_name", "category",
            "quantity", "unit_price", "discount",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Geradas {len(rows)} linhas de vendas em {OUT_PATH}")


if __name__ == "__main__":
    main()
