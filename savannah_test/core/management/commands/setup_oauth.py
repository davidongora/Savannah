"""
Management command to set up OAuth2/OIDC application
"""
from django.core.management.base import BaseCommand, CommandError
from oauth2_provider.models import Application
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Set up OAuth2/OIDC application for API access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='Savannah API Client',
            help='Name for the OAuth2 application'
        )
        parser.add_argument(
            '--client-type',
            type=str,
            choices=['confidential', 'public'],
            default='confidential',
            help='Client type for the OAuth2 application'
        )
        parser.add_argument(
            '--grant-type',
            type=str,
            choices=['authorization-code', 'client-credentials'],
            default='authorization-code',
            help='Grant type for the OAuth2 application'
        )

    def handle(self, *args, **options):
        name = options['name']
        client_type = options['client_type']
        grant_type = options['grant_type']

        # Map grant type to the expected value
        grant_type_mapping = {
            'authorization-code': Application.GRANT_AUTHORIZATION_CODE,
            'client-credentials': Application.GRANT_CLIENT_CREDENTIALS,
        }

        # Map client type to the expected value
        client_type_mapping = {
            'confidential': Application.CLIENT_CONFIDENTIAL,
            'public': Application.CLIENT_PUBLIC,
        }

        try:
            # Check if application already exists
            existing_app = Application.objects.filter(name=name).first()
            if existing_app:
                self.stdout.write(
                    self.style.WARNING(f'Application "{name}" already exists')
                )
                self.stdout.write(f'Client ID: {existing_app.client_id}')
                self.stdout.write(f'Client Secret: {existing_app.client_secret}')
                return

            # Create the application
            application = Application.objects.create(
                name=name,
                client_type=client_type_mapping[client_type],
                authorization_grant_type=grant_type_mapping[grant_type],
            )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created OAuth2 application "{name}"')
            )
            self.stdout.write(f'Client ID: {application.client_id}')
            if client_type == 'confidential':
                self.stdout.write(f'Client Secret: {application.client_secret}')
            
            self.stdout.write('\nOAuth2 Endpoints:')
            self.stdout.write('Authorization: http://localhost:8000/o/authorize/')
            self.stdout.write('Token: http://localhost:8000/o/token/')
            self.stdout.write('Userinfo: http://localhost:8000/o/userinfo/')
            self.stdout.write('JWKS: http://localhost:8000/o/.well-known/jwks.json')
            
            self.stdout.write('\nEnvironment Variables:')
            self.stdout.write(f'OIDC_RP_CLIENT_ID={application.client_id}')
            if client_type == 'confidential':
                self.stdout.write(f'OIDC_RP_CLIENT_SECRET={application.client_secret}')

        except Exception as e:
            raise CommandError(f'Error creating OAuth2 application: {e}')