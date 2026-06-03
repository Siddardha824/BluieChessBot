from dataclasses import dataclass
from PySide6.QtGui import QColor


# ============================================================
# TYPOGRAPHY
# ============================================================

@dataclass(frozen=True)
class TypographyTheme:
    family: str

    tiny: int
    small: int
    normal: int
    large: int
    heading: int
    title: int


# ============================================================
# APPLICATION
# ============================================================

@dataclass(frozen=True)
class WindowTheme:
    background: QColor
    surface: QColor
    border: QColor

    text: QColor
    text_muted: QColor
    text_disabled: QColor

    accent: QColor


@dataclass(frozen=True)
class NavigationTheme:
    background: QColor

    item_text: QColor
    item_text_selected: QColor

    item_hover: QColor
    item_selected: QColor

    icon: QColor
    icon_selected: QColor


# ============================================================
# BOARD
# ============================================================

@dataclass(frozen=True)
class BoardTheme:
    light_square: QColor
    dark_square: QColor

    selection: QColor
    legal_move: QColor
    last_move: QColor
    check: QColor

    coordinate_light: QColor
    coordinate_dark: QColor


# ============================================================
# SHARED CONTAINERS
# ============================================================

@dataclass(frozen=True)
class ContainerTheme:
    background: QColor
    border: QColor

    title_text: QColor
    body_text: QColor
    muted_text: QColor


# ============================================================
# INPUTS & BUTTONS
# ============================================================

@dataclass(frozen=True)
class ButtonTheme:
    primary_background: QColor
    primary_text: QColor

    secondary_background: QColor
    secondary_text: QColor

    danger_background: QColor
    danger_text: QColor

    hover_overlay: QColor


@dataclass(frozen=True)
class InputTheme:
    background: QColor
    border: QColor

    text: QColor
    placeholder: QColor

    focus_border: QColor


# ============================================================
# SPECIALIZED WIDGETS
# ============================================================

@dataclass(frozen=True)
class ConsoleTheme:
    background: QColor

    input_text: QColor
    output_text: QColor

    info_text: QColor
    error_text: QColor


@dataclass(frozen=True)
class ChartTheme:
    background: QColor

    grid: QColor
    axis: QColor

    primary_line: QColor
    secondary_line: QColor
    tertiary_line: QColor


@dataclass(frozen=True)
class EvalBarTheme:
    white: QColor
    black: QColor

    text: QColor


# ============================================================
# STATUS COLORS
# ============================================================

@dataclass(frozen=True)
class StatusTheme:
    success: QColor
    warning: QColor
    error: QColor
    info: QColor


# ============================================================
# ACTIVE THEME
# ============================================================

@dataclass(frozen=True)
class ActiveTheme:
    name: str

    typography: TypographyTheme

    window: WindowTheme
    navigation: NavigationTheme

    board: BoardTheme

    container: ContainerTheme

    button: ButtonTheme
    input: InputTheme

    console: ConsoleTheme
    chart: ChartTheme

    evalbar: EvalBarTheme

    status: StatusTheme