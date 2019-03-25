'''
Given a new mlst version or DB, update the container
'''

import pathlib
import click
import jinja2
import toml
import pendulum


def load_template(name):
    '''
    Return the singularity recipe template as unicode text
    '''
    template = pathlib.Path(name).read_text()
    return template


@click.command()
@click.option("--mlst_version", default=None)
@click.option("--use_github_db", is_flag=True)
@click.option("--author", default=None)
@click.option("-c", "--config", default="config.toml")
def update_mlst_singularity(mlst_version, use_github_db, author, config):
    '''
    Use the config.toml, or override any of the options via the command line
    '''
    # load the params
    config = toml.load(config)
    if mlst_version is not None:
        config['mlst_version'] = mlst_version
    if author is not None:
        config['author'] = author
    if use_github_db:
        config['update_db'] = False
    # load the template
    loader = jinja2.FunctionLoader(load_template)
    env = jinja2.Environment(loader=loader)
    SINGULARITY_RECIPE = env.get_template("_singularity.j2").render(config)
    # prepare the folders
    version_path = pathlib.Path(f'v{config["mlst_version"]}')
    if not version_path.exists():
        version_path.mkdir()
    today = pendulum.today().format('YYYYMMDD')
    subfolder_path = version_path / today
    if not subfolder_path.exists():
        subfolder_path.mkdir()
    # create local version
    local_recipe = subfolder_path / \
        f'Singularity.v{config["mlst_version"]}_{today}'
    local_recipe.write_text(SINGULARITY_RECIPE)
    # create global version
    global_recipe = pathlib.Path("SINGULARITY")
    global_recipe.write_text(SINGULARITY_RECIPE)


if __name__ == "__main__":
    update_mlst_singularity()
