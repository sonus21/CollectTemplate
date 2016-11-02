from __future__ import unicode_literals
from future.builtins import int
from future.builtins import input
from importlib import import_module
import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', action='store_false', dest='interactive',
            help="Do NOT prompt for input of any kind. "
                 "Existing templates will be overwritten.")
        parser.add_argument(
            '-t', '--template', dest='template',
            help="The template name and relative path of a single template "
                 "to copy, eg: home/homeBase.html")
        parser.add_argument(
            '-a', '--admin', action='store_true', dest='admin',
            help="Include admin templates.")

        parser.add_argument(
            'args', metavar='appName', nargs='*',
            help='Restricts collect templates to the specified app name')

        parser.add_argument(
            '-e', '--exclude', dest="AppName", nargs="+",
            help="Exclude one or more apps")

    def get_app_path(self, apps):
        found_apps = []
        not_found_apps = []
        apps_wmtoe = []
        for app in set(apps):
            if app not in settings.INSTALLED_APPS:
                target_apps = []
                for iApp in settings.INSTALLED_APPS:
                    if iApp.rfind(app) != -1:
                        target_apps.append(iApp)
                if len(target_apps) > 1:
                    apps_wmtoe.append(app)
                elif len(target_apps) == 0:
                    not_found_apps.append(app)
                else:
                    found_apps.extend(target_apps)
            else:
                found_apps.append(app)

        return found_apps, not_found_apps, apps_wmtoe

    def handle(self, *apps, **options):
        exclude_apps = options.get('AppName', [])
        if exclude_apps is None:
            exclude_apps = []

        if apps and exclude_apps:
            raise CommandError("--exclude and command arguments are mutual exclusive")

        installed, not_installed, installed_wmoe = self.get_app_path(apps)
        if installed_wmoe:
            raise CommandError("Apps %s have more than one entry in INSTALLED_APPS\n"
                               "HINT: Specify complete app name including dot\n"
                               "eg:  django.contrib.auth" %
                               ", ".join(installed_wmoe))
        if not_installed:
            raise CommandError("Apps are not in INSTALLED_APPS: " +
                               ", ".join(not_installed))

        exclude_installed, not_installed, installed_wmoe = self.get_app_path(exclude_apps)
        if installed_wmoe:
            raise CommandError("Apps %s have more than one entry in INSTALLED_APPS\n"
                               "HINT: Specify complete app name including dot eg: django.contrib.auth" %
                               ", ".join(installed_wmoe))
        if not_installed:
            raise CommandError("Apps are not in INSTALLED_APPS: " +
                               ", ".join(not_installed))
        if not apps:
            apps = set(settings.INSTALLED_APPS) - set(exclude_apps)

        admin = options.get("admin")
        single_template = options.get("template")
        verbosity = int(options.get('verbosity', 1))
        destination_dir = settings.TEMPLATES[0]["DIRS"][0]
        templates = []
        # Build a list of name/path pairs of all templates to copy.
        for app in apps:
            source_dir = os.path.join(
                os.path.dirname(
                    os.path.abspath(import_module(app).__file__)),
                "templates")
            if os.path.exists(source_dir):
                for (dirpath, dirnames, filenames) in os.walk(source_dir):
                    for f in filenames:
                        path = os.path.join(dirpath, f)
                        name = path[len(source_dir) + 1:]
                        if not (single_template and name != single_template) or \
                                (not admin and name.startswith("admin" + os.sep)):
                            templates.append((name, path, app))

        # Copy templates.
        count = 0
        template_src = {}
        interactive = options.get("interactive")
        for name, path, app in templates:
            dest = os.path.join(destination_dir, name)
            # Prompt user to overwrite template if interactive and
            # template exists.
            if verbosity >= 2:
                self.stdout.write("\nCopying: %s"
                                  "\nFrom:    %s"
                                  "\nTo:      %s"
                                  "\n" % (name, path, dest))
            copy = True
            if interactive and os.path.exists(dest):
                if name in template_src:
                    prev = ' [copied from %s]' % template_src[name]
                else:
                    prev = ''
                self.stdout.write("While copying %s [from %s]:\n" %
                                  (name, app))
                self.stdout.write("Template exists%s.\n" % prev)
                confirm = input("Overwrite?  (yes/no/abort): ").lower()
                while confirm not in ("yes", "y", "no", "n", "abort"):
                    confirm = input(
                        'Please enter one of "yes", "y", "no", "n", "abort": ')
                if confirm == "abort":
                    self.stdout.write("Aborted\n")
                    break  # exit templates copying loop
                elif confirm in ["no", "n"]:
                    self.stdout.write("[Skipped]\n")
                    copy = False
            if copy:
                try:
                    os.makedirs(os.path.dirname(dest))
                except OSError:
                    pass
                shutil.copy2(path, dest)
                template_src[name] = app
                count += 1
        if verbosity >= 1:
            s = "s" if count != 1 else ""
            self.stdout.write("\nCopied %s template%s\n" % (count, s))
