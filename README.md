I forgot I made this repo like 2 years ago, but I actually need to make an Ultimate Guitar scraper now. Super lucky that I don't have to make a new repo (altho that would take like 10 seconds to do).

Here's what schollz did for his MCMC project (using this as a source of inspiration):

> To gather song data to analyze, I first wrote a program that parsed guitar tabs and extracted chords. The data sample included more than one million songs from almost every genre (except for classical), including blues, jazz, pop, rock, country, folks, etc. I divided each song into sections (i.e. Verse, Chorus, Pre-chorus) and collected the names of chords contained in each section. To aid in comparison, I transposed all the chords in each section of each song so that they were in the same key, the key of C.
> Once the data was ready, I found that I had compiled over two thousand different four-chord progressions.
> To rank these chord progressions I used Markov chain Monte Carlo to sample the probability distribution of four-chord progressions. This produced a list from most to least common chord progressions.

What the plan of action looks like for me:
- (DONE) Write a scraper that goes to https://www.ultimate-guitar.com/explore filtered by a given genre or subgenre, then scrapes the links to the top ~1000-10000 songs in that genre
 - Genres/subgenres I've decided I want to do: 
  - Rock:
  - Metal:
  - Pop:
  - Folk:
  - Country:
  - RnB: ?genres[]=1787
  - Electronic:
- (DONE) Write a second scraper that, for each link scraped by the first scraper, retrieves all of the chords in order and saves them
- Collect dataset statistics, (for now) cull songs with minimally used chords, and transpose all songs to C/Am
- Run MCMC for all songs in each genre/subgenre
- Train a first-order HMM on the probabilities retrieved
- Maybe try training a higher order HMM?

