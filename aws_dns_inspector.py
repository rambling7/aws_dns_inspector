from boto3 import client
from socket import gethostbyaddr, gethostbyname


class InspectorDNS():

    def __init__(self):
        try:
            client('route53').list_hosted_zones()
        except:
            print('Problem with AWS configure')
            raise SystemExit

    def get_zones(self):
        response = client('route53').list_hosted_zones()
        zones = response['HostedZones']
        my_domains = {}
        for zone in zones:
            ZoneName = zone['Name']
            ZoneId = zone['Id']
            my_domains[ZoneName] = {'Id': ZoneId}
        return my_domains

    # get all records by zone id
    # return dict of checked records
    def get_records(self, zone_id):
        response = client('route53').list_resource_record_sets(HostedZoneId=zone_id)
        records_set = response['ResourceRecordSets']
        my_records = {}
        for record in records_set:
            Name = record['Name']
            Type = record['Type']
            if Type == 'A' or Type == 'CNAME':
                checked_records = self._check_records(Type, record['ResourceRecords'])
                my_records[Type] = {'Name': Name, 'ResourceRecords': checked_records}
            else:
                my_records[Type] = {'Name': Name, 'ResourceRecords': record['ResourceRecords']}
        return my_records

    # check dict of record values,
    # return  dict of record values + status field
    def _check_records(self, Type, records):
        if Type == 'A':
            for record in records:
                try:
                    gethostbyaddr(record['Value'])
                    record['Status'] = 'in use'
                except:
                    record['Status'] = 'not use'

        elif Type == 'CNAME':
            for record in records:
                try:
                    gethostbyname(record['Value'])
                    record['Status'] = 'in use'
                except:
                    record['Status'] = 'not use'
        return records


if __name__ == "__main__":

    inspector = InspectorDNS()

    my_zones = inspector.get_zones()
    for zone in my_zones:
        print('******')
        print(('ZONE: {0}'.format(zone)))
        print('-RECORDS:')
        records = inspector.get_records(my_zones[zone]['Id'])
        for type_record in records:
            print(('--TYPE: {0}'.format(type_record)))
            for record in records[type_record]['ResourceRecords']:
                if 'Status' in record:
                    print(('---VALUE: {0} | STATUS: {1}'.format(record['Value'], record['Status'])))
                else:
                    print(('---VALUE: {0}'.format(record['Value'])))
