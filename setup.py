from setuptools import setup

setup(name='django_site_queue',
      version='1.1',
      description='Django Site Queue (Waiting Room)',
      url='https://github.com/xzzy/django_site_queue',
      author='Jason Moore',
      license='BSD',
      packages=['django_site_queue','django_site_queue.migrations'],
      install_requires=[],
      include_package_data=True,
      zip_safe=False)
