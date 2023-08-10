from setuptools import setup, find_packages

setup(
    name='stata_py',
    version='0.1.0',
    author='Tu Nombre',
    author_email='dmenares@fen.uchile.cl',
    description='stata for python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/dmenares93/stata_py',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # Asegúrate de que esta licencia coincida con la tuya
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=[
        'numpy',
        'pandas',
    ],
    python_requires='>=3.11',
)




