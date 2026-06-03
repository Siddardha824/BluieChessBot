from PySide6.QtGui import QColor

from ..models.active_theme import (
    ActiveTheme,
    TypographyTheme,
    WindowTheme,
    NavigationTheme,
    BoardTheme,
    ContainerTheme,
    ButtonTheme,
    InputTheme,
    ConsoleTheme,
    ChartTheme,
    EvalBarTheme,
    StatusTheme,
)


CHESSCOM_THEME = ActiveTheme(
    name="Chess.com Classic",

    typography=TypographyTheme(
        family="Outfit",
        tiny=9,
        small=10,
        normal=11,
        large=13,
        heading=16,
        title=24,
    ),

    window=WindowTheme(
        background=QColor("#1E1E1E"),
        surface=QColor("#262522"),
        border=QColor("#3B3A36"),

        text=QColor("#F5F5F5"),
        text_muted=QColor("#B0B0B0"),
        text_disabled=QColor("#7A7A7A"),

        accent=QColor("#81B64C"),
    ),

    navigation=NavigationTheme(
        background=QColor("#1A1A1A"),

        item_text=QColor("#D0D0D0"),
        item_text_selected=QColor("#FFFFFF"),

        item_hover=QColor("#2E2D2A"),
        item_selected=QColor("#81B64C"),

        icon=QColor("#B0B0B0"),
        icon_selected=QColor("#FFFFFF"),
    ),

    board=BoardTheme(
        light_square=QColor("#EEEED2"),
        dark_square=QColor("#769656"),

        selection=QColor(255, 235, 59, 140),
        legal_move=QColor(0, 0, 0, 80),
        last_move=QColor(255, 255, 0, 80),
        check=QColor(255, 82, 82, 150),

        coordinate_light=QColor("#769656"),
        coordinate_dark=QColor("#EEEED2"),
    ),

    container=ContainerTheme(
        background=QColor("#262522"),
        border=QColor("#3B3A36"),

        title_text=QColor("#FFFFFF"),
        body_text=QColor("#E0E0E0"),
        muted_text=QColor("#A0A0A0"),
    ),

    button=ButtonTheme(
        primary_background=QColor("#81B64C"),
        primary_text=QColor("#FFFFFF"),

        secondary_background=QColor("#3B3A36"),
        secondary_text=QColor("#E0E0E0"),

        danger_background=QColor("#D9534F"),
        danger_text=QColor("#FFFFFF"),

        hover_overlay=QColor(255, 255, 255, 20),
    ),

    input=InputTheme(
        background=QColor("#1E1E1E"),
        border=QColor("#4B4A45"),

        text=QColor("#F5F5F5"),
        placeholder=QColor("#8A8A8A"),

        focus_border=QColor("#81B64C"),
    ),

    console=ConsoleTheme(
        background=QColor("#181818"),

        input_text=QColor("#A5D6A7"),
        output_text=QColor("#F0F0F0"),

        info_text=QColor("#81C784"),
        error_text=QColor("#EF5350"),
    ),

    chart=ChartTheme(
        background=QColor("#262522"),

        grid=QColor("#3B3A36"),
        axis=QColor("#8A8A8A"),

        primary_line=QColor("#81B64C"),
        secondary_line=QColor("#64B5F6"),
        tertiary_line=QColor("#FFB74D"),
    ),

    evalbar=EvalBarTheme(
        white=QColor("#EEEED2"),
        black=QColor("#4A4A4A"),

        text=QColor("#FFFFFF"),
    ),

    status=StatusTheme(
        success=QColor("#81B64C"),
        warning=QColor("#F9A825"),
        error=QColor("#E53935"),
        info=QColor("#42A5F5"),
    ),
)