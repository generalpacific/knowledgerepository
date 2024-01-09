# Personal Knowlege Repository Tools

These are set of tools that help manage the content that the user reads from
various sources. Following sources are currently supported:
* Kindle highlights
* Liked tweets

`KnowledgeAnki` takes this content and creates a bite sized digest daily based
on the recency of the content for spaced repetition. 

### Links:

* [Architecture](https://github.com/generalpacific/knowledgerepository/blob/master/documentation/Architecture.md)

## List Tools:

### Kindle Highlights Ingestor:
  * This tool logs into your Amazon account and downloads all the recent
    highlights from the books you are reading and uploads them to DynamoDB.

### Web:
* This is website that will show the daily highlights.

### KnowledgeAnki:
* Engine that processes the content to create a daily digest.
* The engine takes into account the recency and upvotes of the entity in the
  repository to create the digest based on principles of spaced repetition.
* Read about spaced repetition more here: https://en.wikipedia.org/wiki/Spaced_repetition 

### Tweets fetcher:
* Tool to fetch the tweet ids of the tweets liked by the user daily.

### Email sender:
* Tool that sends the email of the digest daily.

### Web Entity Ingester Chrome Extension
* A chrome extension that allows selecting a line or paragraph on the website
  and ingests that entity.

## Future improvements:

### Audio to text from podcasts:
* A tool that captures snippets from podcasts that the user is listening and
  ingests in the enginet.

### Content Sumamrizer:
* Based on the content read, creates summaries of various content ingested in
  the engine.

