######
###### scripts to generate test cases for barcode demultiplexing challenge
list.of.packages <- c("data.table", "stringr")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
library(data.table)
library(stringr)

full.barcodes = fread('/Users/josephb1/Desktop/barcodes.txt', header = F)
just.barcodes.and.polyT = unlist(strsplit(x = full.barcodes$V2, split = 'GCCGGTAATACGACTCACTATAGGGAGTTCTACAGTCCGACGATCNNNNNN'))[2*(1:length(full.barcodes$V2))]
just.barcodes = unlist(strsplit(x = just.barcodes.and.polyT, split = 'TTTTTTTTTTTTTTTTTTTTTTTTV'))
modified.barcodes = data.frame(ids = full.barcodes$V1, barcodes = just.barcodes)

set.seed(seed = 2017)
generate.random.seqs = function(length.of.tag, number.of.seqs){
  characters = c('A', 'C', 'G', 'T')
  random.nucleotide = replicate(n = number.of.seqs, expr = paste0(characters[sample(x = c(1:4), size = length.of.tag, replace = T, prob = rep(x = 0.25,4))], collapse = ''))
  return(random.nucleotide)
}

generate.random.qualities = function(length.of.tag, number.of.seqs){
  characters = as.character(unlist(strsplit(rawToChar(as.raw(c(33, 35:75))), "")))
  random.nucleotide = replicate(n = number.of.seqs, expr = paste0(characters[sample(x = c(1:42), size = length.of.tag, replace = T, prob = rep(x = 1/42,42))], collapse = ''))
  return(random.nucleotide)
}

random.seqs = generate.random.seqs(length.of.tag = 8, number.of.seqs = 100000)
reads = generate.random.seqs(length.of.tag = 50, number.of.seqs = 100000)
test.barcodes = just.barcodes[sample(c(1:12), size = 100000, replace = T, prob = rep(x = 1/12, 12))]
extras = 'ACTG'
read.names = paste0('test.', 1:100000, ':', test.barcodes)
#test.qualities = generate.random.qualities(length.of.tag = 50, number.of.seqs = 100000)
  
generate.test.cases = function(barcodes, reads, degenerates, extras, barcode.position, read.names, number.of.reads){
  length.of.tag = sum(str_count(barcodes[1]) + str_count(reads[1]) + str_count(extras[1]) + str_count(degenerates[1]))
  quality.scores = generate.random.qualities(length.of.tag = length.of.tag, number.of.seqs = number.of.reads)
  if (barcode.position == 'left'){
    full.reads = paste0(barcodes, degenerates,rep(extras, number.of.reads),reads)
    pasted.fastqs = paste0('@', read.names, 'split', full.reads, 'split', '+', read.names, 'split', quality.scores) 
    return(pasted.fastqs)
  } else if (barcode.position == 'right') {
    full.reads = paste0( degenerates,barcodes,rep(extras, number.of.reads),reads)
    pasted.fastqs = paste0('@', read.names, 'split', full.reads, 'split', '+', read.names, 'split', quality.scores) 
    return(pasted.fastqs)
  }
  
}
test.left = generate.test.cases(barcodes = test.barcodes, reads = reads, degenerates = random.seqs, extras = extras, barcode.position = 'left', read.names = read.names, number.of.reads = 100000)
test.left.split = unlist(strsplit(x = test.left, split = 'split'))
table(factor(test.barcodes))

test.right = generate.test.cases(barcodes = test.barcodes, reads = reads, degenerates = random.seqs, extras = extras, barcode.position = 'right', read.names = read.names, number.of.reads = 100000)
test.right.split = unlist(strsplit(x = test.right, split = 'split'))

write.table(x = test.left.split, file = '~/Desktop/basic2.R2.fastq', append = F, quote = F, sep = '\n', row.names = F, col.names = F)
write.table(x = test.right.split, file = '~/Desktop/basic1.R1.fastq', append = F, quote = F, sep = '\n', row.names = F, col.names = F)


#######
####### add errors and variable degenerate lengths

generate.random.seqs.with.variation = function(length.of.tag, number.of.seqs){
  characters = c('A', 'C', 'G', 'T')
  random.seq.lengths = rbinom(n = number.of.seqs, size = length.of.tag*2, prob = 0.5)
  one.random.seq.generator = function(lengths){
    seqs = paste0(characters[sample(x = c(1:4), size = lengths, replace = T, prob = rep(x = 0.25,4))], collapse = '')
    return(seqs)
  }
  random.nucleotide = sapply(X = random.seq.lengths, FUN = one.random.seq.generator)
  return(random.nucleotide)
}

mutate.barcode = function(barcode, error){
  chars = c('A','C','G','T')
  str.length = str_count(barcode)
  if (error != 0){
    inds = sample(1:str.length, size = error, replace = F)
    vals = unlist(strsplit(x = barcode, split = ''))
    for (i in 1:error){
      vals[inds[i]] = sample( chars[!chars %in% vals[inds[i]]], size = 1 )
    }
    barcode = paste0(vals, collapse = '') 
  }
  return(barcode)
}

random.seqs = generate.random.seqs.with.variation(length.of.tag = 6, number.of.seqs = 1000000)
reads = generate.random.seqs(length.of.tag = 50, number.of.seqs = 1000000)
test.barcodes = just.barcodes[sample(c(1:12), size = 1000000, replace = T, prob = rep(x = 1/12, 12))]
extras = 'ACTG'
read.names = paste0('test.', 1:1000000, ':', test.barcodes)
error.rate = c(0,1,2,3,4)
error.rate.probs = c(0.9, 0.06, 0.025, 0.01, 0.005)
errors = sample(x = error.rate, size = 1000000, replace = T, prob = error.rate.probs)
new.barcodes = character(length = 1000000)
for (i in seq(from = 1, to = 1000000, by = 1)){
  new.barcodes[i] = mutate.barcode(barcode = test.barcodes[i], error = errors[i])
  print(i)
}

new.barcodes.lengths = str_length(new.barcodes)
random.seqs.lengths = str_length(random.seqs)
qual.lengths = new.barcodes.lengths + random.seqs.lengths + 54

new.qualities = sapply(X = qual.lengths, FUN = generate.random.qualities, number.of.seqs = 1)

struct2 = paste0('@', read.names, 'split', new.barcodes, random.seqs, extras, reads, 'split',
       '+', read.names, 'split', new.qualities)

struct1 = paste0('@', read.names, 'split', random.seqs, new.barcodes, extras, reads, 'split',
                 '+', read.names, 'split', new.qualities)

final.struct1 = unlist(strsplit(x = struct1, split = 'split'))
final.struct2 = unlist(strsplit(x = struct2, split = 'split'))

#write.table(x = final.struct1, file = '~/Desktop/random.barcode.R1.fastq', append = F, quote = F, sep = '\n', row.names = F, col.names = F)
#write.table(x = final.struct2, file = '~/Desktop/barcode.random.R2.fastq', append = F, quote = F, sep = '\n', row.names = F, col.names = F)





