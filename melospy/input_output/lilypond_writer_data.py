""" Static data for LilypondWriter"""

instrument_clefs = {"ts":"treble_8",
                    "ts-c":"treble_8",
                    "as": "treble_8",
                    "bs": "bass",
                    "bsx": "bass",
                    "cbsx": "bass",
                    "ss": "treble",
                    "sss": "treble",
                    "cl": "treble",
                    "bcl": "bass",
                    "acl": "treble",
                    "tp": "treble",
                    "tpt": "treble",
                    "flgn": "treble",
                    "tb": "bass",
                    "fl": "treble",
                    "cor": "treble",
                    "ptp": "treble",
                    "frhn": "treble",
                    "ob": "treble",
                    "voc": "treble",
                    "vib": "treble",
                    "g":"treble_8",
                    "corn": "treble",
                    "b":"bass_8"}

lilypond_header = """\\version "{}"\n
#(ly:set-option 'point-and-click #f)\n
"""
title_header = """\\header {{
  title = "{}"
  composer = "{}"
  tagline = ##f
}}
"""
global_sect = """global =
{{
    \\override Staff.TimeSignature #'style = #'()
    \\time {}
    \\clef "{}"
    \\key {}
    \\override Rest #'direction = #'0
    \\override MultiMeasureRest #'staff-position = #0
}}
"""
transpose_sect ="""\\transpose c' {}
"""
overrides = (r""" \global
  		%\override Score.MetronomeMark #'transparent = ##t
  		%\override Score.MetronomeMark #'stencil = ##f
  		\override HorizontalBracket #'direction = #UP
  		\override HorizontalBracket #'bracket-flare = #'(0 . 0)
  		\override TextSpanner #'dash-fraction = #1.0
  		\override TextSpanner #'bound-details #'left #'text = \markup{ \concat{\draw-line #'(0 . -1.0) \draw-line #'(1.0 . 0) }}
  		\override TextSpanner #'bound-details #'right #'text = \markup{ \concat{ \draw-line #'(1.0 . 0) \draw-line #'(0 . -1.0) }}
        \set Score.markFormatter = #format-mark-box-numbers""")

chord_sect = (r"""\new ChordNames {{ \chords {{
              \set majorSevenSymbol = \markup {{ "maj7" }}
              \set minorChordModifier = \markup {{ \char ##x2013 }}
              {}
              }}
              }}""")
main_sect = """\\score
{{
<<
    {}
    {}
    \\new Staff
    <<
    {}
    {{
     {}
     {}
     {}
     {}
    }}
    >>
>>
}}
"""
