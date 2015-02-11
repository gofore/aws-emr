

To copy objects from within S3:

    aws s3 cp 
      s3://hadoop-seminar-emr/digitraffic/imported/2014/06/18/ 
      s3://hadoop-seminar-emr/digitraffic/imported/subset-1hour/ 
      --recursive 
      --exclude "*" 
      --include "*measurements-2014-06-18T08*" 
      --profile hadoop-seminar-emr


# Case 1: Calculate average speeds from 2014-06

# Start a cluster
aws-tools/run-jobs.py create-cluster "Car speed counting cluster"
Starting cluster j-TVW9D7C54E10 Car speed counting cluster

# Add a job
aws-tools/run-jobs.py run-step j-TVW9D7C54E10 car-average-speeds.py digitraffic/munged/links-by-date/2014
Step will output data to s3://hadoop-seminar-emr/digitraffic/outputs/2015-02-11_18-15-43_car-average-speeds.py/

# Download and concatenate results
aws s3 cp s3://hadoop-seminar-emr/digitraffic/outputs/2015-02-11_18-15-43_car-average-speeds.py/ /tmp/emr --recursive --profile hadoop-seminar-emr
cat /tmp/emr/part-* > /tmp/emr/output

# Visualize results
python streaming-programs/car-average-speeds_output.py /tmp/emr/output example-data/locationdata.json

125 	Kehä III -> Tattarisuo
123 	Iittala -> Parolannummi
122 	Hevoskallio -> Veikkola
121 	Järvenpää -> Kehä III
121 	Korso -> Kehä III
121 	Linnatuuli -> Herajoki
120 	Hangelby -> Kulloo
