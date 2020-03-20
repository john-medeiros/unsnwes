# Unsnwes

O *unsnwes* é uma ferramenta para coleta de notícias usando RSS.
 O objetivo desta ferramenta é facilitar a coleta de dados para fins de análises.

# Funcionamento

 1. O script lê um arquivo com a lista de links RSS para consumo de notícias ( arquivo: sites.txt);
 2. Para cada site, o programa consome os dados disponíveis e salva em um banco de dados local (./db/local.db). É um banco de dados SQLite simples.
 3. O programa é executado em um loop infinito até que sua execução seja paralisada.