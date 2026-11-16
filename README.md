# Diagrama Ternário LCPETRO

Página interativa (HTML único, sem dependências de servidor) para construir diagramas ternários de sistemas água / óleo / tensoativo-cotensoativo a partir de titulações de laboratório, com classificação de Winsor (I–IV) e emulsão.

Desenvolvida no LCPETRO (Laboratório de Engenharia e Ciências do Petróleo, UFPA, Campus de Salinópolis).

## O que faz

- Vértices: tensoativo/cotensoativo (C/T) no topo, água à esquerda, óleo à direita; frações em massa.
- **Linhas de titulação em tabela**: peso do tubo com peixe, massa de C/T, fase fixa (óleo, titulando água, ou água, titulando óleo) e sua massa; a cada adição registra-se a massa total lida na balança e o sistema calcula o titulante acumulado e a composição. Cada linha começa no ponto de origem (0 % de titulante) sobre a aresta correspondente.
- **Transições de fase**: em cada adição marca-se se houve transição e qual a nova classe (Winsor I, II, III, IV ou Emulsão), que vale até a próxima transição.
- **Pontos avulsos** (composições diretas em %).
- **Visualizações**: pontos; regiões em área (mapa por classe, fronteira pela 1ª transição de cada linha, nomes das regiões); envoltória convexa por classe.
- Marcadores vazados ou preenchidos; cores por classe com paleta de cores claras clássicas, branco (só contornos) ou seletor completo.
- **Projetos e diagramas**: vários projetos (por exemplo, um por orientando), cada um com vários diagramas; renomear, duplicar, mover e excluir (com confirmação); desfazer/refazer com Ctrl+Z / Ctrl+Y.
- Exportação em SVG, PNG (3×), CSV de pontos e JSON (um diagrama ou todos os projetos); importação de JSON e de CSV de pontos.
- Os dados ficam salvos no navegador (localStorage); use "Salvar JSON" para levar para outro computador.

## Uso

Abra `index.html` em um navegador moderno. A página também está publicada como artefato no claude.ai; a versão publicada usa o recurso de download do artefato, e fora dele os botões "Salvar …" ficam ocultos (use "Copiar SVG" ou o campo JSON).

## Estrutura dos dados (JSON)

```json
{
  "projects": [
    {
      "name": "Mestrado Luciane",
      "diagrams": [
        {
          "name": "DL1",
          "vertices": {"top": "Tween 80 / n-butanol (1:1)", "left": "Água (HCl 15%)", "right": "Óleo de açaí"},
          "series": [
            {
              "name": "5:5", "tube": 0, "sc": 0.8192, "fixed": "oil", "fixedMass": 0.7998, "init": "I",
              "rows": [{"total": 1.8007, "trans": false, "to": "I", "note": ""}]
            }
          ],
          "free": [],
          "opts": {"view": "both", "hollow": true}
        }
      ]
    }
  ]
}
```

`sc` é a massa de C/T (g); `fixed` indica a fase fixa (`oil` ou `water`) e `fixedMass` a sua massa; `rows[].total` é a massa total lida na balança após cada adição; `trans`/`to` registram a transição de fase.

## Licença

MIT.
