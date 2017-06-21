#######
####### get some stats and some plots 
args = commandArgs(trailingOnly = T)

if (length(args) != 1){
  stop('Please provide fastQ output directory as solitary input')
} else if (length(args) == 1) output.dir = args

output.dir = '~/Barcode_Partitioning/test.cases/'
setwd(output.dir)
output.fastqs = list.files(path = output.dir, pattern = 'fastq')
output.table = data.frame(sample.ids = character(length(output.fastqs)), read.counts = numeric(length(output.fastqs)), stringsAsFactors = F)
for (i in seq(1, length(output.fastqs))){
  command = paste0('wc -l ', output.fastqs[i]) 
  test = system(command, intern = T)
  results = unlist(strsplit(x = test, split = ' '))
  ind = which(results == output.fastqs[i])
  id = results[ind]
  counts = as.numeric(results[ind-1])/4
  output.table$sample.ids[i] = id
  output.table$read.counts[i] = counts

}
write.table(x = output.table, file = 'demultiplexingResults.txt', append = F, quote = F, sep = '\t', row.names = F, col.names = T)
pdf('graphicalDemultiplexingResults.pdf')
barplot(height = output.table$read.counts, names.arg = output.table$sample.ids, ylab = '# reads/file', col = 'red', cex.names = 0.3)
dev.off()
