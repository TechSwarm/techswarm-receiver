import subprocess
from PIL import Image


PARAMS = {
    'pto_gen': (),
    'cpfind': ('--multirow',
               '--celeste'  # Ignore clouds
               ),
    'cpclean': (),
    'linefind': (),
    'autooptimiser': ('-a',  # Auto align
                      '-m',  # Optimize photometric parameters
                      '-l',  # Level horizon
                      '-s'  # Select output projection and size automatically
                      ),
    'pano_modify': ('--canvas=AUTO', '--crop=AUTO'),
    'nona': ('-m', 'TIFF')
}

JPEG_OPTIONS = {
    'quality': 80,
}


def __call_hugin(cmd, project_url, *params, add_project_param=True):
    """
    Call the specified Hugin-related command

    The parameters, besides the ones passed as params argument, are taken from
    PARAMS dictionary. Additionally, if add_project_param is True, then
    a parameter with project URL is added at the end as well.

    Function throws exception if the process returned non-zero exit code.

    :param cmd: command to call
    :type cmd: str
    :param project_url: URL of the project
    :type project_url: str
    :param params: parameters to pass to the command
    :type params: tuple
    :param add_project_param: True if project URL should be appended to the
        parameters (default behavior); False otherwise
    :type add_project_param: bool
    """
    params = [cmd, '-o', project_url] + list(PARAMS[cmd]) + list(params)
    if add_project_param:
        params += [project_url]
    subprocess.check_call(params, stderr=subprocess.STDOUT)


def __pano_to_jpeg(input_url, output_url):
    """
    Open the specified file (TIFF, usually), crop it and save in given location
    with options specified in JPEG_OPTIONS.

    :param input_url: URL of source image
    :type input_url: str
    :param output_url: URL of destination file
    :type output_url: str
    """
    image = Image.open(input_url)
    image.load()
    image_box = image.getbbox()
    cropped = image.crop(image_box)
    cropped.save(output_url, **JPEG_OPTIONS)


def stitch_panorama(output_url, project_url, *input_urls):
    """
    Stitch the panorama automatically out of the images specified in input_urls.

    Basically the function just calls a bunch of commands taken mainly from
    http://wiki.panotools.org/Panorama_scripting_in_a_nutshell. Parameters
    to these CLI programs are taken from PARAMS dictionary, whereas options
    used when saving JPEG file are stored in JPEG_OPTIONS.

    :param output_url: the URL to save the file in. It should not contain
        extension, since the function causes two files to be created:
        `output_url + '.tif'` and `output_url + '.jpg'`.
    :type output_url: str
    :param project_url: the URL to store Hugin project in
    :type project_url: str
    :param input_urls: URLs of input images
    :type input_urls: str
    """
    # Create project
    __call_hugin('pto_gen', project_url, *input_urls,
                 add_project_param=False)  # 5%

    # Find checkpoints
    __call_hugin('cpfind', project_url)  # 35%
    # Clean checkpoints
    __call_hugin('cpclean', project_url)  # 45%
    # Find vertical lines
    __call_hugin('linefind', project_url)  # 55%

    # Optimize
    __call_hugin('autooptimiser', project_url)  # 65%
    # Crop
    __call_hugin('pano_modify', project_url)  # 70%

    # Render
    __call_hugin('nona', output_url + '.tif', project_url,
                 add_project_param=False)  # 95%
    # Crop and convert to JPEG
    __pano_to_jpeg(output_url + '.tif', output_url + '.jpg')  # 100%

