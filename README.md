# Zap2-Userside

Este projeto visa simular uma aplicação de chat com criptografia de ponta-a-ponta rodando através de um servidor websocket. Para isso, foi implementada a Double Ratchet Encryption (Criptografia de Catraca Dupla), implementada de acordo com a ótima explicação do post https://nfil.dev/coding/encryption/python/double-ratchet-example/.

As ferramentas mais utilizadas pelo projeto são
  * O módulo de criptografia: A partir do qual são geradas as chaves primárias e públicas a em cima das quais são executados as trocas de inforamações necessárias do protocolo de comunicação.
  * O módulo do socket-io: Também tenho implementado um repositório que haje como servidor para que haja comunicação entre dois usuários. O funcionamento esperado de uma comunicação completa pode ser obtido a partir do módulo `crypto_tester.py` implementado para que seja possível utilizar este módulo como um stand alone
  * O módulo do pymongo: O pymongo foi utilizado para armazer as informações dos usuários e dos chats e as mensagens trocadas
  * Também é utilizado o gevent para trabalhar com threading

Os testes que implementamos foram direcionados às funções relacionadas a criptografia na troca de mensagem e em cima das funções do módulo Api que envia mensagens para o servidor.

Para a configuração do GitHub Actions no projeto, utilizamos na documentação que o Git possui. Configuramos o Actions dentro do próprio navegador, o que facilita nosso trabalho, já que nos permite escolher um setup pré-configurado, de acordo com a tecnologia que iremos utilizar. Escolhemos portanto o "Python Application", e realizamos apenas a modificação de colocar uma versão do python que fosse igual a usada durante o nosso desenvolvimento.

