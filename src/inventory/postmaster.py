from base64 import b64encode
import boto3, urllib.parse

# Email details
RECIPIENTS = ['jdoe@example.com']
FROM = 'FedRAMP Inventory Postmaster <do-not-reply@example.com>'

def mail_that_bit(report, key):
    """
    Use AWS SES to email the received inventory report.
    """ 
    # Send raw email
    ses = boto3.client('ses')
    response = ses.send_raw_email(
        Source=FROM,
        Destinations=RECIPIENTS,
        RawMessage={
            'Data': 'From: %s\nSubject: Inventory Report\nMIME-Version: 1.0\nContent-type: Multipart/Mixed; boundary="NextPart"\n\n--NextPart\nContent-Type: text/plain\n\nInventory report attached.\n\n--NextPart\nContent-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\nContent-Transfer-Encoding: base64\nContent-Disposition: attachment; filename="%s"' % (FROM, key) + '\n\n%s' % report
        }
    )
    print(response)

def lambda_handler(event, context):
    """
    AWS Lambda handler, entrypoint.
    """
    # Get the object details from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket, Key=key)
        # Read report and base64 encode 
        report = b64encode(response['Body'].read()).decode('ascii')
        print('Got Object')
        # Try to email with SES
        print('Trying to email...')
        mail_that_bit(report, key)
        print('Done')
    except Exception as error:
        print(error)
        raise error
