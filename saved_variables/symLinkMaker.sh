ext="cn2"
unlink graph.txt 
unlink longest_chain.txt 
unlink dataframe.txt 
ln -s graph_${ext}.txt graph.txt
ln -s dataframe_${ext}.txt dataframe.txt
ln -s longest_chain_${ext}.txt longest_chain.txt
