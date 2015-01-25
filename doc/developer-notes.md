

To copy objects from within S3:

    aws s3 cp 
      s3://hadoop-seminar-emr/digitraffic/imported/2014/06/18/ 
      s3://hadoop-seminar-emr/digitraffic/imported/subset-1hour/ 
      --recursive 
      --exclude "*" 
      --include "*measurements-2014-06-18T08*" 
      --profile hadoop-seminar-emr
