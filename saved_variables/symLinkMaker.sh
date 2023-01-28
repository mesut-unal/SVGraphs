main="235884-WG01"
ext="v1"

unlink graph_${main}.txt 
unlink longest_chain_${main}.txt 
unlink dataframe_${main}.txt 
unlink simple_cycles_${main}.txt
ln -s graph_${main}_${ext}.txt graph_${main}.txt
ln -s dataframe_${main}_${ext}.txt dataframe_${main}.txt
ln -s longest_chain_${main}_${ext}.txt longest_chain_${main}.txt
ln -s simple_cycles_${main}_${ext}.txt simple_cycles_${main}.txt
