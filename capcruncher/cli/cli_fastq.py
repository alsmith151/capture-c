from os import name
import click
from capcruncher.cli import UnsortedGroup

@click.group()
def cli():
    """Contains methods for fastq splitting, deduplicating and digestion."""


@cli.command()
@click.argument("input_files", nargs=-1, required=True)
@click.option(
    "-m",
    "--method",
    help="Method to use for splitting",
    type=click.Choice(["python", "unix"]),
    default="unix",
)
@click.option(
    "-o",
    "--output_prefix",
    help="Output prefix for deduplicated fastq file(s)",
    default="split",
)
@click.option(
    "--compression_level",
    help="Level of compression for output files",
    default=5,
    type=click.INT,
)
@click.option(
    "-n",
    "--n_reads",
    help="Number of reads per fastq file",
    default=1e6,
    type=click.INT,
)
@click.option(
    "--gzip/--no-gzip", help="Determines if files are gziped or not", default=False
)
def split(*args, **kwargs):
    """
    Splits fastq file(s) into equal chunks of n reads.

    """

    from capcruncher.cli.fastq_split import split
    split(*args, **kwargs)

@cli.command()
@click.argument("input_fastq", nargs=-1, required=True)
@click.option("-r", "--restriction_enzyme", help="Restriction enzyme name or sequence to use for in silico digestion.", required=True)
@click.option(
    "-m",
    "--mode",
    help="Digestion mode. Combined (Flashed) or non-combined (PE) read pairs.",
    type=click.Choice(["flashed", "pe"], case_sensitive=False),
    required=True,
)
@click.option("-o", "--output_file", default="out.fastq.gz")
@click.option("-p", "--n_cores", default=1, type=click.INT)
@click.option("--minimum_slice_length", default=18, type=click.INT)
@click.option("--keep_cutsite", default=False)
@click.option(
    "--compression_level",
    help="Level of compression for output files (1=low, 9=high)",
    default=5,
    type=click.INT,
)
@click.option(
    "--read_buffer",
    help="Number of reads to process before writing to file to conserve memory.",
    default=1e5,
    type=click.INT,
)
@click.option("--stats_prefix", help="Output prefix for stats file", default="stats")
@click.option(
    "--sample_name", help="Name of sample e.g. DOX_treated_1. Required for correct statistics.", default="sampleX"
)
def digest(*args, **kwargs):
    """
    Performs in silico digestion of one or a pair of fastq files.
    """
    from capcruncher.cli.fastq_digest import digest
    digest(*args, **kwargs)


@cli.group(cls=UnsortedGroup)
def deduplicate():
    """
    Identifies PCR duplicate fragments from Fastq files.

    PCR duplicates are very commonly present in Capture-C/Tri-C/Tiled-C data and must be removed
    for accurate analysis. These commands attempt to identify and remove duplicate reads/fragments
    from fastq file(s) to speed up downstream analysis.

    """

@deduplicate.command(name='parse')
@click.argument("input_files", nargs=-1, required=True)
@click.option(
    "-o",
    "--output",
    help="File to store hashed sequence identifiers",
    default="out.json",
)
@click.option(
    "--read_buffer",
    help="Number of reads to process before writing to file",
    default=1e5,
    type=click.INT,
)
def deduplicate_parse(*args, **kwargs):

    """
    Parses fastq file(s) into easy to deduplicate format.

    This command parses one or more fastq files and generates a dictionary containing
    hashed read identifiers together with hashed concatenated sequences. The hash dictionary
    is output in json format and the identify subcommand can be used to determine which read identifiers 
    have duplicate sequences.
    """

    from capcruncher.cli.fastq_deduplicate import parse
    parse(*args, **kwargs)


@deduplicate.command(name='identify')
@click.argument(
    "input_files",
    nargs=-1,
)
@click.option(
    "-o", "--output", help="Output file", default="duplicates.json", required=True
)
def deduplicate_identify(*args, **kwargs):

    """
    Identifies fragments with duplicated sequences.

    Merges the hashed dictionaries (in json format) generated by the "parse" subcommand and 
    identifies read with exactly the same sequence (share an identical hash). Duplicated read
    identifiers (hashed) are output in json format. The "remove" subcommand uses this dictionary
    to remove duplicates from fastq files.

    """

    from capcruncher.cli.fastq_deduplicate import identify
    identify(*args, **kwargs)
    

@deduplicate.command(name='remove')
@click.argument("input_files", nargs=-1)
@click.option(
    "-o",
    "--output_prefix",
    help="Output prefix for deduplicated fastq file(s)",
    default="",
)
@click.option(
    "-d",
    "--duplicated_ids",
    help="Path to duplicate ids, identified by the identify subcommand",
)
@click.option(
    "--read_buffer",
    help="Number of reads to process before writing to file",
    default=1e5,
    type=click.INT,
)
@click.option(
    "--gzip/--no-gzip",
    help="Determines if files are gziped or not",
    default=False
)
@click.option(
    "--compression_level",
    help="Level of compression for output files",
    default=5,
    type=click.INT,
)
@click.option("--sample_name", help="Name of sample e.g. DOX_treated_1", default='sampleX')
@click.option("--stats_prefix", help="Output prefix for stats file", default='stats')
def deduplicate_remove(*args, **kwargs):
    """
    Removes fragments with duplicated sequences from fastq files.
    
    Parses input fastq files and removes any duplicates from the fastq file(s) that are
    present in the json file supplied. This json dictionary should be produced by the 
    "identify" subcommand. 

    Statistics for the number of duplicated and unique reads are also provided.
    """
    from capcruncher.cli.fastq_deduplicate import remove
    remove(*args, **kwargs)


