from wordpot.plugins_manager import BasePlugin
import re
import urllib2

wp_mobile_detect_resize = re.compile('resize|timthumb.php\?src', re.I)


class Plugin(BasePlugin):
    def run(self):
        full_url = urllib2.unquote(self.inputs['request'].url).decode('utf8')
        bad_url = re.search(r"\=(.*)", full_url)

        if bad_url:
            bad_url = bad_url.group(1)
            try:
                file_name = bad_url.split('/')[-1]
            except:
                return

        if wp_mobile_detect_resize.search(self.inputs['subpath']) is not None:
            # Message to log
            log = '%s possible file inclusion: %s' % (self.inputs['request'].remote_addr, bad_url)
            self.outputs['log'] = log

            # Render blank page (sucessful file inclusion will be blank)
            self.outputs['template'] = 'blank'

            # Download file
            try:
                f = urllib2.urlopen(bad_url)
                data = f.read()
                save_location = "../../badfiles/" + self.inputs['request'].remote_addr + file_name
                with open(save_location, "wb") as bad:
                    bad.write(data)

                # Add file to log
                log = 'Saved remote file to: %s' % (save_location)
                self.outputs['log'] = log

                # Add filename to badfiles/file_names.txt
                with open("../../badfiles/files.txt", "a") as done_file:
                    done_file.write(file_name + "\n")
                    done_file.close()
            except:
                pass

        # If a requested file from previously "uploaded" file inclusion
        #if self.inputs['subpath'].replace("/", "") in open('../../badfiles/files.txt').read():
        #    log = '%s requested file located in badfiles/files.txt: %s' % (self.inputs['subpath'].replace("/", ""))
        #    self.outputs['log'] = log

        return
