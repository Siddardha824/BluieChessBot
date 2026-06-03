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


LICHESS_THEME = ActiveTheme(
    name="Lichess",

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
        background=QColor("#0F1724"),
        surface=QColor("#131D2E"),
        border=QColor("#24354A"),

        text=QColor("#E5E7EB"),
        text_muted=QColor("#94A3B8"),
        text_disabled=QColor("#64748B"),

        accent=QColor("#3B82F6"),
    ),

    navigation=NavigationTheme(
        background=QColor("#0B1220"),

        item_text=QColor("#D1D5DB"),
        item_text_selected=QColor("#FFFFFF"),

        item_hover=QColor("#1E293B"),
        item_selected=QColor("#1D4ED8"),

        icon=QColor("#9CA3AF"),
        icon_selected=QColor("#FFFFFF"),
    ),

    board=BoardTheme(
        light_square=QColor("#EFEFED"),
        dark_square=QColor("#7393B3"),

        selection=QColor(247, 247, 105, 130),
        legal_move=QColor(25, 45, 65, 120),
        last_move=QColor(255, 255, 150, 100),
        check=QColor(240, 80, 80, 140),

        coordinate_light=QColor("#7393B3"),
        coordinate_dark=QColor("#EFEFED"),
    ),

    container=ContainerTheme(
        background=QColor("#131D2E"),
        border=QColor("#24354A"),

        title_text=QColor("#F8FAFC"),
        body_text=QColor("#E2E8F0"),
        muted_text=QColor("#94A3B8"),
    ),

    button=ButtonTheme(
        primary_background=QColor("#2563EB"),
        primary_text=QColor("#FFFFFF"),

        secondary_background=QColor("#1E293B"),
        secondary_text=QColor("#E2E8F0"),

        danger_background=QColor("#DC2626"),
        danger_text=QColor("#FFFFFF"),

        hover_overlay=QColor(255, 255, 255, 20),
    ),

    input=InputTheme(
        background=QColor("#0F172A"),
        border=QColor("#334155"),

        text=QColor("#E2E8F0"),
        placeholder=QColor("#64748B"),

        focus_border=QColor("#3B82F6"),
    ),

    console=ConsoleTheme(
        background=QColor("#0A101A"),

        input_text=QColor("#60A5FA"),
        output_text=QColor("#BFDBFE"),

        info_text=QColor("#86EFAC"),
        error_text=QColor("#F87171"),
    ),

    chart=ChartTheme(
        background=QColor("#131D2E"),

        grid=QColor("#24354A"),
        axis=QColor("#64748B"),

        primary_line=QColor("#3B82F6"),
        secondary_line=QColor("#22C55E"),
        tertiary_line=QColor("#F59E0B"),
    ),

    evalbar=EvalBarTheme(
        white=QColor("#EFEFED"),
        black=QColor("#313131"),

        text=QColor("#FFFFFF"),
    ),

    status=StatusTheme(
        success=QColor("#22C55E"),
        warning=QColor("#F59E0B"),
        error=QColor("#EF4444"),
        info=QColor("#3B82F6"),
    ),
)