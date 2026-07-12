# Data sources & provenance

The corpus (`data/economic_verses_aligned.csv`) is **105 muʿāmalāt anchor verses ×
5 national editions**, joined on the sūra:āya key (identical across editions). Each
edition is a short, verse-level excerpt drawn from an open digital repository.

| Code | Edition (label in code) | Source actually used | Official authority it represents |
|------|-------------------------|----------------------|----------------------------------|
| `id` | Indonesia (Kemenag) | QuranEnc translation `indonesian_affairs` | LPMQ, Kemenag RI — *Al-Qur'an dan Terjemahnya*, 2019 |
| `ms` | Malaysia (Basmeih) | Quran.com translation **#39** (Abdullah Basmeih) | Basis of JAKIM's *Tafsir Pimpinan ar-Rahman* |
| `bn` | Brunei (KHEU) | Verse strings from the official KHEU mobile application | Kementerian Hal Ehwal Ugama, Brunei |
| `th` | Thailand (Rowwad) | QuranEnc translation `thai_rwwad` | Rowwad Translation Center (see caveat) |
| `tl` | Philippines (Tagalog) | QuranEnc translation `tagalog_rwwad` | Rowwad Translation Center (see caveat) |

Arabic anchor text and Indonesian/Tagalog footnotes are taken from the same
QuranEnc records. `scripts/01_fetch_corpus.py` regenerates `id`, `ms`, `th`, `tl`;
the Brunei column was extracted separately from the KHEU app.

## Important caveat (Thailand & the Philippines)

For Indonesia, Malaysia, and Brunei the editions are **state-authorised** texts, so
the "convergence of the Malay family" result rests on genuinely official editions.
For **Thailand and the Philippines** we use the open **Rowwad** editions, *not* a
state-tashīḥ translation:

- Thailand's official translation (CICOT / Sheikhul Islam office, Suwannasat 1968)
  is not openly available as clean digital text.
- The Philippines has **no single state translation** (the Tagalog/Maranao editions
  are scholar-team works, not state products).

These two editions therefore stand in as the most widely available, digitally clean
renderings, not as instruments of state authority. This is a limitation of the
corpus and should be stated as such in any reuse.

## Copyright

The translation strings remain the intellectual property of the respective
authorities and translation centers. They are reproduced here only as short,
verse-level excerpts for scholarly analysis and citation (see `LICENSE`). The MIT
license covers the **code only**, not the translated text.

## APIs used

- **QuranEnc** — `https://quranenc.com/api/v1/translation/aya/{key}/{sura}/{aya}`
- **Quran.com** — `https://api.quran.com/api/v4/quran/translations/{id}?verse_key=...`
