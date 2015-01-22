
Develop the Hadoop streaming program locally by passing the example input data to it in stdin:

    cat input-data-example.xml | python test-wordsplitter.py

Once the output looks good, upload the streaming program to S3 with the upload script, and run it in EMR.
