from wordpot.plugins_manager import BasePlugin
import re
import urllib2

phpmyadmin_index = re.compile('index.php', re.I)
phpmyadmin_setup = re.compile('setup.php', re.I)
phpmyadmin_config = re.compile('config.inc.php', re.I)


class Plugin(BasePlugin):
    def run(self):

        # Initialize template vars dict
        self.outputs['template_vars'] = {}

        origin = self.inputs['request'].remote_addr

        # Capture setup.php exploit
        if phpmyadmin_setup.search(self.inputs['subpath']) is not None:
            log = '%s probed for phpmyadmin setup.php: %s' % (self.inputs['request'].remote_addr, self.inputs['subpath'])
            self.outputs['log'] = log
            self.outputs['log_json'] = self.to_json_log(filename=self.inputs['subpath'], plugin='phpmyadmin')

            # WHY CAN'T I GET COOKIE?
            #self.outputs['template_vars']['COOKIE'] = self.inputs['request'].cookies

            # Return setup.php
            self.outputs['template'] = 'phpsetup.html'

            # Check for post
            # TODO: Add exploit check?
            if self.inputs['request'].method == 'POST':
                request = self.inputs['request']
                self.outputs['log'] = 'setup.php request: %s' % request

        elif phpmyadmin_config.search(self.inputs['subpath']) is not None:
            # Get full url
            full_url = urllib2.unquote(self.inputs['request'].url).decode('utf8')
            # Pull out everything after = sign (usually command like whoami)
            php_commands = re.search(r"\=(.*)", full_url)

            log = '%s probed for config.inc.php: %s' % (self.inputs['request'].remote_addr, self.inputs['subpath'])
            self.outputs['log'] = log
            self.outputs['log_json'] = self.to_json_log(filename=self.inputs['subpath'], plugin='phpmyadmin')

            if self.inputs['request'].method == 'POST':
                request = self.inputs['request']
                self.outputs['log'] = 'setup.php request: %s' % request
            elif php_commands is not None:
                log = '%s possible command injection for config.inc.php: %s' % (self.inputs['request'].remote_addr, php_commands)
                self.outputs['log'] = log
                self.outputs['log_json'] = self.to_json_log(filename=self.inputs['subpath'], plugin='phpmyadmin')

            self.outputs['template'] = 'blank'

        # Capture login attempts
        elif phpmyadmin_index.search(self.inputs['subpath']) is not None:
            if self.inputs['request'].method == 'POST':
                username = self.inputs['request'].form['username']
                password = self.inputs['request'].form['password']
                self.outputs['log'] = '%s tried to login to phpmyadmin with login/password: %s:%s' % (origin, username, password)
                self.outputs['log_json'] = self.to_json_log(username=username, password=password, plugin='phpmyadmin')
                self.outputs['template_vars']['BADLOGIN'] = True
                self.outputs['template'] = 'phpmyadmin.html'
            else:
                self.outputs['log'] = '%s probed for the login page' % origin
                self.outputs['template_vars']['BADLOGIN'] = False
                self.outputs['template'] = 'phpmyadmin.html'

        return
