# LLM-TextAnalyzer

**LLM-TextAnalyzer** è un prototipo progettato per supportare l'analisi automatica di testi utilizzando modelli di machine learning, in particolare Large Language Models (LLMs). Il progetto è in grado di leggere file JSON o CSV contenenti testi, eseguire interrogazioni basate su un set di domande predefinite, e salvare i risultati in un database NoSQL.

## Funzionalità principali:
- **Lettura di dati da file JSON o CSV**: Il sistema è in grado di elaborare file contenenti una serie di testi (ad esempio, abstract di articoli scientifici).
- **Esecuzione di interrogazioni automatiche**: Un set predefinito di domande viene sottoposto automaticamente a ciascun testo, utilizzando modelli LLM per rispondere a richieste come:
  - Estrazione di parole chiave
  - Riassunti
  - Verifica della coerenza con un argomento specifico
- **Salvataggio dei risultati**: I risultati delle interrogazioni vengono memorizzati in un database NoSQL per analisi e consultazione future.
- **Architettura scalabile**: La struttura del prototipo può essere estesa per supportare ambienti distribuiti, ad esempio, distribuendo il contenuto JSON su Kafka tramite connettori come [Kafka Connect File Pulse](https://github.com/streamthoughts/kafka-connect-file-pulse).
- **Supporto a soluzioni LLM pronte all'uso**: Il prototipo è compatibile con soluzioni esistenti per l'esecuzione di modelli LLM on-premise, come [OnPrem LLM](https://github.com/amaiya/onprem).

## Obiettivi futuri:
- Supporto per ulteriori formati di file.
- Integrazione con altre piattaforme di streaming.
- Ottimizzazione per l'analisi su larga scala.

## Architettura
![Big data drawio](https://github.com/user-attachments/assets/c0172e78-6f93-4f7b-8dda-b71404f0c704)
