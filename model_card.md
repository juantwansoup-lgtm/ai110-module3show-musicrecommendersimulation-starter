# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

The clearest bias I found during evaluation is an **"energy gap" that creates a
filter bubble against moderate-energy listeners.** The 17-song catalog is
bimodal on energy: 7 songs sit in a low cluster (0.28–0.48) and 8 sit in a high
cluster (0.74–0.96), but there is a hole in the middle — no song at all between
0.55 and 0.74. Because the scoring rewards energy *proximity* (`2.0 × (1 −
|Δenergy|)`), a user who wants a moderate energy of ~0.65 can never get a true
match: the nearest songs are ~0.1 away, so the best any track can score on
energy is capped below the maximum, and the "closest" pick is chosen almost at
random from unrelated genres. In effect the system quietly serves chill users
and hype users well while under-serving anyone in between — a fairness problem
driven entirely by how the data happens to be distributed, not by the user's
request. This compounds a second data limitation: 12 of the 14 genres appear
only once, so even when a user's genre *does* match, there is zero within-genre
variety and the rest of the list is filler, making the "top 5" feel repetitive
and thin for most tastes.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected.

### Profiles I tested

I ran the recommender against **seven** taste profiles and looked at the top 5
songs for each (full output is in the README):

**Three normal listeners**

- **High-Energy Pop** — pop, happy, energy 0.9
- **Chill Lofi** — lofi, chill, energy 0.35, likes acoustic
- **Deep Intense Rock** — rock, intense, energy 0.9

**Four "adversarial" edge cases** (built to try to trick the scoring)

- **Conflicting** — classical, melancholy, but energy 0.95 (wants sad *and* hyped)
- **Out-of-range energy** — metal, angry, energy 2.0 (an impossible value)
- **Unknown genre & mood** — polka, ecstatic (words that appear on no song)
- **Empty profile** — no preferences at all

I checked whether each list "felt right," whether songs I expected to win
actually won, and whether two different-sounding users got sensibly different
lists.

### What surprised me

The biggest surprise was how often **the same high-energy songs show up for
very different people.** "Gym Hero," "Storm Runner," and "Pulse Reactor"
appeared in the bottom of both the Happy Pop list and the Intense Rock list,
even though those are almost opposite tastes. The reason is that once a song
can't match your genre or mood, the only thing left deciding its place is how
close its energy is to yours — and both of those users asked for a high energy
(0.9), so the same loud songs fill both their lists. I was also surprised that
the adversarial profiles never crashed or complained; even the impossible ones
returned five confident-looking picks.

### Comparing profiles, pair by pair

**Happy Pop vs. Chill Lofi.** These two share *zero* songs, which is exactly
what I hoped for. The pop user wants loud and upbeat (energy 0.9), the lofi user
wants quiet and calm (energy 0.35), so the two ends of the catalog cleanly
separate. The lofi scores are higher overall (top song 6.00 vs 5.34) because
the catalog simply has more lofi songs *and* the lofi user gets an extra bonus
for liking acoustic music. This comparison shows genre and energy are steering
the results the way they should.

**Happy Pop vs. Intense Rock.** This is the revealing pair. The *tops* of the
lists differ correctly — Happy Pop's #1 is the cheerful "Sunrise City," Intense
Rock's #1 is the aggressive "Storm Runner" — but from #4 down the two lists look
almost the same (both end in Storm Runner / Gym Hero / Pulse Reactor). Both
users asked for energy 0.9, and since none of those tail songs match either
user's exact genre or mood, energy is the *only* thing left ranking them. So two
people with opposite tastes get nearly identical filler at the bottom. This is
the clearest sign that energy quietly dominates whenever genre and mood go
silent.

**Chill Lofi vs. Intense Rock.** Complete opposites — calm acoustic vs. loud and
angry — and they share no songs, which is the correct result. Nothing on the
lofi list is remotely aggressive, and nothing on the rock list is soft. When two
profiles disagree on *both* genre and energy, the system separates them cleanly;
the trouble only appears (as above) when two profiles agree on energy.

**Normal vs. adversarial (Happy Pop vs. Out-of-range energy).** The out-of-range
user asked for energy 2.0, which is impossible (real values stop at 1.0). Instead
of rejecting it, the system kept going and the energy part of the score turned
*negative*, dragging most songs below zero. Only the one song matching genre and
mood ("Iron Verdict") stayed positive. Compared to Happy Pop's tidy list, this
shows the scoring trusts whatever number it's given.

**Adversarial vs. adversarial (Unknown genre & mood vs. Empty profile).** Both of
these have no valid genre or mood to match. The Empty profile has nothing to go
on at all, so every song ties at 0.00 and the "top 5" is just the first five
rows of the file. The Unknown profile still has an energy target (0.5), so it at
least sorts songs by energy closeness — which is why it produces a real-looking
ranking even though the genre "polka" and mood "ecstatic" matched nothing. The
difference shows energy is the one signal keeping the system afloat when the
word-matching fails.

### Explaining it to a non-programmer: why does "Gym Hero" keep showing up for "Happy Pop" fans?

Think of the score as points in three buckets: points for being the right *type*
of music (genre), points for having the right *feeling* (mood), and points for
being the right *loudness/intensity* (energy). "Gym Hero" is a pop song, so it
grabs the genre points — but it's a tense workout track, not a happy one, so it
misses the "happy" feeling points. A song like "Rooftop Lights" is genuinely
happy but isn't filed under plain "pop." Because being the right *type* of music
is worth slightly more than having the right *feeling*, the pop-but-not-happy
"Gym Hero" edges out the happy-but-not-pop song. So a listener who just wants
*happy pop* keeps getting a gym anthem — the system is rewarding the label on the
song more than the actual vibe the person asked for.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

My biggest takeaway is that the "smarts" in a recommender aren't in the code —
they're in the weights and the data. When I halved the genre weight and doubled
energy, a genuinely happy song finally beat a mislabeled gym track, and I
realized I hadn't fixed a bug so much as changed my mind about what should
matter more. The code was always doing exactly what I told it.

AI tools were great for the busywork — scaffolding the profile runner, drafting
edge cases, cleaning up the output. But I learned to double-check anything with
a number in it. The AI could describe a bias convincingly, but I didn't believe
"there's an energy gap" until I counted the songs myself (7 low, 2 middle, 8
high). It also missed that an impossible energy of 2.0 quietly produced negative
scores. So I treated its answers as a solid first draft, not the truth.

What surprised me most was how real the results feel for something so simple.
No machine learning, no listening history — just points for genre, mood, and
energy — and yet it reads like a thoughtful playlist with reasons for each pick.
Even the empty and nonsense profiles came back with five confident songs, which
was a little unsettling.

If I kept going, I'd fix the data first (a bigger, more even catalog to close
the energy gap), then add input validation, loosen the exact-word matching so
"indie pop" and "pop" count for something, and stop the top 5 from filling up
with energy-only filler.
