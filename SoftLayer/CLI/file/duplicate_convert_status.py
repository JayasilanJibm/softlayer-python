"""Get status for split or move completed percentage of a given file duplicate volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand,
               epilog="""Get status for split or move completed percentage of a given file duplicate volume.""")
@click.argument('volume-id')
@environment.pass_env
def cli(env, volume_id):
    """Get status for split or move completed percentage of a given file duplicate volume."""
    table = formatting.Table(['username', 'active_conversion_start_time', 'completed_percentage'])

    file_manager = SoftLayer.FileStorageManager(env.client)

    value = file_manager.split_percentage(
        volume_id
    )

    table.add_row(
        [
            value['volumeUsername'],
            value['activeConversionStartTime'],
            value['deDuplicateConversionPercentage']
        ]
    )

    env.fout(table)
