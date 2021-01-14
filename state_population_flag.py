import os
import os.path
import math


OUTPUT_PATH = 'flags'

OUTPUT_NORMAL = os.path.join(OUTPUT_PATH, 'us_flag.svg')
OUTPUT_BY_POPULATION = os.path.join(OUTPUT_PATH, 'us_flag_stars_and_stripes_scaled_by_population.svg')
OUTPUT_BY_AREA = os.path.join(OUTPUT_PATH, 'us_flag_stars_and_stripes_scaled_by_area.svg')
OUTPUT_BY_POPULATION_ANIMATED = os.path.join(OUTPUT_PATH, 'us_flag_stars_and_stripes_scaled_by_population_animated.svg')
OUTPUT_BY_AREA_ANIMATED = os.path.join(OUTPUT_PATH, 'us_flag_stars_and_stripes_scaled_by_area_animated.svg')
OUTPUT_BY_POPULATION_ANIMATED_TO_ELECTORAL_VOTES = os.path.join(OUTPUT_PATH, 'us_flag_stars_and_stripes_scaled_by_population_and_electoral_votes_animated.svg')

ANIMATION_TIMINGS = (10, 2, 5)  # 10 seconds showing proportional flag, 2 seconds transitioning, 5 seconds default flag, 2 seconds transitioning back
ANIMATED_ELECTORAL_VOTES = (3, 0.5, 3)

# Original flag is specified by Title 4 of the United States Code
# https://uscode.house.gov/view.xhtml?req=granuleid%3AUSC-prelim-title4&saved=%7CZ3JhbnVsZWlkOlVTQy1wcmVsaW0tdGl0bGU0LWZyb250%7C%7C%7C0%7Cfalse%7Cprelim&edition=prelim

# This might break the flag code, but the flag code is not law, nor am I American

# Flag layout:
# Ratio 10:19

# See https://uscode.house.gov/images/uscprelim/t4flag.gif
# A = 1  (Hoist / width of flag. Everything is scaled relative to this)
# B = A * 1.9  (Fly / length of flag)
# C = 7 * L = A * 7/13  (Canton is 7 red and white stripes tall)
# D = 2/5 * B = A * 0.76  (Canton is 40% of the width of the flag)
# E = F = C / 10  (Each row of stars on the canton is equidistant)
# G = H = D / 12  (Each column of stars on the canton is equidistant)
# K = L * 0.8  (Diameter of a star)
# L = A/13  (Each strip is of equal height)

# Canton ratio is C : D = 175 : 247


# Thirteen horixontal stripes, alternate red and white
# Blue canton with 50 white stars


# Don't think the colours are legally defined anywhere
# Just pick the ones that Wikipedia use
RED = '#B22234'
WHITE = '#FFFFFF'
BLUE = '#3C3B6E'

def get_relative_star_coordinate(n):
    """Returns relative (x, y) of the position of the nth star

    0 <= x <= 10
    0 <= y <= 8

    Relative to the scale of the flag, these will be integer coordinates where x+y is even
    The actual coordinate on the flag will be (G + H*x, E + F*y)

    First row is 6 stars every other even index
    >>> get_relative_star_coordinate(0) == (0, 0)
    >>> get_relative_star_coordinate(1) == (2, 0)
    ...
    >>> get_relative_star_coordinate(5) == (10, 0)
    Second row is 5 stars ever other odd index
    >>> get_relative_star_coordinate(6) == (1, 1)
    >>> get_relative_star_coordinate(7) == (3, 1)
    ...
    >>> get_relative_star_coordinate(10) == (9, 1)
    And so on
    """
    y, x = divmod(n * 2, 11)
    return x, y


def polar_to_cartesian(r, theta):
    return r * math.cos(theta), r * math.sin(theta)


def make_svg(red_stripe_defs, star_scales, animate_duration=None, canton_width=0.4, alt_default=None):
    """
    red_strip_defs is a list of 7 pairs (top_y, height) where the 7 red stripes are each starting at top_y and ending at top_y+height
    (In relative units where the height of the flag is 1)

    star_scales is a map from states to floats which represent how much the area of each star needs to be scaled

    If animate_duration is not None, will animate so that the flag will cycle between the default US flag and the scaled version in that duration

    If alt_default is not None, it should be a tuple (red_stripe_defs, star_scales, canton_width), (red_stripe_defs, star_scales) or (star_scales,)
    as above which will be used as the default flag instead (red_stripe_defs will default to 1/13th width, canton_width will default to the canton_width of the other flag)

    canton_width is the proportion of the flag the canton takes up (40% on a standard US flag). Set to -n to be scaled to n red/white stripes tall
    """
    do_animate = animate_duration is not None
    has_alt_default = alt_default is not None
    if has_alt_default:
        if len(alt_default) == 3:
            alt_red_stripe_defs, alt_star_scales, alt_canton_width = alt_default
        elif len(alt_default) == 2:
            alt_red_stripe_defs, alt_star_scales = alt_default
            alt_canton_width = None
        else:
            alt_star_scales, = alt_default
            alt_red_stripe_defs = None
            alt_canton_width = None

    if do_animate:
        proportional_time, transition_time, default_time = animate_duration
        duration = proportional_time + 2*transition_time + default_time
        timing = ''.join(map(str, (
            'repeatCount="indefinite" dur="', duration, 's" keyTimes="0;',
            proportional_time / duration, ';', (proportional_time + transition_time) / duration, ';', (proportional_time + transition_time + default_time) / duration, ';1"'
        )))
        def make_animate(name, value, default_value):
            return ''.join((
                '<animate attributeName="', name, '" values="', value, ';', value, ';', default_value, ';', default_value, ';', value, '" ',
                timing, '/>'
            ))
    elif alt_default is not None:
        raise TypeError('animate_duration not set but alt_default is set. No animation would actually occur and alt_default would be unused')

    if canton_width < 0:
        n = -canton_width
        if n % 2 == 0:
            # Top of a red stripe
            canton_height, _ = red_stripe_defs[n // 2]
        else:
            # Bottom of a red stripe
            canton_height, height = red_stripe_defs[n // 2]
            canton_height += height
        canton_width = canton_height * 175 / 247
        canton_height_pct = str(canton_height * 100)
        canton_width_pct = str(canton_height * 17500 / 247)
    elif canton_width == 0.4:
        canton_height = 7/13
        canton_width_pct = '40'
        canton_height_pct = str(700/13)
    else:
        canton_height = canton_width * 247 / 175
        canton_width_pct = str(canton_width * 100)
        canton_height_pct = str(canton_width * 988 / 7)

    if do_animate:
        if has_alt_default and alt_canton_width is None:
            default_canton_width = canton_width
            default_canton_height = canton_height
            default_canton_height_pct = canton_height_pct
            default_canton_width_pct = canton_width_pct
        elif has_alt_default and alt_canton_width != 0.4:
            if alt_canton_width < 0:
                n = -alt_canton_width
                if n % 2 == 0:
                    default_canton_height, _ = alt_red_stripe_defs[n // 2]
                else:
                    default_canton_height, height = alt_red_stripe_defs[n // 2]
                    default_canton_height += height
                default_canton_width = default_canton_height * 175 / 247
                default_canton_height_pct = str(default_canton_height * 100)
                default_canton_width_pct = str(default_canton_height * 17500 / 247)
            else:
                default_canton_width = alt_canton_width
                default_canton_height = default_canton_width * 247 / 175
                default_canton_width_pct = str(default_canton_width * 100)
                default_canton_height_pct = str(default_canton_width * 988 / 7)
        else:
            default_canton_width = 0.4
            default_canton_height = 7/13
            default_canton_width_pct = '40'
            default_canton_height_pct = str(700/13)


    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1235" height="650" viewBox="0 0 1.9 1">'
            '<defs>'
                '<path id="s" fill="', WHITE, '" d="M'
    ]

    # #s is a white star radius 1 centred at (0, 0), with a point at (0, 1) (so it faces upwards)
    for n in range(5):
        x, y = polar_to_cartesian(1, math.tau * ((n * 2) % 5 - 0.25) / 5)
        svg.extend((str(x), ',', str(y)))

    svg.extend((
                  'Z"/>'
            '</defs>'
            '<rect width="100%" height="100%" fill="', WHITE, '"/>'  # White rectangle for 6 of the 13 stripes
    ))

    # 7 red stripes
    for i, (top_y, height) in enumerate(red_stripe_defs):
        top_y = str(top_y)
        height = str(height)
        if do_animate:
            if has_alt_default and alt_red_stripe_defs is not None:
                default_top_y, default_height = alt_red_stripe_defs[i]
                default_top_y = str(default_top_y)
                default_height = str(default_height)
            else:
                default_top_y = str(i * 2/13)
                default_height = str(1/13)
            svg.extend((
                '<rect width="100%" y="', top_y, '" height="', height, '" fill="', RED, '">',
                    make_animate('y', top_y, default_top_y),
                    make_animate('height', height, default_height),
                '</rect>'
            ))
        else:
            svg.extend(('<rect width="100%" y="', top_y, '" height="', height, '" fill="', RED, '"/>'))

    # Blue canton
    if (not do_animate) or canton_width == default_canton_width:
        svg.extend(('<rect width="', canton_width_pct, '%" height="', canton_height_pct, '%" fill="', BLUE, '"/>'))
    else:
        svg.extend((
            '<rect width="', canton_width_pct, '%" height="', canton_height_pct, '%" fill="', BLUE ,'">',
                make_animate('width', canton_width_pct + '%', default_canton_width_pct + '%'),
                make_animate('height', canton_height_pct + '%', default_canton_height_pct + '%'),
            '</rect>'
        ))

    # 50 stars
    star_column_width = canton_width * 19 / 120
    star_row_height = canton_height / 10
    star_radius = canton_height * 2 / 35  # star_diameter = canton_height / 7 * 0.8 == canton_height * 4 / 35

    if do_animate:
        default_column_width = default_canton_width * 19 / 120
        default_row_height = default_canton_height / 10
        default_star_radius = default_canton_height * 2 / 35

    for state in order_of_admission_to_union:
        cx, cy = get_relative_star_coordinate(star_index(state))

        if do_animate:
            default_radius = default_star_radius
            if has_alt_default:
                default_radius *= math.sqrt(alt_star_scales[state])
            default_cx = default_column_width + default_column_width * cx
            default_cy = default_row_height + default_row_height * cy

            radius = star_radius * math.sqrt(star_scales[state])
            cx = star_column_width + star_column_width * cx
            cy = star_row_height + star_row_height * cy

            # Transformation:
            # Scale by multiplying (x, y) by current radius
            # Translate to new centre

            scale = str(radius) + ' ' + str(radius)
            default_scale = str(default_radius) + ' ' + str(default_radius)
            translate = str(cx) + ' ' + str(cy)
            default_translate = str(default_cx) + ' ' + str(default_cy)

            svg.extend((
                '<use xlink:href="#s" transform="translate(', translate, ') scale(', scale, ')">'
                    '<animateTransform attributeName="transform" attributeType="XML" type="translate" values="',
                        translate, ';', translate, ';', default_translate, ';', default_translate, ';', translate, '" ', timing, '/>'
                    '<animateTransform attributeName="transform" attributeType="XML" type="scale" values="',
                        scale, ';', scale, ';', default_scale, ';', default_scale,';', scale, '" ', timing, ' additive="sum"/>'
                '</use>'
            ))
        else:
            radius = str(star_radius * math.sqrt(star_scales[state]))
            cx = str(star_column_width + star_column_width * cx)
            cy = str(star_row_height + star_row_height * cy)
            svg.extend(('<use xlink:href="#s" transform="translate(', cx, ' ', cy,') scale(', radius, ')"/>'))

    svg.append('</svg>\n')

    return ''.join(svg)


def get_red_stripe_defs(proportions):
    red_stripe_defs = []
    thirteen_colonies_total = sum(proportions[state] for state in thirteen_colonies_order_of_founding)
    is_red = True
    cumulative_value = 0
    for state in thirteen_colonies_order_of_founding:
        top_y = cumulative_value / thirteen_colonies_total
        state_value = proportions[state]
        cumulative_value += state_value
        height = state_value / thirteen_colonies_total
        if is_red:
            red_stripe_defs.append((top_y, height))
        is_red = not is_red

    return red_stripe_defs


def get_star_scales(proportions):
    total = sum(proportions.values())
    return {state: 50*state_value / total for state, state_value in proportions.items()}


def proportional_flag(proportions, animate_duration=None):
    return make_svg(get_red_stripe_defs(proportions), get_star_scales(proportions), animate_duration)


def main():
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    with open(OUTPUT_NORMAL, 'wb') as f:
        f.write(proportional_flag({s: 1 for s in order_of_admission_to_union}).encode('ascii'))
    with open(OUTPUT_BY_POPULATION, 'wb') as f:
        f.write(proportional_flag(state_populations).encode('ascii'))
    with open(OUTPUT_BY_AREA, 'wb') as f:
        f.write(proportional_flag(state_areas).encode('ascii'))
    with open(OUTPUT_BY_POPULATION_ANIMATED, 'wb') as f:
        f.write(proportional_flag(state_populations, ANIMATION_TIMINGS).encode('ascii'))
    with open(OUTPUT_BY_AREA_ANIMATED, 'wb') as f:
        f.write(proportional_flag(state_areas, ANIMATION_TIMINGS).encode('ascii'))
    with open(OUTPUT_BY_POPULATION_ANIMATED_TO_ELECTORAL_VOTES, 'wb') as f:
        electoral_votes_flag_info = get_red_stripe_defs(state_electoral_votes), get_star_scales(state_electoral_votes)
        svg = make_svg(get_red_stripe_defs(state_populations), get_star_scales(state_populations), ANIMATED_ELECTORAL_VOTES, -8, electoral_votes_flag_info)
        f.write(svg.encode('ascii'))


# Data section

# https://en.wikipedia.org/wiki/List_of_U.S._states_by_date_of_admission_to_the_Union

order_of_admission_to_union = (
    'DE',  #  7 Dec 1787, Delaware
    'PA',  # 12 Dec 1787, Pennsylvania
    'NJ',  # 18 Dec 1787, New Jersey
    'GA',  #  2 Jan 1788, Georgia
    'CT',  #  9 Jan 1788, Connecticut
    'MA',  #  6 Feb 1788, Massachusetts
    'MD',  # 28 Apr 1788, Maryland
    'SC',  # 23 May 1788, South Carolina
    'NH',  # 21 Jun 1788, New Hampshire
    'VA',  # 25 Jun 1788, Virginia
    'NY',  # 26 Jul 1788, New York
    'NC',  # 21 Nov 1789, North Carolina
    'RI',  # 29 May 1790, Rhode Island
# Thirteen colonies
    'VT',  #  4 Mar 1791, Vermont
    'KY',  #  1 Jun 1792, Kentucky
    'TN',  #  1 Jun 1796, Tennessee
    'OH',  #  1 Mar 1803, Ohio
    'LA',  # 30 Apr 1812, Louisiana
    'IN',  # 11 Dec 1816, Indiana
    'MS',  # 10 Dec 1817, Mississippi
    'IL',  #  3 Dec 1818, Illinois
    'AL',  # 14 Dec 1819, Alabama
    'ME',  # 15 Mar 1820, Maine
    'MO',  # 10 Aug 1821, Missouri
    'AR',  # 15 Jun 1836, Arkansas
    'MI',  # 26 Jan 1837, Michigan
    'FL',  #  3 Mar 1845, Florida
    'TX',  # 29 Dec 1845, Texas
    'IA',  # 28 Dec 1846, Iowa
    'WI',  # 29 May 1848, Wisconsin
    'CA',  #  9 Sep 1850, California
    'MN',  # 11 May 1858, Minnesota
    'OR',  # 14 Feb 1858, Oregon
    'KS',  # 29 Jan 1861, Kansas
    'WV',  # 20 Jun 1863, West Virginia
    'NV',  # 31 Oct 1864, Nevada
    'NE',  #  1 Mar 1867, Nebraska
    'CO',  #  1 Aug 1876, Colorado
    'ND',  #  2 Nov 1889, North Dakota
    'SD',  #  2 Nov 1889, South Dakota
    'MT',  #  8 Nov 1889, Montana
    'WA',  # 11 Nov 1889, Washington
    'ID',  #  3 Jul 1890, Idaho
    'WY',  # 10 Jul 1890, Wyoming
    'UT',  #  4 Jan 1896, Utah
    'OK',  # 16 Nov 1907, Oklahoma
    'NM',  #  6 Jan 1912, New Mexico
    'AZ',  # 14 Feb 1912, Arizona
    'AK',  #  3 Jan 1959, Alaska
    'HI',  # 21 Aug 1959, Hawaii
)

star_index = dict(zip(order_of_admission_to_union, range(len(order_of_admission_to_union)))).__getitem__

# (Find a source for this)

thirteen_colonies_order_of_founding = (
    'VA',
    'NY',
    'MA',
    'MD',
    'RI',
    'CT',
    'NH',
    'DE',
    'NC',
    'SC',
    'NJ',
    'PA',
    'GA'
)

# 2020 US Census (https://www.census.gov/programs-surveys/decennial-census/2020-census.html)
# hasn't released counts yet. Reportedly, they will be released by 26th January 2021

# Using Population Estimate (estimate of population as of 1st July 2020) instead
# https://www.census.gov/programs-surveys/popest/technical-documentation/research/evaluation-estimates.html
# (DC removed)
state_populations = {
    'AL':  4_921_532,
    'AK':    731_158,
    'AZ':  7_421_401,
    'AR':  3_030_522,
    'CA': 39_368_078,
    'CO':  5_807_719,
    'CT':  3_557_006,
    'DE':    986_809,
    'FL': 21_733_312,
    'GA': 10_710_017,
    'HI':  1_407_006,
    'ID':  1_826_913,
    'IL': 12_587_530,
    'IN':  6_754_953,
    'IA':  3_163_561,
    'KS':  2_913_805,
    'KY':  4_477_251,
    'LA':  4_645_318,
    'ME':  1_350_141,
    'MD':  6_055_802,
    'MA':  6_893_574,
    'MI':  9_966_555,
    'MN':  5_657_342,
    'MS':  2_966_786,
    'MO':  6_151_548,
    'MT':  1_080_577,
    'NE':  1_937_552,
    'NV':  3_138_259,
    'NH':  1_366_275,
    'NJ':  8_882_371,
    'NM':  2_106_319,
    'NY': 19_336_776,
    'NC': 10_600_823,
    'ND':    765_309,
    'OH': 11_693_217,
    'OK':  3_980_783,
    'OR':  4_241_507,
    'PA': 12_783_254,
    'RI':  1_057_125,
    'SC':  5_218_040,
    'SD':    892_717,
    'TN':  6_886_834,
    'TX': 29_360_759,
    'UT':  3_249_879,
    'VT':    623_347,
    'VA':  8_590_563,
    'WA':  7_693_612,
    'WV':  1_784_787,
    'WI':  5_832_655,
    'WY':    582_328,
}


# From 2010 census. Area as of 1st January 2010 (Includes water area)
# https://www.census.gov/geographies/reference-files/2010/geo/state-area.html

state_areas = {
    'AL': 135_767,
    'AK': 1_723_337,
    'AZ': 295_234,
    'AR': 137_732,
    'CA': 423_967,
    'CO': 269_601,
    'CT':  14_357,
    'DE':   6_446,
    'FL': 170_312,
    'GA': 153_910,
    'HI':  28_313,
    'ID': 216_443,
    'IL': 149_995,
    'IN':  94_326,
    'IA': 145_746,
    'KS': 213_100,
    'KY': 104_656,
    'LA': 135_659,
    'ME':  91_633,
    'MD':  32_131,
    'MA':  27_336,
    'MI': 250_487,
    'MN': 225_163,
    'MS': 125_438,
    'MO': 180_540,
    'MT': 380_831,
    'NE': 200_330,
    'NV': 286_380,
    'NH':  24_214,
    'NJ':  22_591,
    'NM': 314_917,
    'NY': 141_297,
    'NC': 139_391,
    'ND': 183_801,
    'OH': 116_098,
    'OK': 181_037,
    'OR': 254_799,
    'PA': 119_280,
    'RI':   4_001,
    'SC':  82_933,
    'SD': 199_729,
    'TN': 109_153,
    'TX': 695_662,
    'UT': 219_882,
    'VT':  24_906,
    'VA': 110_787,
    'WA': 184_661,
    'WV':  62_756,
    'WI': 169_653,
    'WY': 253_335,
}

# Based on 2010 census. Electoral votes per state in the 2012, 2016 and 2020 presidential elections.
# https://www.archives.gov/electoral-college/allocation
# DC is removed

state_electoral_votes = {
    'AL': 9,
    'AK': 3,
    'AZ': 11,
    'AR': 6,
    'CA': 55,
    'CO': 9,
    'CT': 7,
    'DE': 3,
    'FL': 29,
    'GA': 16,
    'HI': 4,
    'ID': 4,
    'IL': 20,
    'IN': 11,
    'IA': 6,
    'KS': 6,
    'KY': 8,
    'LA': 8,
    'ME': 4,
    'MD': 10,
    'MA': 11,
    'MI': 16,
    'MN': 10,
    'MS': 6,
    'MO': 10,
    'MT': 3,
    'NE': 5,
    'NV': 6,
    'NH': 4,
    'NJ': 14,
    'NM': 5,
    'NY': 29,
    'NC': 15,
    'ND': 3,
    'OH': 18,
    'OK': 7,
    'OR': 7,
    'PA': 20,
    'RI': 4,
    'SC': 9,
    'SD': 3,
    'TN': 11,
    'TX': 38,
    'UT': 6,
    'VT': 3,
    'VA': 13,
    'WA': 12,
    'WV': 5,
    'WI': 10,
    'WY': 3,
}

if __name__ == '__main__':
    main()
