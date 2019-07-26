from setuptools import setup


setup(
    name='hiltnlp',
    version='0.1',
    description='NLP tools for use with HiLT-style GATE annotation documents',
    url='http://github.com/nickwbarber/hiltnlp',
    author='Nick Barber',
    author_email='nickwbarber@gmail.com',
    license='MIT',
    packages=['hiltnlp'],
    install_requires=[
        'gatenlp-hiltlab',
    ],
    zip_safe=False
)
