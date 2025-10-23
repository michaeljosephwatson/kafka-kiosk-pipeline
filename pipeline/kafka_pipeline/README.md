This is the pipeline for the Kafka stream taking an entry of data and uploading it to the RDS.

It assumes the RDS has already been set up in aws according to the original pipeline. 

If this is not set up, go into original_pipeline and run create_pipeline.sh.

Then do start the pipeline run: python3 consumer.py

