import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QLabel,
    QStatusBar, QHeaderView, QGroupBox, QFrame, QDoubleSpinBox,
    QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QColor, QFont, QBrush
from get_odds.get_odds import GetOdds


class FetchWorker(QObject):
    finished = Signal(dict)
    error = Signal(str)
    status = Signal(str)

    def __init__(self, sports):
        super().__init__()
        self.sports = sports

    def run(self):
        try:
            self.status.emit("Fetching odds from API...")
            all_games = GetOdds.get_games(self.sports)

            opportunities_by_sport = {}
            for sport_key, games in all_games.items():
                self.status.emit(f"Analyzing {GetOdds.SPORT_NAMES.get(sport_key, sport_key)}...")
                if games:
                    opportunities = GetOdds.find_arbitrage_opportunities(games)
                    opportunities_by_sport[sport_key] = opportunities
                else:
                    opportunities_by_sport[sport_key] = []

            self.finished.emit(opportunities_by_sport)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    SPORTS = {
        "basketball_nba": "NBA",
        "baseball_mlb": "MLB",
        "americanfootball_nfl": "NFL",
        "icehockey_nhl": "NHL",
    }

    TABLE_HEADERS = [
        "Sport", "Game", "Status", "Time (EST)",
        "Home Team", "Home Odds", "Home Book",
        "Away Team", "Away Odds", "Away Book",
        "Profit %", "Home Stake", "Away Stake", "Guaranteed Profit",
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SangOdds — Arbitrage Finder")
        self.setMinimumSize(1300, 700)
        self._thread = None
        self._worker = None
        self._opportunities = {}
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(14, 14, 14, 14)

        # ── Header ──────────────────────────────────────────────────────────
        header = QLabel("SangOdds")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        root.addWidget(header)

        # ── Control bar ──────────────────────────────────────────────────────
        ctrl_frame = QFrame()
        ctrl_frame.setObjectName("ctrlFrame")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setContentsMargins(14, 10, 14, 10)
        ctrl_layout.setSpacing(16)

        sports_group = QGroupBox("Sports")
        sports_layout = QHBoxLayout(sports_group)
        sports_layout.setSpacing(14)
        self._sport_checks: dict[str, QCheckBox] = {}
        for key, name in self.SPORTS.items():
            cb = QCheckBox(name)
            cb.setChecked(True)
            self._sport_checks[key] = cb
            sports_layout.addWidget(cb)
        ctrl_layout.addWidget(sports_group)

        stake_group = QGroupBox("Total Stake ($)")
        stake_layout = QHBoxLayout(stake_group)
        self._stake_spin = QDoubleSpinBox()
        self._stake_spin.setRange(1, 1_000_000)
        self._stake_spin.setValue(100)
        self._stake_spin.setDecimals(2)
        self._stake_spin.setSingleStep(10)
        self._stake_spin.setMinimumWidth(130)
        stake_layout.addWidget(self._stake_spin)
        ctrl_layout.addWidget(stake_group)

        ctrl_layout.addStretch()

        self._fetch_btn = QPushButton("Fetch Odds")
        self._fetch_btn.setObjectName("fetchBtn")
        self._fetch_btn.setMinimumHeight(42)
        self._fetch_btn.setMinimumWidth(150)
        self._fetch_btn.clicked.connect(self._on_fetch)
        ctrl_layout.addWidget(self._fetch_btn)

        root.addWidget(ctrl_frame)

        # ── Summary ──────────────────────────────────────────────────────────
        self._summary_label = QLabel("Press 'Fetch Odds' to scan for arbitrage opportunities.")
        self._summary_label.setObjectName("summaryLabel")
        root.addWidget(self._summary_label)

        # ── Results table ─────────────────────────────────────────────────────
        self._table = QTableWidget(0, len(self.TABLE_HEADERS))
        self._table.setHorizontalHeaderLabels(self.TABLE_HEADERS)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        hh.setStretchLastSection(True)
        root.addWidget(self._table)

        # ── Status bar ───────────────────────────────────────────────────────
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")

        self._stake_spin.valueChanged.connect(self._refresh_table)

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #141414;
                color: #e5e5e5;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            #header {
                font-size: 28px;
                font-weight: 900;
                color: #ffffff;
                letter-spacing: 6px;
                padding: 10px 0 6px 0;
            }
            #ctrlFrame {
                background-color: #1f1f1f;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
            }
            QGroupBox {
                border: 1px solid #333333;
                border-radius: 5px;
                margin-top: 8px;
                padding: 6px 10px 6px 10px;
                font-weight: bold;
                color: #808080;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: #808080;
            }
            QCheckBox {
                spacing: 7px;
                color: #e5e5e5;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid #555555;
                background-color: #1f1f1f;
            }
            QCheckBox::indicator:checked {
                background-color: #ffffff;
                border-color: #ffffff;
                image: url(none);
            }
            QCheckBox::indicator:hover {
                border-color: #cccccc;
            }
            QDoubleSpinBox {
                background-color: #1f1f1f;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 4px 8px;
                color: #e5e5e5;
            }
            QDoubleSpinBox:focus {
                border-color: #ffffff;
            }
            #fetchBtn {
                background-color: #ffffff;
                color: #141414;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 26px;
                letter-spacing: 1px;
            }
            #fetchBtn:hover  { background-color: #e0e0e0; }
            #fetchBtn:pressed { background-color: #bbbbbb; }
            #fetchBtn:disabled {
                background-color: #2a2a2a;
                color: #555555;
            }
            #summaryLabel {
                color: #808080;
                padding: 2px 4px;
                font-size: 12px;
            }
            QTableWidget {
                background-color: #141414;
                alternate-background-color: #1a1a1a;
                gridline-color: #2a2a2a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #1f1f1f;
                color: #ffffff;
                padding: 8px 6px;
                border: none;
                border-bottom: 2px solid #ffffff;
                font-weight: bold;
                font-size: 12px;
                letter-spacing: 1px;
            }
            QTableWidget::item:selected {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QStatusBar {
                background-color: #0a0a0a;
                color: #555555;
                border-top: 1px solid #1f1f1f;
            }
            QScrollBar:vertical {
                background: #141414;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #333333;
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background: #888888;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar:horizontal {
                background: #141414;
                height: 8px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: #333333;
                border-radius: 4px;
                min-width: 24px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #888888;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0;
            }
        """)

    def _selected_sports(self) -> list[str]:
        return [key for key, cb in self._sport_checks.items() if cb.isChecked()]

    def _on_fetch(self):
        sports = self._selected_sports()
        if not sports:
            self._status_bar.showMessage("Select at least one sport first.")
            return

        self._fetch_btn.setEnabled(False)
        self._fetch_btn.setText("Fetching…")
        self._table.setRowCount(0)
        self._summary_label.setText("Fetching odds, please wait…")
        self._opportunities = {}

        self._thread = QThread()
        self._worker = FetchWorker(sports)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_fetch_done)
        self._worker.error.connect(self._on_fetch_error)
        self._worker.status.connect(self._status_bar.showMessage)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def _on_fetch_done(self, opportunities_by_sport: dict):
        self._opportunities = opportunities_by_sport
        self._fetch_btn.setEnabled(True)
        self._fetch_btn.setText("Fetch Odds")
        self._refresh_table()

    def _on_fetch_error(self, error_msg: str):
        self._fetch_btn.setEnabled(True)
        self._fetch_btn.setText("Fetch Odds")
        self._summary_label.setText(f"Error: {error_msg}")
        self._status_bar.showMessage(f"Error: {error_msg}")

    def _refresh_table(self):
        if not self._opportunities:
            return

        stake = self._stake_spin.value()
        self._table.setRowCount(0)
        total = 0

        for sport_key, opps in self._opportunities.items():
            for opp in opps:
                total += 1
                row = self._table.rowCount()
                self._table.insertRow(row)

                # Recalculate stakes for the custom stake amount
                total_prob = opp["total_implied_probability"]
                home_prob = 1.0 / opp["best_home_odds"]
                away_prob = 1.0 / opp["best_away_odds"]
                home_stake = (home_prob / total_prob) * stake
                away_stake = (away_prob / total_prob) * stake
                profit = min(
                    home_stake * opp["best_home_odds"],
                    away_stake * opp["best_away_odds"]
                ) - stake

                is_live = opp["is_live"]
                status_text = "● LIVE" if is_live else "UPCOMING"

                cells = [
                    opp["sport_name"],
                    opp["game"],
                    status_text,
                    opp["commence_time_est"],
                    opp["home_team"],
                    f"{opp['best_home_odds']:.3f}",
                    opp["home_bookmaker"],
                    opp["away_team"],
                    f"{opp['best_away_odds']:.3f}",
                    opp["away_bookmaker"],
                    f"{opp['profit_margin_percent']:.2f}%",
                    f"${home_stake:.2f}",
                    f"${away_stake:.2f}",
                    f"${profit:.2f}",
                ]

                for col, text in enumerate(cells):
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    if col == 2 and is_live:
                        item.setForeground(QBrush(QColor("#ffffff")))
                        font = item.font(); font.setBold(True); item.setFont(font)

                    if col in (10, 13):  # Profit % and Profit $
                        item.setForeground(QBrush(QColor("#46d369")))
                        font = item.font(); font.setBold(True); item.setFont(font)

                    self._table.setItem(row, col, item)

        word = "opportunity" if total == 1 else "opportunities"
        if total > 0:
            by_sport = "  |  ".join(
                f"{GetOdds.SPORT_NAMES.get(k, k)}: {len(v)}"
                for k, v in self._opportunities.items()
                if v
            )
            self._summary_label.setText(f"Found {total} arbitrage {word}  —  {by_sport}")
        else:
            self._summary_label.setText("No arbitrage opportunities found across selected sports.")

        self._status_bar.showMessage(f"Done. {total} arbitrage {word} found.")


