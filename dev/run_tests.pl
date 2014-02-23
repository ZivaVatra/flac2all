my $infolder = "./testinput";
my $outfolder = "./testoutput";

# If the test folder does not exist, create it and populate it with music for testing
unless ( -e $infolder ) {
	die( "Error, $infolder does not exist. Please create it and stick some FLAC files in there for testing\n" );
}

my @flacfiles = <"$infolder/*.flac"> ;
if (scalar(@flacfiles) == 0) {
	die("No flac files found in $infolder. Please put some in there for testing (no subfolders please)...\n");
}

unless ( -e $outfolder ) { mkdir($outfolder); }

my @testypes = ("mp3","vorbis","flac","aacplusnero");

for $test (@testypes) {
	my $larg = "--lame-options='-preset standard' ";
	my $aarg = "--aacplus-options 64";
	my $varg = "--vorbis-options='quality=5:resample 32000:downmix'";

	for $opt ('-c','-f','-t 4','-n') {
		my $cmd = "python ./__main__.py $test $larg $aarg $varg $opt -o $outfolder/$test/ $infolder\n";
		die($cmd);
		print '-'x80;
		print "Executing: $cmd";
		print '-'x80;
		$rc = system($cmd);
		if ($rc != 0) {
			die("ERROR Executing command: \"$cmd\"\n");
		}
	}
}

rmdir($outfolder);

