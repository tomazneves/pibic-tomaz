# PREDIÇÃO DAS ÁREAS DO CONHECIMENTO DE PRODUÇÕES ACADÊMICAS DE PESQUISADORES DA PUC-RIO

O Quem@PUC é um sistema de recuperação de informações (information retrieval)  e análise estatística sobre professores e pesquisadores da PUC-Rio, bem como de sua produção acadêmica, desenvolvido pelo laboratório TreeTech na mesma universidade, permitindo aos usuários a realização de consultas a sua base de dados com expressões regulares limitadas e a visualização de gráficos acerca da produção científica da Universidade. Embora o sistema seja atualmente usado pela administração da PUC-Rio para acompanhamento estatístico da produção acadêmica dos pesquisadores vinculados à universidade, o sistema não atende a todas as demandas administrativas, incluindo a determinação das áreas do conhecimento mais estudadas na PUC com confiança.
O principal obstáculo para tal análise é oriundo de dados faltantes e ambíguos na plataforma Lattes, tida como a principal fonte de dados para o sistema Quem@PUC, que põe em dúvida algumas estatísticas mais gerais obtidas com base nos mesmos.
Neste trabalho, foi estudada a magnitude das lacunas dos dados relativos às áreas de pesquisa de cada produção cadastrada na plataforma Lattes por pesquisadores associados à PUC-Rio, bem como desenvolvida uma metodologia para reduzi-las. Por fim, os dados enriquecidos com as predições foram utilizados para avaliação estatística setorizada das áreas de pesquisa estudadas na PUC-Rio.

---
## Organização do repositório
- **data_preproc:** Inclui dados usados no tratamento preliminar de dados, como tradução e busca de _abstracts_. Os códigos Python na pasta devem ser rodados em sequência.
- **data_preproc/arvore_do_conhecimento.json:** Arquivo extraído manualmente da Árvore do Conhecimento do CNPq em formato JSON para ser utilizado.
- **data_preproc/areas_fantasma.json:** Arquivo gerado pelo Gemini com classificação das demais áreas, corrigido manualmente.
- **data_preproc/_.json:** Demais arquivos temporários gerados durante a manipulação para gerar o arquivo JSON completo.
- **data_complete.json:** Arquivo de dados JSON completo referenciado no relatório.
- **area_values.json:** Arquivo JSON com pesos e ancestrais da árvore do conhecimento extendida, para evitar reprocessamento.
- **df_*.csv:** Arquivos CSV contendo as dataframes usadas no programa para evitar reprocessamento (atualmente instável).
- **data_relatorio.ipynb:** Notebook usado para gerar dados usados para os gráficos no final do relatório.
- _**main.ipynb:** Arquivo principal do projeto._
