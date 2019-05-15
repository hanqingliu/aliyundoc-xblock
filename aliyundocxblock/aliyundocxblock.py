"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from django.template import Context, Template
from django.conf import settings
from django.utils import translation
from xblock.core import XBlock
from xblock.fields import Scope, String, Boolean
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
import logging
import oss2

def _(text):
    return text

class AliyunDocXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    '''
    Icon of the XBlock. Values : [other (default), video, problem]
    '''
    icon_class = "other"

    '''
    Fields
    '''
    display_name = String(
        display_name=_("Display Name"),
        default="Document",
        scope=Scope.settings,
        help="This name appears in the horizontal navigation at the top of the page."
    )

    url = String(
        display_name=_("Document URL"),
        default="http://tutorial.math.lamar.edu/pdf/Trig_Cheat_Sheet.pdf",
        scope=Scope.content,
        help="The URL for your Document."
    )

    allow_download = Boolean(
        display_name=_("Document Download Allowed"),
        default=True,
        scope=Scope.content,
        help="Display a download button for this Document."
    )

    source_text = String(
        display_name=_("Source document button text"),
        default="",
        scope=Scope.content,
        help="Add a download link for the source file of your Document. "
             "Use it for example to provide the PowerPoint file used to create this PDF."
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, template_path, context={}):
        """
        Evaluate a template by resource path, applying the provided context
        """
        template_str = self.resource_string(template_path)
        return Template(template_str).render(Context(context))

    def get_aliyun_doc_url(self, object_id):
        """
        Get preview and download url from aliyun
        """
        access_key_id = getattr(settings, 'ALIYUN_ACCESS_KEY_ID', 'default_key')
        access_key_secret = getattr(settings, 'ALIYUN_ACCESS_KEY_SECRET', 'default_secret')
        endpoint = getattr(settings, 'ALIYUN_OSS_ENDPOINT', 'https://oss_endpoint')
        bucket_name = getattr(settings, 'ALIYUN_OSS_BUCKET', 'default_bucket')
        bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
        process = 'imm/previewdoc,copy_1'
        params = {}
        params.update({bucket.PROCESS: process})
        preview_url = bucket.sign_url("GET", object_id, 3600, params=params)
        download_url = bucket.sign_url('GET', object_id, 3600)
        return preview_url, download_url

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the AliyunDocXBlock, shown to students
        when viewing courses.
        """
        preview_url, download_url = self.get_aliyun_doc_url(self.url)
        context = {
            'display_name': self.display_name,
            'url': preview_url,
            'allow_download': self.allow_download,
            'source_text': self.source_text,
            'source_url': download_url
        }
        html = self.render_template("templates/html/aliyundocxblock.html", context)
        frag = Fragment(html)
        frag.add_css(self.resource_string("static/css/aliyundocxblock.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(self.runtime.local_resource_url(self, statici18n_js_url))

        frag.add_javascript(self.resource_string("static/js/src/aliyundocxblock.js"))
        frag.initialize_js('AliyunDocXBlock')
        return frag

    def studio_view(self, context=None):
        """
        The secondary view of the XBlock, shown to teachers
        when editing the XBlock.
        """
        context = {
            'display_name': self.display_name,
            'url': self.url,
            'allow_download': self.allow_download,
            'source_text': self.source_text,
        }
        html = self.render_template('templates/html/doc_edit.html', context)
        frag = Fragment(html)
        frag.add_javascript(self.resource_string("static/js/src/doc_edit.js"))
        frag.initialize_js('docXBlockInitEdit')
        return frag

    @XBlock.json_handler
    def on_download(self, data, suffix=''):
        """
        The download file event handler
        """
        event_type = 'edx.doc.downloaded'
        event_data = {
            'url': self.url,
        }
        self.runtime.publish(self, event_type, event_data)

    @XBlock.json_handler
    def save_doc(self, data, suffix=''):
        """
        The saving handler.
        """
        self.display_name = data['display_name']
        self.url = data['url']
        self.allow_download = True if data['allow_download'] == "True" else False  # Str to Bool translation
        self.source_text = data['source_text']

        return {
            'result': 'success',
        }

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("AliyunDocXBlock",
             """<aliyundocxblock/>
             """),
            ("Multiple AliyunDocXBlock",
             """<vertical_demo>
                <aliyundocxblock/>
                <aliyundocxblock/>
                <aliyundocxblock/>
                </vertical_demo>
             """),
        ]

    @staticmethod
    def _get_statici18n_js_url():
        """
        Returns the Javascript translation file for the currently selected language, if any.
        Defaults to English if available.
        """
        locale_code = translation.get_language()
        if locale_code is None:
            return None
        text_js = 'public/js/translations/{locale_code}/text.js'
        lang_code = locale_code.split('-')[0]
        for code in (locale_code, lang_code, 'en'):
            loader = ResourceLoader(__name__)
            if pkg_resources.resource_exists(
                    loader.module_name, text_js.format(locale_code=code)):
                return text_js.format(locale_code=code)
        return None

    @staticmethod
    def get_dummy():
        """
        Dummy method to generate initial i18n
        """
        return translation.gettext_noop('Dummy')
