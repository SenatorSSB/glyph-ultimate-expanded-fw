//in: desired "output"
//out: procon or GCC values that give that value (or the closest it can get)

#include <stdint.h>
#include <stdbool.h>

#include "game_utils/Ult_adc.h"

//in: desired ult output
//out: gcc value
uint8_t ultToGcc[] = {
    0, //0
    15, //1 - impossible
    16, //2
    16, //3 - impossible
    17, //4
    17, //5 - impossible
    18, //6
    18, //7 - impossible
    19, //8 - impossible
    19, //9
    19, //10 - impossible
    20, //11
    20, //12 - impossible
    21, //13
    21, //14 - impossible
    22, //15 - impossible
    22, //16
    22, //17 - impossible
    23, //18
    23, //19 - impossible
    24, //20
    24, //21 - impossible
    25, //22 - impossible
    25, //23
    25, //24 - impossible
    26, //25
    26, //26 - impossible
    27, //27
    27, //28 - impossible
    28, //29 - impossible
    28, //30
    28, //31 - impossible
    29, //32
    29, //33 - impossible
    30, //34
    30, //35 - impossible
    31, //36 - impossible
    31, //37
    31, //38 - impossible
    32, //39
    32, //40 - impossible
    33, //41
    33, //42 - impossible
    34, //43
    34, //44 - impossible
    35, //45 - impossible
    35, //46
    35, //47 - impossible
    36, //48
    36, //49 - impossible
    37, //50
    37, //51 - impossible
    38, //52 - impossible
    38, //53
    39, //54 - impossible
    39, //55
    39, //56 - impossible
    40, //57
    40, //58 - impossible
    41, //59 - impossible
    41, //60
    41, //61 - impossible
    42, //62
    42, //63 - impossible
    43, //64
    43, //65 - impossible
    44, //66 - impossible
    44, //67
    44, //68 - impossible
    45, //69
    45, //70 - impossible
    46, //71
    46, //72 - impossible
    47, //73 - impossible
    47, //74
    47, //75 - impossible
    48, //76
    48, //77 - impossible
    49, //78
    49, //79 - impossible
    50, //80
    50, //81 - impossible
    51, //82 - impossible
    51, //83
    51, //84 - impossible
    52, //85
    52, //86 - impossible
    53, //87
    53, //88 - impossible
    54, //89 - impossible
    54, //90
    54, //91 - impossible
    55, //92
    55, //93 - impossible
    56, //94
    56, //95 - impossible
    57, //96 - impossible
    57, //97
    57, //98 - impossible
    58, //99
    58, //100 - impossible
    59, //101
    59, //102 - impossible
    60, //103 - impossible
    60, //104
    60, //105 - impossible
    61, //106
    61, //107 - impossible
    62, //108
    62, //109 - impossible
    63, //110 - impossible
    63, //111
    63, //112 - impossible
    64, //113
    64, //114 - impossible
    65, //115
    65, //116 - impossible
    66, //117 - impossible
    66, //118
    66, //119 - impossible
    67, //120
    67, //121 - impossible
    68, //122
    68, //123 - impossible
    68, //124
    69, //125 - impossible
    69, //126 - impossible
    70, //127 - maximum output value
    // 70, //127 - maximum raw value
};


//in: desired ult output
//out: POKKEN conch value
uint8_t ultToPok[] = {
    0, //0
    11, //1
    12, //2
    13, //3
    14, //4
    14, //5 - impossible
    15, //6
    16, //7
    17, //8
    18, //9
    19, //10
    20, //11
    21, //12
    22, //13
    23, //14
    24, //15
    24, //16 - impossible
    25, //17
    26, //18
    27, //19
    28, //20
    29, //21
    30, //22
    31, //23
    32, //24
    33, //25
    33, //26 - impossible
    34, //27
    35, //28
    36, //29
    37, //30
    38, //31
    39, //32
    40, //33
    41, //34
    42, //35
    43, //36
    43, //37 - impossible
    44, //38
    45, //39
    46, //40
    47, //41
    48, //42
    49, //43
    50, //44
    51, //45
    52, //46
    52, //47 - impossible
    53, //48
    54, //49
    55, //50
    56, //51
    57, //52
    58, //53
    59, //54
    60, //55
    61, //56
    62, //57
    62, //58 - impossible
    63, //59
    64, //60
    65, //61
    66, //62
    67, //63
    68, //64
    69, //65
    70, //66
    71, //67
    71, //68 - impossible
    72, //69
    73, //70
    74, //71
    75, //72
    76, //73
    77, //74
    78, //75
    79, //76
    80, //77
    81, //78
    81, //79 - impossible
    82, //80
    83, //81
    84, //82
    85, //83
    86, //84
    87, //85
    88, //86
    89, //87
    90, //88
    90, //89 - impossible
    91, //90
    92, //91
    93, //92
    94, //93
    95, //94
    96, //95
    97, //96
    98, //97
    99, //98
    100, //99
    100, //100 - impossible
    101, //101
    102, //102
    103, //103
    104, //104
    105, //105
    106, //106
    107, //107
    108, //108
    109, //109
    109, //110 - impossible
    110, //111
    111, //112
    112, //113
    113, //114
    114, //115
    115, //116
    116, //117
    117, //118
    118, //119
    119, //120
    119, //121 - impossible
    120, //122
    121, //123
    122, //124
    123, //125
    124, //126
	127,
	//let's just do max here
    //125, //127 - maximum output value
    // 126, //127
    // 127, //127 - maximum raw value
};


uint8_t stickValueFromDesiredOutput(int8_t stickValue, bool gcc) {
    uint8_t* LUT;
    if(gcc) {
        LUT = ultToGcc;
    } else {
        LUT = ultToPok;
    }

    if(stickValue >= 0) {
        return 128 + LUT[stickValue];
    } else if(gcc){
        return 128 - LUT[stickValue * -1];
    } else {
        return 127 - LUT[stickValue * -1];
    }
}
