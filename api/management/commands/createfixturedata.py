from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files.base import File as DjangoFile

import traceback
import urllib2
import json
import random
import os

# Custom User Model
from django.contrib.auth import get_user_model

# User Helper Models
from api.models import Organization, University

# User Profile Models
from api.models import Nationals, Administrator, Host

# Email Helper Models
from api.models import CarbonCopyAddress

# Identity Models
from api.models import Identity, Flag

# Event Models
from api.models import Event, Procedure, Invitee

# Guest Registration Model
from api.models import GuestRegistration


class Command(BaseCommand):
    """
    Create a large set of fixture data for visual testing.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force DB Wipe',
        )

    def handle(self, *args, **kwargs):
        """
        Prompt the user, asking if he/she would truly like to delete all
        objects.
        """
        if not kwargs.get('force'):
            print 'Are you sure you would like to recreate your entire database?'
            print 'Enter `DELETE` to delete database and load with fixture data: '
            choice = raw_input()
            if choice != 'DELETE':
                print 'Your actions have resulted in zero change to the database.'
                return

        """
        Generate `CarbonCopyAddress` information.
        """
        CarbonCopyAddress.objects.all().delete()
        email_list = ['bobjones@bobjones.com ', 'jimbob@jimbob.com  ', 'joey@joey.com',
                      'sarahmarshall@sarahmarshall.com', 'josh@josh.com', 'john@john.com']

        """
        Generate user information.
        """
        # Delete pre-existing objects
        get_user_model().objects.all().exclude(is_superuser=True).delete()

        # Get email `json` data
        response = urllib2.urlopen('http://www.json-generator.com/api/json/get/cjAElSKJTS?indent=2')
        json_user_list = json.loads(response.read())
        user_list = []
        

        for user in json_user_list:
            password = ''.join(user['name'].split(' ')).lower()
            user_list.append({'email': user['email'], 'password': password})

        """
        Generate `Organization` and `Nationals` objects.
        """
        # Delete pre-existing objects
        Organization.objects.all().delete()
        Nationals.objects.all().delete()

        name_list = ['Kappa Sigma', 'Sigma Alpha Epsilon', 'Sigma Nu', 'Kappa Delta']

        for name in name_list:
            org = Organization.objects.create(name=name)
            json_user = user_list.pop()
            user = get_user_model().objects.create_user(username=json_user['email'].split('@')[0],
                                                        password=json_user['password'],
                                                        email=json_user['email'])
            Nationals.objects.create(user=user, organization=org, enabled=True)
            for i in range(0, random.randint(0, 5)):
                try:
                    CarbonCopyAddress.objects.create(email=email_list[i], user=user)
                except:
                    pass

        print 'Completed objects...'
        print '\t1. Organization'
        print '\t2. Nationals'

        """
        Generate `University` and `Administrator` objects.
        """
        # Delete pre-existing objects
        Administrator.objects.all().delete()
        University.objects.all().delete()

        university_list = [{'name': 'Southern Polytechnic State University',
                            'acronym': 'SPSU',
                            'state': 'Georgia',
                            'longitude': '33.9400',
                            'latitude': '84.5200'},
                           {'name': 'Kennesaw State University',
                            'acronym': 'KSU',
                            'state': 'Georgia',
                            'longitude': '34.0379',
                            'latitude': '84.5810'},
                           {'name': 'University of Georgia',
                            'acronym': 'UGA',
                            'state': 'Georgia',
                            'longitude': '33.9558',
                            'latitude': '83.3475'},
                           {'name': 'Georgia State University',
                            'acronym': 'GSU',
                            'state': 'Georgia',
                            'longitude': '33.7528',
                            'latitude': '84.3861'}]

        for university in university_list:
            univ = University.objects.create(name=university['name'], acronym=university['acronym'],
                                             state=university['state'],
                                             longitude=university['longitude'],
                                             latitude=university['latitude'])
            json_user = user_list.pop()
            user = get_user_model().objects.create_user(username=json_user['email'].split('@')[0],
                                                        password=json_user['password'],
                                                        email=json_user['email'])
            Administrator.objects.create(user=user, university=univ, enabled=True)
            for i in range(0, random.randint(0, 5)):
                try:
                    CarbonCopyAddress.objects.create(email=email_list[i], user=user)
                except:
                    pass

        print '\t3. University'
        print '\t4. Administrator'

        """
        Generate `Host` objects.
        """
        # Delete pre-existing objects
        Host.objects.all().delete() 

        nationals = Nationals.objects.all()
        administrators = Administrator.objects.all()

        for national in nationals:
            for administrator in administrators:
                json_user = user_list.pop()
                user = get_user_model().objects.create_user(username=json_user['email'].split('@')[0],
                                                            password=json_user['password'],
                                                            email=json_user['email'])
                Host.objects.create(user=user, university=administrator.university,
                                    organization=national.organization,
                                    administrator=administrator,
                                    nationals=national,
                                    enabled=True)

                for i in range(0, random.randint(0, 5)):
                    try:
                        CarbonCopyAddress.objects.create(email=email_list[i], user=user)
                    except:
                        pass

        print '\t6. Host'
        print '\t7. CarbonCopyAddress'

        """
        Generate `Event` objects.
        """
        # Delete pre-existing objects
        Event.objects.all().delete()

        hosts = Host.objects.all()

        data = {
            'name': 'New Event',
            'description': 'My event.',
            'date': '2014-07-21',
            'time': '00:00:00.000000',
            'location': 'Chapter House',
            'planner_name': 'Joshua Taylor Eppinette',
            'planner_mobile': '7704016678',
            'planner_email': 'josh.eppinette@riskmanaged.net',
            'president_email': 'pres@pres.com',
            'sober_monitors': 'Josh Eppinette',
            'expected_guest_count': 50,
            'exclusivity': 'Invitation Only',
            'alcohol_distribution': 'Mobile Cocktails',
            'entry': 'Yes',
            'entry_description': 'Front Door',
            'co_sponsored_description': 'With Kappa Delta'
        }

        event_names = [
            'Christmas Party', 'New Years Party', 'Thrift Shop Party',
            'Rush Party', 'Formal', 'Semi-Formal', 'End of the Year Party',
            'Random Party', 'Rush Event', 'Shoot the Hooch', 'Greek Social',
            'Tommy Bahama Party', 'Beach Party', 'Black Light Party', '80"s Party',
            '90"s Party', 'Construction Party', 'Cowboys and Indians Party',
            'ABC Party', 'Halloween Party', 'Toga Party', 'Easter Party',
            'No Mo SoPro Party', 'GI Joe and Jane Party', 'Red Neck Party', 'Nerd Party',
            'Date Night', 'Braves Night'
        ]
            

        for host in hosts:
            data['name'] = random.choice(event_names)
            Event.objects.create(host=host, **data)

        print '\t8. Event'

        """
        Generate `Procedure` objects.
        """
        # Delete pre-existing objects
        Procedure.objects.all().delete()

        events = Event.objects.all()

        for event in events:
            Procedure.objects.create(event=event, description='Interior Sweep')
            Procedure.objects.create(event=event, description='Exterior Sweep')

        print '\t9. Procedure'

        """
        Generate `Invitee` objects.
        """
        # Delete pre-existing objects
        Invitee.objects.all().delete()

        events = Event.objects.all()

        # Get `json` data
        response = urllib2.urlopen('http://www.json-generator.com/api/json/get/bVIMfRScya?indent=2')
        json_invitee_list = json.loads(response.read())
        
        for event in events:
            for i in range(50):
                invitee_data = json_invitee_list.pop()
                Invitee.objects.create(event=event,
                                       first_name=invitee_data['first_name'],
                                       last_name=invitee_data['last_name'],
                                       gender=invitee_data['gender'].capitalize())
               
        print '\t10. Invitee'

        """
        Generate `Identity` objects.
        """
        # Delete pre-existing objects
        Identity.objects.all().delete()

        # Get `json` data
        response = urllib2.urlopen('http://www.json-generator.com/api/json/get/cjLssdDLDm?indent=2')
        json_identity_list = json.loads(response.read())
        
        for i in range(300):
            identity_data = json_identity_list.pop()
            Identity.objects.create(first_name=identity_data['first_name'],
                                    last_name=identity_data['last_name'],
                                    gender=identity_data['gender'].capitalize(),
                                    dob=identity_data['dob'])
               
        print '\t11. Identity'

        """
        Generate `Flag` objects.
        """
        # Delete pre-existing objects
        Flag.objects.all().delete()

        identities = Identity.objects.all()
        nationals = Nationals.objects.all()
        administrators = Administrator.objects.all()
        hosts = Host.objects.all()

        # Create `Nationals` flags
        for i in range(10):
            national = random.choice(nationals)
            identity = random.choice(identities)
            Flag.objects.create(identity=identity,
                                nationals=national,
                                reach='Nationals',
                                violation=random.choice(Flag.VIOLATIONS)[0])

        for i in range(10):
            administrator = random.choice(administrators)
            identity = random.choice(identities)
            Flag.objects.create(identity=identity,
                                administrator=administrator,
                                reach='Administrator',
                                violation=random.choice(Flag.VIOLATIONS)[0])

        for i in range(10):
            host = random.choice(hosts)
            identity = random.choice(identities)
            Flag.objects.create(identity=identity,
                                host=host,
                                reach='Host',
                                violation=random.choice(Flag.VIOLATIONS)[0])

        print '\t12. Flag'

        """
        Generate `GuestRegistration` objects.
        """
        # Delete pre-existing objects
        GuestRegistration.objects.all().delete()

        identities = Identity.objects.all()
        events = Event.objects.all()

        from django.core.files.uploadedfile import SimpleUploadedFile

        for i in range(500):
            event = random.choice(events)
            identity = random.choice(identities)
            try:
                with open(os.path.join(settings.ROOT, 'static', 'tests', 'test_image.jpg'), 'rb') as f:
                    name = os.path.join('images', 'guests', str(identity.id) + '-' + str(event.id) + '-image.jpg')
                    GuestRegistration.objects.create(identity=identity,
                                                     event=event,
                                                     image=SimpleUploadedFile(name, f.read()))
                    print str(i) + '. %s at %s.' % (str(identity), str(event))
            except Exception, e:
                print str(e)
                print str(traceback.format_exc())

        print '\t13. GuestRegistration'
