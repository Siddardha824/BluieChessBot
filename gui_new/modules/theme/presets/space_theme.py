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

SPACE_THEME = ActiveTheme(
    name="Space",

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
        background=QColor("#050B18"),
        surface=QColor("#091224"),
        border=QColor("#123C8D"),

        text=QColor("#F3F7FF"),
        text_muted=QColor("#8AA0C5"),
        text_disabled=QColor("#4D5D80"),

        accent=QColor("#2962FF"),
    ),

    navigation=NavigationTheme(
        background=QColor("#08111F"),

        item_text=QColor("#D6E4FF"),
        item_text_selected=QColor("#FFFFFF"),

        item_hover=QColor("#10244D"),
        item_selected=QColor("#1D4DFF"),

        icon=QColor("#88A4E8"),
        icon_selected=QColor("#FFFFFF"),
    ),

    board=BoardTheme(
        light_square=QColor("#4D548C"),
        dark_square=QColor("#1A255A"),

        selection=QColor(0, 229, 255, 120),
        legal_move=QColor(0, 229, 255, 70),
        last_move=QColor(156, 39, 255, 90),
        check=QColor(255, 64, 129, 140),

        coordinate_light=QColor("#A7C5FF"),
        coordinate_dark=QColor("#EAF2FF"),
    ),

    container=ContainerTheme(
        background=QColor("#091224"),
        border=QColor("#123C8D"),

        title_text=QColor("#F3F7FF"),
        body_text=QColor("#D8E6FF"),
        muted_text=QColor("#8AA0C5"),
    ),

    button=ButtonTheme(
        primary_background=QColor("#2962FF"),
        primary_text=QColor("#FFFFFF"),

        secondary_background=QColor("#9C27FF"),
        secondary_text=QColor("#FFFFFF"),

        danger_background=QColor("#E53935"),
        danger_text=QColor("#FFFFFF"),

        hover_overlay=QColor(255, 255, 255, 20),
    ),

    input=InputTheme(
        background=QColor("#07101D"),
        border=QColor("#123C8D"),

        text=QColor("#F3F7FF"),
        placeholder=QColor("#6D84B8"),

        focus_border=QColor("#00E5FF"),
    ),

    console=ConsoleTheme(
        background=QColor("#050B18"),

        input_text=QColor("#00E5FF"),
        output_text=QColor("#EAF2FF"),

        info_text=QColor("#00E5FF"),
        error_text=QColor("#FF5370"),
    ),

    chart=ChartTheme(
        background=QColor("#091224"),

        grid=QColor("#123C8D"),
        axis=QColor("#6D84B8"),

        primary_line=QColor("#00E5FF"),
        secondary_line=QColor("#9C27FF"),
        tertiary_line=QColor("#2962FF"),
    ),

    evalbar=EvalBarTheme(
        white=QColor("#EAF2FF"),
        black=QColor("#0F1628"),

        text=QColor("#FFFFFF"),
    ),

    status=StatusTheme(
        success=QColor("#00E676"),
        warning=QColor("#FFD54F"),
        error=QColor("#FF5370"),
        info=QColor("#00E5FF"),
    ),
)