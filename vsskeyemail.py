from __future__ import print_function
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import base64
import argparse
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def get_email(capitao_time, categoria, time):
    corpo_email = f"""
    Olá, {capitao_time} da/de {time}!

    Este e-mail confirma o recebimento do seu pagamento via PIX para a Competição Brasileira de Futebol de Robôs Simulado na categoria {categoria}.

    Em anexo, você recebeu um arquivo .pem que deve ser utilizado para acessar a máquina na AWS utilizando o passo-a-passo abaixo. 

    Caso você tenha se inscrito em mais de uma categoria, você irá receber uma chave para cada categoria.

    Além disso, informamos que só será permitida a execução do seu código utilizando Docker para evitar conflito de dependências entre os times. 
    Caso você não tenha conhecimento chama um dos co-chairs no Discord e a gente vai te ajudar.

    Instruções para conexão com AWS:
    1- Primeiro tenha instalado o cliente SSH na sua máquina.
    \t 1.1- sudo apt-get update
    \t 1.2- sudo apt-get upgrade
    \t 1.3- sudo apt-get install openssh-client
    2- Baixe o arquivo .pem para a sua máquina
    3- Abra o terminal na pasta que o arquivo está
    4- Execute o comando "sudo chmod 400 seuArquivo.pem"
    5- Conecte usando "ssh -i "seuArquivo.pem" {time}@ec2-18-228-22-122.sa-east-1.compute.amazonaws.com"
    \t 5.1- Voce será requisitado a aceitar a adição da conexão. Responda com "sim" ou "yes".

    """
    return corpo_email

def create_message_with_attachment(
    sender, to, subject, message_text, file):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEMultipart()
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject

  msg = MIMEText(message_text)
  message.attach(msg)

  content_type, encoding = mimetypes.guess_type(file)

  if content_type is None or encoding is not None:
    content_type = 'application/octet-stream'
  main_type, sub_type = content_type.split('/', 1)
  if main_type == 'text':
    fp = open(file, 'rb')
    msg = MIMEText(fp.read(), _subtype=sub_type)
    fp.close()
  elif main_type == 'image':
    fp = open(file, 'rb')
    msg = MIMEImage(fp.read(), _subtype=sub_type)
    fp.close()
  elif main_type == 'audio':
    fp = open(file, 'rb')
    msg = MIMEAudio(fp.read(), _subtype=sub_type)
    fp.close()
  else:
    fp = open(file, 'rb')
    msg = MIMEBase(main_type, sub_type)
    msg.set_payload(fp.read())
    fp.close()
  filename = os.path.basename(file)
  msg.add_header('Content-Disposition', 'attachment', filename=filename)
  message.attach(msg)
  b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
  b64_string = b64_bytes.decode()
  body = {'raw': b64_string}
  return body

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    menID = message['id']           
    print (f'Message Id: {menID}')
    return message
  except HttpError as error:
    print (f'An error occurred: {error}')

def main(args):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        """
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
        for label in labels:
            print(label['name'])
        
        """
        service = build('gmail', 'v1', credentials=creds)
        sender = "pjls2@cin.ufpe.br"
        to = args.email
        message_email = get_email(args.capitao, args.categoria, args.time)
        subject = "Confirmação de inscrição no Campeonato Brasileiro de Futebol de Robôs Simulado"
        file = "./"+args.time+args.categoria+".pem"
        final_email = create_message_with_attachment(sender, to, subject, message_email, file)
        user_id = 'me'
        send_message(service, user_id , final_email)
        

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    

    parser = argparse.ArgumentParser(description='envia as chaves pem para os times do VSS')
    parser.add_argument('--email', help='Email do capitão do time')
    parser.add_argument('--categoria', help='categoria do time')
    parser.add_argument('--capitao', help='primeiro nome do capitao')
    parser.add_argument('--time', help='nome do time')

    args = parser.parse_args()
    main(args)
