from setuptools import setup, find_packages

setup(
    name='mainevent_client',
    version='0.1',
    license='MIT',
    url='https://github.com/mypackage.git',
    author='Liam Earley',
    author_email='liamearley7@gmail.com',
    description='Mainevent SSE Server Python Client',
    packages=find_packages(),    
    install_requires=['wheel', 'aiohttp', 'aiosseclient', 'aiostream'],
)